from flask import render_template

from app.main import bp
from flask import request, jsonify
from app.db import execute_query


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/over-mij")
def about_me():
    return render_template("zelfportret.html")

@bp.route("/blockly")
def blockly():
    return render_template("blockly.html")


@bp.route("/blockly/save", methods=["POST"])
def save_blockly():
    data = request.get_json()
    xml = data.get("workspace_xml")

    query = """
    INSERT INTO blockly_project (project_name, workspace_xml)
    VALUES (?, ?)
    """

    result = execute_query(query, ["Mijn project", xml])

    if isinstance(result, dict) and "reason" in result:
        return jsonify({
            "message": "Opslaan mislukt",
            "result": result
        }), 400

    return jsonify({
        "message": "Opgeslagen in database!"
    })

@bp.route("/blockly/load", methods=["GET"])
def load_blockly():
    query = """
    SELECT workspace_xml
    FROM blockly_project
    ORDER BY id DESC
    LIMIT 1
    """

    result = execute_query(query)

    if not result:
        return jsonify({"workspace_xml": ""})

    return jsonify({
        "workspace_xml": result[0]["workspace_xml"]
    })


