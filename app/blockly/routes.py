import os
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from flask import Response, jsonify, render_template, request, session

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

        xml_path = os.path.join(tmpdir, "output.xml")
        output_xml = ""
        if os.path.exists(xml_path):
            with open(xml_path, "r") as f:
                output_xml = f.read()

        result_dict = TestResult.from_process(result, output_xml).to_dict(result.stderr)
        result_dict["output_xml"] = output_xml
        return result_dict


def get_project_name(project_id):
    if not project_id:
        return ""
    result = execute_query("SELECT name FROM testflow WHERE testflow_id = ?", [project_id])
    if result and isinstance(result, list):
        return result[0].get("name", "")
    return ""


def get_testruns(project_id):
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
    data = request.get_json()
    xml = data.get("workspace_xml", "")
    project_id = data.get("project_id")
    _, robot_file = xml_to_robot(xml)
    testrun_id = create_testrun(project_id)
    results = execute_robot_test(robot_file)
    status = "passed" if results["return_code"] == 0 else "failed"
    update_testrun_result(testrun_id, status, results.get("geslaagd", 0), results.get("gefaald", 0), results.get("output_xml", ""))
    return jsonify(results)


@bp.route("/geschiedenis")
def geschiedenis():
    project_id = request.args.get("project_id")
    testruns = get_testruns(project_id) if project_id else []
    project_name = get_project_name(project_id)
    return render_template("testrun_history.html", testruns=testruns, project_name=project_name, project_id=project_id)


@bp.route("/testrun/<int:testrun_id>")
def testrun_detail(testrun_id):
    row = execute_query("""
        SELECT tr.testrun_id, tr.testflow_id, tr.status, tr.started_at, tr.finished_at,
               tf.name AS project_name, rp.passed_count, rp.failed_count, rp.output_xml
        FROM testrun tr
        JOIN testflow tf ON tr.testflow_id = tf.testflow_id
        LEFT JOIN testreport rp ON rp.testrun_id = tr.testrun_id
        WHERE tr.testrun_id = ?
    """, [testrun_id])

    if not row:
        return "Testrun niet gevonden", 404

    run = row[0]
    steps = []

    if run.get("output_xml"):
        try:
            root = ET.fromstring(run["output_xml"])
            for test in root.iter("test"):
                for kw in test:
                    if kw.tag == "kw":
                        name = kw.get("name", "")
                        args = [a.text for a in kw.findall("arg") if a.text]
                        status_el = kw.find("status")
                        status = status_el.get("status", "") if status_el is not None else ""
                        elapsed = float(status_el.get("elapsed", 0)) if status_el is not None else 0
                        msg_el = kw.find("msg")
                        message = msg_el.text if msg_el is not None else ""
                        steps.append({
                            "name": name,
                            "args": args,
                            "status": status,
                            "elapsed": round(elapsed, 3),
                            "message": message,
                        })
        except Exception:
            pass

    return render_template("testrun_detail.html", run=run, steps=steps)


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