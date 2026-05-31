import os
import shutil
import subprocess
import tempfile

from flask import Response, jsonify, render_template, request, send_from_directory, current_app

from app.blockly import bp, create_testrun, update_testrun_result
from app.blockly.code_generator import RobotCodeGenerator
from app.blockly.test_result import TestResult
from app.db import execute_query


def execute_robot_test(robot_file, testrun_id, timeout=60):
    """Draai een Robot Framework-test en geef het resultaat terug.

    Schrijft de testcode naar een tijdelijk bestand, draait die met Robot
    Framework, bewaart de screenshots en leest het rapport en de log uit.

    Args:
        robot_file (str): De inhoud van het .robot-testbestand.
        testrun_id (int): Id van de testrun, gebruikt om de screenshots op te slaan.
        timeout (int): Maximale tijd in seconden dat de test mag draaien.

    Returns:
        dict: Het testresultaat met de uitvoer, het rapport en de log.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Schrijf de gegenereerde test naar een tijdelijk bestand.
        robot_path = os.path.join(tmpdir, "generated_test.robot")

        with open(robot_path, "w", encoding="utf-8") as f:
            f.write(robot_file)

        # Draai de test met Robot Framework.
        result = subprocess.run(
            ["python", "-m", "robot", "--outputdir", tmpdir, robot_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        # Lees het rapport en de log die Robot heeft gemaakt (als ze bestaan).
        report_path = os.path.join(tmpdir, "report.html")
        log_path = os.path.join(tmpdir, "log.html")

        report_html = open(report_path, encoding="utf-8").read() if os.path.exists(report_path) else ""
        log_html = open(log_path, encoding="utf-8").read() if os.path.exists(log_path) else ""

        screenshots_dir = os.path.join(
            "app",
            "static",
            "testrun_screenshots",
            str(testrun_id)
        )
        os.makedirs(screenshots_dir, exist_ok=True)

        for filename in os.listdir(tmpdir):
            if filename.lower().endswith(".png"):
                shutil.copy(
                    os.path.join(tmpdir, filename),
                    os.path.join(screenshots_dir, filename)
        )

        screenshot_url = f"/blockly/testrun/{testrun_id}/{filename}"
        log_html = log_html.replace(filename, screenshot_url)
        report_html = report_html.replace(filename, screenshot_url)

        result_dict = TestResult(result).to_dict()
        result_dict["report_html"] = report_html
        result_dict["log_html"] = log_html

        return result_dict


def get_project_name(project_id):
    """Zoek de naam van een project op.

    Args:
        project_id (int): Id van het project (testflow).

    Returns:
        str: De projectnaam, of een lege tekst als het project niet bestaat.
    """
    if not project_id:
        return ""
    result = execute_query("SELECT name FROM testflow WHERE testflow_id = ?", [project_id])
    return result[0].get("name", "") if result else ""


def get_testruns(project_id):
    """Haal de testruns van een project op, de nieuwste eerst.

    Args:
        project_id (int): Id van het project (testflow).

    Returns:
        list: De laatste 100 testruns van dit project.
    """
    return execute_query("""
        SELECT tr.testrun_id, tr.status, tr.started_at, tf.name AS project_name
        FROM testrun tr
        JOIN testflow tf ON tr.testflow_id = tf.testflow_id
        WHERE tr.testflow_id = ?
        ORDER BY tr.started_at DESC
        LIMIT 100
    """, [project_id])


@bp.route("/")
def editor():
    """Toon de Blockly-editor waarin de gebruiker zijn test bouwt.

    Returns:
        str: De gerenderde HTML-pagina van de editor.
    """
    project_id = request.args.get("project_id")
    return render_template("blockly.html", project_name=get_project_name(project_id), project_id=project_id)


@bp.route("/run", methods=["POST"])
def run():
    """Genereer de testcode uit de blokken, draai de test en sla het resultaat op.

    Returns:
        Response: Het testresultaat als JSON voor de browser.
    """
    data = request.get_json()
    # Zet de blokken uit de editor om in een Robot-testbestand.
    robot_file = RobotCodeGenerator(data.get("workspace_xml", "")).to_robot()
    # Maak een testrun aan, draai de test en bepaal of die geslaagd is.
    testrun_id = create_testrun(data.get("project_id"))
    results = execute_robot_test(robot_file, testrun_id)
    status = "passed" if results["return_code"] == 0 else "failed"
    # Sla het eindresultaat met rapport en log op.
    update_testrun_result(
        testrun_id, status,
        results.get("report_html", ""),
        results.get("log_html", "")
    )
    return jsonify(results)


@bp.route("/geschiedenis")
def geschiedenis():
    """Toon de lijst met eerdere testruns van een project.

    Returns:
        str: De gerenderde HTML-pagina met de testgeschiedenis.
    """
    project_id = request.args.get("project_id")
    return render_template(
        "testrun_history.html",
        testruns=get_testruns(project_id) if project_id else [],
        project_name=get_project_name(project_id),
        project_id=project_id,
    )


@bp.route("/testrun/<int:testrun_id>")
def testrun_detail(testrun_id):
    """Toon de detailpagina van één testrun.

    Args:
        testrun_id (int): Id van de testrun die getoond moet worden.

    Returns:
        str: De gerenderde detailpagina, of een 404 als de testrun niet bestaat.
    """
    row = execute_query("""
        SELECT tr.testrun_id, tr.testflow_id, tr.status, tr.started_at, tr.finished_at,
               tf.name AS project_name,
               rp.report_html IS NOT NULL AND rp.report_html != '' AS has_report,
               rp.log_html IS NOT NULL AND rp.log_html != '' AS has_log
        FROM testrun tr
        JOIN testflow tf ON tr.testflow_id = tf.testflow_id
        LEFT JOIN testreport rp ON rp.testrun_id = tr.testrun_id
        WHERE tr.testrun_id = ?
    """, [testrun_id])

    if not row:
        return "Testrun niet gevonden", 404

    run = row[0]
    return render_template("testrun_detail.html", run=run)


@bp.route("/testrun/<int:testrun_id>/report")
def testrun_report(testrun_id):
    """Geef het opgeslagen HTML-rapport van een testrun terug.

    Args:
        testrun_id (int): Id van de testrun.

    Returns:
        Response: Het rapport als HTML, of een 404 als er geen rapport is.
    """
    row = execute_query(
        "SELECT report_html FROM testreport WHERE testrun_id = ?", [testrun_id]
    )
    if not row or not row[0].get("report_html"):
        return "Rapport niet beschikbaar", 404
    return Response(row[0]["report_html"], mimetype="text/html")

@bp.route("/testrun/<int:testrun_id>/log")
def testrun_log(testrun_id):
    """Geef de opgeslagen HTML-log van een testrun terug.

    Args:
        testrun_id (int): Id van de testrun.

    Returns:
        Response: De log als HTML, of een 404 als er geen log is.
    """
    row = execute_query(
        "SELECT log_html FROM testreport WHERE testrun_id = ?", [testrun_id]
    )
    if not row or not row[0].get("log_html"):
        return "Log niet beschikbaar", 404

    return Response(row[0]["log_html"], mimetype="text/html")

@bp.route("/testrun/<int:testrun_id>/<path:filename>")
def testrun_file(testrun_id, filename):
    folder = os.path.join(
        current_app.root_path,
        "static",
        "testrun_screenshots",
        str(testrun_id)
    )

    return send_from_directory(folder, filename)


@bp.route("/save", methods=["POST"])
def save():
    """Sla de blokken (workspace) van een project op.

    Bestaat het project al, dan worden de blokken bijgewerkt.

    Returns:
        Response: Een JSON-bericht dat het opslaan gelukt is.
    """
    data = request.get_json()
    execute_query(
        "INSERT INTO blockly_project (project_name, workspace_xml) VALUES (?, ?) ON DUPLICATE KEY UPDATE workspace_xml = VALUES(workspace_xml)",
        (data.get("project_name", "Untitled Project"), data.get("workspace_xml", ""))
    )
    return jsonify({"success": True, "message": "Workspace opgeslagen"})


@bp.route("/load", methods=["GET"])
def load():
    """Laad de laatst opgeslagen blokken (workspace) in.

    Returns:
        Response: De opgeslagen blokken als JSON, of leeg als er niets is.
    """
    result = execute_query("SELECT workspace_xml FROM blockly_project ORDER BY id DESC LIMIT 1")
    return jsonify({"workspace_xml": result[0].get("workspace_xml", "") if result else ""})