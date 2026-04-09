from flask import render_template, request, jsonify
from app.blockly import bp
from app.db import execute_query

@bp.route("/")
def editor():
    return render_template("blockly.html")

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
