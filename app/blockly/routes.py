from flask import render_template, request, jsonify
from app.blockly import bp
from app.db import execute_query

@bp.route("/")
def editor():
    project_id = request.args.get('project_id')
    project_name = ""
    
    if project_id:
        try:
            result = execute_query("SELECT name FROM testflow WHERE testflow_id = ?", [project_id])
            if result and isinstance(result, list) and result:
                project_name = result[0]['name']
        except:
            project_name = ""
    
    return render_template("blockly.html", project_name=project_name)

@bp.route("/save", methods=["POST"])
def save():
    data = request.get_json()
    xml = data.get("workspace_xml")
    query = "INSERT INTO blockly_project (project_name, workspace_xml) VALUES (?, ?)"
    result = execute_query(query, ["Project", xml])
    return jsonify({"message": "Saved"}), 200

@bp.route("/load", methods=["GET"])
def load():
    query = "SELECT workspace_xml FROM blockly_project ORDER BY id DESC LIMIT 1"
    result = execute_query(query)
    return jsonify({"workspace_xml": result[0]["workspace_xml"] if result else ""})
