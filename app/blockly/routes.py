"""Routes en helpfuncties voor Blockly vertaling, runs en geschiedenis."""

import os
import subprocess
import tempfile

from flask import Response, jsonify, render_template, request

from app.blockly import bp, create_testrun, update_testrun_result
from app.blockly.code_generator import xml_to_robot
from app.blockly.test_result import TestResult
from app.db import execute_query


def execute_robot_test(robot_file: str, timeout: int = 60) -> dict:
    """
    Voer Robot Framework test uit met gegenereerde .robot file.

    Schrijft de code naar een temp folder en voert robot command uit.
    Returned alle output en telt geslaagde/gefaalde tests.

    Args:
        robot_file (str): Inhoud van het .robot bestand
        timeout (int): Maximale wachttijd in seconden

    Returns:
        dict: Test resultaat met return_code, tellers en output

    Raises:
        RuntimeError: Als Robot niet geïnstalleerd is of timeout
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        robot_path = os.path.join(tmpdir, "generated_test.robot")

        # Schrijf .robot file naar temp folder
        with open(robot_path, "w") as file:
            file.write(robot_file)

        try:
            # Voer Robot Framework uit
            result = subprocess.run(
                ["python", "-m", "robot", "--outputdir", tmpdir, robot_path],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except FileNotFoundError:
            raise RuntimeError("Robot Framework niet geïnstalleerd (pip install robotframework)")
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Test time-out na {timeout} seconden")

        # Parse output naar TestResult object
        test_result = TestResult.from_process(result)
        return test_result.to_dict(result.stderr)


def get_project_name(project_id: str | None) -> str:
    """
    Haal projectnaam op uit database.

    Args:
        project_id (str | None): ID van het project

    Returns:
        str: Projectnaam of lege string als niet gevonden
    """
    if not project_id:
        return ""

    # Query de testflow tabel naar projectnaam
    result = execute_query("SELECT name FROM testflow WHERE testflow_id = ?", [project_id])
    if result and isinstance(result, list):
        return result[0].get("name", "")

    return ""


def get_robot_file(xml: str) -> str:
    """
    Zet Blockly XML om naar compleet .robot bestand.

    Args:
        xml (str): Blockly XML van workspace

    Returns:
        str: Volledige Robot Framework bestand inhoud
    """
    # Haal robot_file uit xml_to_robot (eerste waarde is preview)
    _, robot_file = xml_to_robot(xml)
    return robot_file


def get_testruns(project_id: str | None) -> list:
    """
    Haal testruns op uit database.

    Filtert op project als project_id gegeven, anders alle testruns.

    Args:
        project_id (str | None): Project ID om op te filteren

    Returns:
        list: Testruns met testrun_id, status en started_at
    """
    base_query = """SELECT
                        tr.testrun_id,
                        tr.status,
                        tr.started_at
                    FROM testrun tr"""

    # Filter op project_id als die gegeven is
    if project_id:
        query = base_query + """
                    WHERE tr.testflow_id = ?
                    ORDER BY tr.started_at DESC
                    LIMIT 100"""
        return execute_query(query, [project_id])

    # Haal alle testruns op
    query = base_query + """
                ORDER BY tr.started_at DESC
                LIMIT 100"""
    return execute_query(query)


@bp.route("/")
def editor():
    """
    Laad en toon de Blockly editor pagina.

    Returns:
        Response: HTML pagina met editor
    """
    # Haal project_id uit URL parameters
    project_id = request.args.get("project_id")
    # Render editor met projectnaam in titel
    return render_template("blockly.html", project_name=get_project_name(project_id))


@bp.route("/generate", methods=["POST"])
def generate():
    """
    Genereer Robot code uit Blockly XML.

    Returned preview keywords en volledig .robot bestand.

    Returns:
        Response: JSON met code en robot_bestand of fout
    """
    data = request.get_json()
    xml = data.get("workspace_xml", "")

    # Return lege waarden als geen XML
    if not xml.strip():
        return jsonify({"code": "", "robot_bestand": ""})

    try:
        # Vertaal XML naar Robot code
        keywords_code, robot_file = xml_to_robot(xml)
        return jsonify({"code": keywords_code, "robot_bestand": robot_file})
    except ValueError as error:
        return jsonify({"fout": str(error)}), 400


@bp.route("/download", methods=["POST"])
def download():
    """
    Download gegenereerde .robot file.

    Returns:
        Response: Download bestand of JSON foutmelding
    """
    data = request.get_json()
    xml = data.get("workspace_xml", "")
    # Maak bestandsnaam: spaties weg, lowercase
    project_name = data.get("project_name", "test").replace(" ", "_").lower()

    # Valideer dat er XML is
    if not xml.strip():
        return jsonify({"fout": "Geen XML"}), 400

    try:
        # Genereer .robot file
        robot_file = get_robot_file(xml)
    except ValueError as error:
        return jsonify({"fout": str(error)}), 400

    # Return file voor download
    return Response(
        robot_file,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename={project_name}.robot"},
    )


@bp.route("/run", methods=["POST"])
def run():
    """
    Voer gegenereerde test uit en sla resultaat op.

    Stap 1: Valideer XML
    Stap 2: Maak testrun record in DB
    Stap 3: Voer Robot test uit
    Stap 4: Sla resultaten op in DB
    Stap 5: Return resultaten naar frontend

    Returns:
        Response: JSON met testresultaat of fout
    """
    data = request.get_json()
    xml = data.get("workspace_xml", "")

    # Valideer dat er blokken zijn
    if not xml.strip():
        return jsonify({"fout": "Geen blokken om uit te voeren"}), 400

    # Genereer .robot file
    try:
        robot_file = get_robot_file(xml)
        if not robot_file:
            return jsonify({"fout": "Geen blokken om uit te voeren"}), 400
    except ValueError as error:
        return jsonify({"fout": str(error)}), 400

    # Maak testrun record (status = "running")
    testrun_id = create_testrun()

    try:
        # Voer de test uit
        results = execute_robot_test(robot_file)
        passed = results.get("geslaagd", 0)
        failed = results.get("gefaald", 0)
        # Bepaal status op basis van return_code
        status = "passed" if results["return_code"] == 0 else "failed"
        # Sla resultaten op in DB
        update_testrun_result(testrun_id, status, passed, failed)
        # Return resultaten naar frontend
        return jsonify(results)
    except RuntimeError as error:
        # Update DB met fout status
        update_testrun_result(testrun_id, "error", 0, 0)
        return jsonify({"fout": str(error)}), 500


@bp.route("/geschiedenis")
def geschiedenis():
    """
    Toon pagina met testrun geschiedenis.

    Haalt alle testruns op uit DB en toont ze in tabel.

    Returns:
        Response: HTML pagina met testruns
    """
    try:
        # Haal project_id uit URL (optioneel filteren)
        project_id = request.args.get("project_id")
        # Query testruns met of zonder filter
        testruns = get_testruns(project_id)
        return render_template("testrun_history.html", testruns=testruns)
    except Exception as error:
        # Bij fout: toon lege geschiedenis met foutmelding
        return render_template("testrun_history.html", testruns=[], error=str(error))


@bp.route("/save", methods=["POST"])
def save():
    """
    Sla workspace XML op in database.

    Returns:
        Response: JSON met succes of fout
    """
    try:
        data = request.get_json()
        workspace_xml = data.get("workspace_xml", "")
        project_name = data.get("project_name", "Untitled Project")

        # Insert of update workspace
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
    Laad laatst opgeslagen workspace uit database.

    Returns:
        Response: JSON met workspace XML of fout
    """
    try:
        # Haal meest recente workspace op
        query = "SELECT workspace_xml FROM blockly_project ORDER BY id DESC LIMIT 1"
        result = execute_query(query)
        # Extraheer XML of lege string
        workspace_xml = result[0].get("workspace_xml", "") if result else ""
        return jsonify({"workspace_xml": workspace_xml})
    except Exception as error:
        return jsonify({"error": str(error)}), 500
