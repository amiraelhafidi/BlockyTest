from flask import render_template, request, redirect, url_for
from app.db import execute_query
from app.Overzichtspagina import bp

@bp.route('/projects')
def overview():
    """
    Show an overview of all projects.
    """
    query = "SELECT * FROM testflow ORDER BY created_at DESC"
    result = execute_query(query)

    projects = result if isinstance(result, list) else []

    return render_template('projects.html', projects=projects)


@bp.route('/project/<int:id>')
def project_detail(id):
    """
    Show the details of a project.
    """
    return f"Project detail page for project {id}"



@bp.route('/delete/<int:id>')
def delete_project(id):
    """Delete a project from the database.
    """

    query = "DELETE FROM testflow WHERE testflow_id = ?"
    result = execute_query(query, [id])

    if isinstance(result, dict) and (result.get("error") or result.get("reason")):
        return f"Databasefout: {result.get('error') or result.get('reason')}"

    return redirect(url_for('projects.overview'))



@bp.route('/add', methods=['GET', 'POST']) 
def add_project():
    """
    Add a new project to the database.
    """

    if request.method == 'POST':
        # heeft gebruiker iets ingevuld?
        name = request.form.get('name')
        description = request.form.get('description')
        if not name:
            return "Projectnaam is verplicht."

        # user_id is verplicht in schema.sql, gebruik tijdelijk user 1
        query = "INSERT INTO testflow (name, description, user_id, status) VALUES (?, ?, ?, ?)"
        result = execute_query(query, [name, description, 1, "nieuw"])
        if isinstance(result, dict) and (result.get("error") or result.get("reason")):
            return f"Databasefout: {result.get('error') or result.get('reason')}"

        return redirect(url_for('projects.overview'))
    # doe iets daarna

    return render_template('add_project.html')
