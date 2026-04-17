from flask import render_template, request, jsonify, Response
from app.blockly import bp, create_testrun, update_testrun_result
from app.db import execute_query
from app.blockly.code_generator import xml_to_robot
from app.db import execute_query
import os
import subprocess
import tempfile


def execute_robot_test(robot_file: str, timeout: int = 60) -> dict:
    """
    Voert een .robot bestand uit met Robot Framework.
    
    Args:
        robot_file (str): inhoud van het .robot bestand
        timeout (int): timeout in seconden (standaard 60)
    
    Returns:
        dict met keys: return_code, geslaagd, gefaald, output
    
    Raises:
        RuntimeError: als Robot Framework niet geïnstalleerd of time-out
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        robot_path = os.path.join(tmpdir, "generated_test.robot")
        with open(robot_path, 'w') as f:
            f.write(robot_file)
        
        try:
            # Voer via 'python -m robot' zodat venv versie gebruikt wordt
            result = subprocess.run(
                ["python", "-m", "robot", "--outputdir", tmpdir, robot_path],
                capture_output=True,
                text=True,
                timeout=timeout
            )
        except FileNotFoundError:
            raise RuntimeError("Robot Framework niet geïnstalleerd (pip install robotframework)")
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Test time-out na {timeout} seconden")
        
        passed = result.stdout.count("| PASS |")
        failed = result.stdout.count("| FAIL |")
        
        # Verwijder temp file paths uit output
        output_lines = result.stdout.split('\n')
        cleaned_output = '\n'.join([
            line for line in output_lines 
            if not any(keyword in line for keyword in ['Output:', 'Log:', 'Report:'])
        ])
        
        return {
            "return_code": result.returncode,
            "geslaagd": passed,
            "gefaald": failed,
            "output": cleaned_output + result.stderr,
        }


# API ROUTES
# Deze routes is nodig om de projectnaam te kunnen tonen in de editor en om de gegenereerde code te kunnen downloaden als .robot bestand.
@bp.route("/")
def editor():
    """Laadt de Blockly editor pagina"""
    project_id = request.args.get("project_id")
    project_name = ""

    if project_id:
        result = execute_query("SELECT name FROM testflow WHERE testflow_id = ?", [project_id])
        if result and isinstance(result, list):
            project_name = result[0].get("name", "")

    return render_template("blockly.html", project_name=project_name)


@bp.route("/generate", methods=["POST"])
def generate():
    """Genereert Robot Framework code preview uit Blockly XML"""
    data = request.get_json()
    xml = data.get("workspace_xml", "")
    
    if not xml.strip():
        return jsonify({"code": "", "robot_bestand": ""})
    
    try:
        keywords_code, robot_file = xml_to_robot(xml)
        return jsonify({"code": keywords_code, "robot_bestand": robot_file})
    except ValueError as e:
        return jsonify({"fout": str(e)}), 400


@bp.route("/download", methods=["POST"])
def download():
    """Downloadt .robot file als attachment"""
    data = request.get_json()
    xml = data.get("workspace_xml", "")
    project_name = data.get("project_name", "test").replace(" ", "_").lower()
    
    if not xml.strip():
        return jsonify({"fout": "Geen XML"}), 400
    
    try:
        _, robot_file = xml_to_robot(xml)
    except ValueError as e:
        return jsonify({"fout": str(e)}), 400
    
    return Response(
        robot_file,
        mimetype="text/plain",
        headers={"Content-Disposition": f"attachment; filename={project_name}.robot"}
    )


@bp.route("/run", methods=["POST"])
def run():
    """Voert test uit en slaat resultaten automatisch op in database
    
    Verwacht JSON POST data met workspace_xml.
    Maakt automatisch een testrun aan, voert test uit en slaat resultaten op.
    
    JSON body:
        workspace_xml (str): Blockly XML van de test
    
    Returns:
        dict: Test resultaten (return_code, geslaagd, gefaald, output)
    """
    data = request.get_json()
    xml = data.get("workspace_xml", "")
    
    if not xml.strip():
        return jsonify({"fout": "Geen blokken om uit te voeren"}), 400
    
    try:
        _, robot_file = xml_to_robot(xml)
        if not robot_file:
            return jsonify({"fout": "Geen blokken om uit te voeren"}), 400
    except ValueError as e:
        return jsonify({"fout": str(e)}), 400
    
    # Create testrun entry
    testrun_id = create_testrun()
    
    try:
        results = execute_robot_test(robot_file)
        
        # Update testrun with results
        passed = results.get("geslaagd", 0)
        failed = results.get("gefaald", 0)
        status = "passed" if results["return_code"] == 0 else "failed"
        update_testrun_result(testrun_id, status, passed, failed)
        
        return jsonify(results)
    except RuntimeError as e:
        # Update testrun with error status
        update_testrun_result(testrun_id, "error", 0, 0)
        return jsonify({"fout": str(e)}), 500


@bp.route("/geschiedenis")
def geschiedenis():
    """Laadt de test geschiedenis pagina met testruns van het huidige project"""
    try:
        project_id = request.args.get("project_id")
        project_name = ""
        
        if project_id:
            result = execute_query("SELECT name FROM testflow WHERE testflow_id = ?", [project_id])
            if result and isinstance(result, list) and len(result) > 0:
                project_name = result[0].get("name", "")
        
        if project_id:
            query = """SELECT 
                        tr.testrun_id,
                        tf.name as testflow_name,
                        tr.status,
                        tr.started_at
                       FROM testrun tr
                       LEFT JOIN testflow tf ON tr.testflow_id = tf.testflow_id
                       WHERE tr.testflow_id = ?
                       ORDER BY tr.started_at DESC
                       LIMIT 100"""
            testruns = execute_query(query, [project_id])
        else:
            query = """SELECT 
                        tr.testrun_id,
                        tf.name as testflow_name,
                        tr.status,
                        tr.started_at
                       FROM testrun tr
                       LEFT JOIN testflow tf ON tr.testflow_id = tf.testflow_id
                       ORDER BY tr.started_at DESC
                       LIMIT 100"""
            testruns = execute_query(query)
        
        return render_template("testrun_history.html", testruns=testruns, project_name=project_name)
    except Exception as e:
        return render_template("testrun_history.html", testruns=[], project_name="", error=str(e))


@bp.route("/save", methods=["POST"])
def save():
    """Slaat de Blockly workspace op in database"""
    try:
        data = request.get_json()
        workspace_xml = data.get("workspace_xml", "")
        project_name = data.get("project_name", "Untitled Project")
        
        # Insert of update blockly_project
        query = """INSERT INTO blockly_project (project_name, workspace_xml) 
                   VALUES (?, ?) 
                   ON DUPLICATE KEY UPDATE workspace_xml = VALUES(workspace_xml)"""
        execute_query(query, (project_name, workspace_xml))
        
        return jsonify({"success": True, "message": "Workspace opgeslagen"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@bp.route("/load", methods=["GET"])
def load():
    """Laadt de laatst opgeslagen Blockly workspace"""
    try:
        query = "SELECT workspace_xml FROM blockly_project ORDER BY id DESC LIMIT 1"
        result = execute_query(query)
        
        if result and len(result) > 0:
            return jsonify({"workspace_xml": result[0].get("workspace_xml", "")})
        else:
            return jsonify({"workspace_xml": ""})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
