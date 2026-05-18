import os
import subprocess
import tempfile

from flask import Response, jsonify, render_template, request

from app.blockly import bp, create_testrun, update_testrun_result
from app.blockly.code_generator import xml_to_robot
from app.blockly.test_result import TestResult
from app.db import execute_query


def execute_robot_test(robot_file, timeout=60):
    with tempfile.TemporaryDirectory() as tmpdir:
        robot_path = os.path.join(tmpdir, "generated_test.robot")

        with open(robot_path, "w") as file:
            file.write(robot_file)

        result = subprocess.run(
            ["python", "-m", "robot", "--outputdir", tmpdir, robot_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return TestResult.from_process(result).to_dict(result.stderr)


def get_project_name(project_id):
    if not project_id:
        return ""
    result = execute_query("SELECT name FROM testflow WHERE testflow_id = ?", [project_id])
    if result and isinstance(result, list):
        return result[0].get("name", "")
    return ""


def get_testruns():
    return execute_query("""
        SELECT testrun_id, status, started_at
        FROM testrun
        ORDER BY started_at DESC
        LIMIT 100
    """)


@bp.route("/")
def editor():
    project_id = request.args.get("project_id")
    return render_template("blockly.html", project_name=get_project_name(project_id))


@bp.route("/generate", methods=["POST"])
def generate():
    xml = request.get_json().get("workspace_xml", "")
    if not xml.strip():
        return jsonify({"code": "", "robot_bestand": ""})
    keywords_code, robot_file = xml_to_robot(xml)
    return jsonify({"code": keywords_code, "robot_bestand": robot_file})


@bp.route("/download", methods=["POST"])
def download():
    data = request.get_json()
    xml = data.get("workspace_xml", "")
    project_name = data.get("project_name", "test").replace(" ", "_").lower()
    _, robot_file = xml_to_robot(xml)
    return Response(
        robot_file,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename={project_name}.robot"},
    )


@bp.route("/run", methods=["POST"])
def run():
    xml = request.get_json().get("workspace_xml", "")
    _, robot_file = xml_to_robot(xml)
    testrun_id = create_testrun()
    results = execute_robot_test(robot_file)
    status = "passed" if results["return_code"] == 0 else "failed"
    update_testrun_result(testrun_id, status, results.get("geslaagd", 0), results.get("gefaald", 0))
    return jsonify(results)


@bp.route("/geschiedenis")
def geschiedenis():
    return render_template("testrun_history.html", testruns=get_testruns())


@bp.route("/save", methods=["POST"])
def save():
    data = request.get_json()
    execute_query(
        "INSERT INTO blockly_project (project_name, workspace_xml) VALUES (?, ?) ON DUPLICATE KEY UPDATE workspace_xml = VALUES(workspace_xml)",
        (data.get("project_name", "Untitled Project"), data.get("workspace_xml", ""))
    )
    return jsonify({"success": True, "message": "Workspace opgeslagen"})


@bp.route("/load", methods=["GET"])
def load():
    result = execute_query("SELECT workspace_xml FROM blockly_project ORDER BY id DESC LIMIT 1")
    return jsonify({"workspace_xml": result[0].get("workspace_xml", "") if result else ""})