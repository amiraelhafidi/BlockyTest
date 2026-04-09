from flask import render_template, request, redirect, url_for
from app.db import execute_query
from app.projects import bp

@bp.route('/')
def overview():
    query = "SELECT * FROM testflow ORDER BY created_at DESC"
    result = execute_query(query)
    projects = result if isinstance(result, list) else []
    return render_template('projects.html', projects=projects)

@bp.route('/<int:id>')
def project_detail(id):
    query = "SELECT * FROM testflow WHERE testflow_id = ?"
    result = execute_query(query, [id])
    return render_template('project_detail.html', project=result[0]) if result else "Not found", 404

@bp.route('/add', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        if not name:
            return "Name required", 400
        query = "INSERT INTO testflow (name, description, user_id, status) VALUES (?, ?, ?, ?)"
        execute_query(query, [name, description, 1, "new"])
        return redirect(url_for('projects.overview'))
    return render_template('add_project.html')
