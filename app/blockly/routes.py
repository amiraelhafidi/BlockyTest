"""Routes en helpers voor Blocky codevertaling, runs en geschiedenis."""

import os
import subprocess
import tempfile

from flask import Response, jsonify, render_template, request

from app.blockly import bp, create_testrun, update_testrun_result
from app.blockly.test_result import TestResult
from app.blockly.code_generator import xml_to_robot
from app.db import execute_query


def execute_robot_test(robot_file: str, timeout: int = 60) -> dict:
    """
    Voert een Robot Framework test uit.

    Args:
        robot_file (str): Inhoud van het .robot bestand.
        timeout (int): Maximale wachttijd in seconden.

    Returns:
        dict: Resultaat van de testrun met status en output.

    Raises:
        RuntimeError: Als Robot Framework niet beschikbaar is of de test te lang duurt.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        robot_path = os.path.join(tmpdir, "generated_test.robot")

        # Schrijf eerst het tijdelijke Robot bestand weg.
        with open(robot_path, "w") as file:
            file.write(robot_file)

        try:
            # Gebruik de Python omgeving van het project.
            result = subprocess.run(
                ["python", "-m", "robot", "--outputdir", tmpdir, robot_path],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except FileNotFoundError:
            raise RuntimeError("Robot Framework niet geÃ¯nstalleerd (pip install robotframework)")
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Test time-out na {timeout} seconden")

        # Laat de result class de output en aantallen opbouwen.
        test_result = TestResult.from_process(result)
        return test_result.to_dict(result.stderr)


def get_project_name(project_id: str | None) -> str:
    """
    Haalt de naam van een project op.

    Args:
        project_id (str | None): Id van het project.

    Returns:
        str: De projectnaam of een lege string.
    """
    if not project_id:
        return ""

    result = execute_query("SELECT name FROM testflow WHERE testflow_id = ?", [project_id])
    if result and isinstance(result, list):
        return result[0].get("name", "")

    return ""


def get_robot_file(xml: str) -> str:
    """
    Zet Blocky XML om naar een volledig Robot bestand.

    Args:
        xml (str): Blocky XML.

    Returns:
        str: Inhoud van het Robot bestand.
    """
    _, robot_file = xml_to_robot(xml)
    return robot_file


def get_testruns(project_id: str | None) -> list:
    """
    Haalt testruns op voor de geschiedenis.

    Args:
        project_id (str | None): Id van het project om op te filteren.

    Returns:
        list: Lijst met testruns.
    """
    base_query = """SELECT
                        tr.testrun_id,
                        tr.status,
                        tr.started_at
                    FROM testrun tr"""

    if project_id:
        query = base_query + """
                    WHERE tr.testflow_id = ?
                    ORDER BY tr.started_at DESC
                    LIMIT 100"""
        return execute_query(query, [project_id])

    query = base_query + """
                ORDER BY tr.started_at DESC
                LIMIT 100"""
    return execute_query(query)


@bp.route("/")
def editor():
    """
    Laadt de Blockly editor pagina.

    Returns:
        Response: HTML pagina van de editor.
    """
    project_id = request.args.get("project_id")
    return render_template("blockly.html", project_name=get_project_name(project_id))


@bp.route("/generate", methods=["POST"])
def generate():
    """
    Genereert preview code uit Blocky XML.

    Returns:
        Response: JSON met preview code of een foutmelding.
    """
    data = request.get_json()
    xml = data.get("workspace_xml", "")

    if not xml.strip():
        return jsonify({"code": "", "robot_bestand": ""})

    try:
        keywords_code, robot_file = xml_to_robot(xml)
        return jsonify({"code": keywords_code, "robot_bestand": robot_file})
    except ValueError as error:
        return jsonify({"fout": str(error)}), 400


@bp.route("/download", methods=["POST"])
def download():
    """
    Maakt een downloadbaar Robot bestand.

    Returns:
        Response: Download of JSON foutmelding.
    """
    data = request.get_json()
    xml = data.get("workspace_xml", "")
    project_name = data.get("project_name", "test").replace(" ", "_").lower()

    if not xml.strip():
        return jsonify({"fout": "Geen XML"}), 400

    try:
        robot_file = get_robot_file(xml)
    except ValueError as error:
        return jsonify({"fout": str(error)}), 400

    return Response(
        robot_file,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename={project_name}.robot"},
    )


@bp.route("/run", methods=["POST"])
def run():
    """
    Voert een test uit en slaat het resultaat op.

    Returns:
        Response: JSON met testresultaat of foutmelding.
    """
    data = request.get_json()
    xml = data.get("workspace_xml", "")

    if not xml.strip():
        return jsonify({"fout": "Geen blokken om uit te voeren"}), 400

    try:
        robot_file = get_robot_file(xml)
        if not robot_file:
            return jsonify({"fout": "Geen blokken om uit te voeren"}), 400
    except ValueError as error:
        return jsonify({"fout": str(error)}), 400

    # Maak eerst een testrun record aan.
    testrun_id = create_testrun()

    try:
        results = execute_robot_test(robot_file)

        # Werk daarna status en aantallen bij.
        passed = results.get("geslaagd", 0)
        failed = results.get("gefaald", 0)
        status = "passed" if results["return_code"] == 0 else "failed"
        update_testrun_result(testrun_id, status, passed, failed)

        return jsonify(results)
    except RuntimeError as error:
        # Sla ook fouten op in de geschiedenis.
        update_testrun_result(testrun_id, "error", 0, 0)
        return jsonify({"fout": str(error)}), 500


@bp.route("/geschiedenis")
def geschiedenis():
    """
    Laadt de pagina met testrun geschiedenis.

    Returns:
        Response: HTML pagina met geschiedenis.
    """
    try:
        project_id = request.args.get("project_id")
        testruns = get_testruns(project_id)
        return render_template("testrun_history.html", testruns=testruns)
    except Exception as error:
        return render_template("testrun_history.html", testruns=[], error=str(error))


@bp.route("/save", methods=["POST"])
def save():
    """
    Slaat de Blockly workspace op in de database.

    Returns:
        Response: JSON met succes of foutmelding.
    """
    try:
        data = request.get_json()
        workspace_xml = data.get("workspace_xml", "")
        project_name = data.get("project_name", "Untitled Project")

        query = """INSERT INTO blockly_project (project_name, workspace_xml)
                   VALUES (?, ?)
                   ON DUPLICATE KEY UPDATE workspace_xml = VALUES(workspace_xml)"""
        execute_query(query, (project_name, workspace_xml))

        return jsonify({"success": True, "message": "Workspace opgeslagen"})
    except Exception as error:
        return jsonify({"success": False, "error": str(error)}), 500


@bp.route("/load", methods=["GET"])
def load():
    """
    Laadt de laatst opgeslagen Blockly workspace.

    Returns:
        Response: JSON met workspace XML of foutmelding.
    """
    try:
        query = "SELECT workspace_xml FROM blockly_project ORDER BY id DESC LIMIT 1"
        result = execute_query(query)
        workspace_xml = result[0].get("workspace_xml", "") if result else ""
        return jsonify({"workspace_xml": workspace_xml})
    except Exception as error:
        return jsonify({"error": str(error)}), 500
