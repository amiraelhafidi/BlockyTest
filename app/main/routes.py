from flask import render_template, redirect, url_for, request, jsonify
from app.main import bp
from app.db import execute_query
from app.blockly_editor.load_service import LoadService

@bp.route("/")
def index():
   return render_template("welcome.html")

@bp.route("/about")
def about():
   return render_template("about.html")

@bp.route('/blockly/save', methods=['POST'])
def save():
   data = request.get_json()
   print("SAVE DATA:", data)
   xml = data.get('workspace_xml')
   source = data.get('source', 'manual')
   query = """
   INSERT INTO blockly_project (project_name, workspace_xml)
   VALUES (?, ?)
   """
   project_name = "Autosave project" if source == "autosave" else "Project"
   result = execute_query(query, [project_name, xml])
   print("SAVE RESULT:", result)
   message = "Automatisch opgeslagen" if source == "autosave" else "Opgeslagen in database"
   return jsonify({
       "message": message
   })

@bp.route("/blockly/load", methods=["GET"])
def load():
   loader = LoadService()
   result = loader.load_latest()
   return jsonify(result)
