from flask import render_template, redirect, url_for, request, jsonify
from app.main import bp
from app.db import execute_query

@bp.route("/")
def index():
   return redirect(url_for("blockly.editor"))

@bp.route("/about")
def about():
   return render_template("about.html")

@bp.route('/blockly/save', methods=['POST'])
def save():
   data = request.get_json()
   xml = data.get('workspace_xml')
   source = data.get('source', 'manual')
   query = """
   INSERT INTO blockly_project (project_name, workspace_xml)
   VALUES (?, ?)
   """
   project_name = "Autosave project" if source == "autosave" else "Project"
   result = execute_query(query, [project_name, xml])
   if isinstance(result, dict) and "reason" in result:
       return jsonify({
           "message": "Opslaan mislukt",
           "result": result
       }), 400
   message = "Automatisch opgeslagen" if source == "autosave" else "Opgeslagen in database"
   return jsonify({
       "message": message
   })
