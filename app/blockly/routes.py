from flask import render_template, request, jsonify, Response
from app.blockly import bp
from app.blockly.code_generator import xml_to_robot
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
            result = subprocess.run(
                ["robot", "--outputdir", tmpdir, robot_path],
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
        
        return {
            "return_code": result.returncode,
            "geslaagd": passed,
            "gefaald": failed,
            "output": result.stdout + result.stderr,
        }


# API ROUTES

@bp.route("/")
def editor():
    """Laadt de Blockly editor pagina"""
    return render_template("blockly.html")


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
    """Voert test uit en retourneert resultaten"""
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
    
    try:
        results = execute_robot_test(robot_file)
        return jsonify(results)
    except RuntimeError as e:
        return jsonify({"fout": str(e)}), 500
