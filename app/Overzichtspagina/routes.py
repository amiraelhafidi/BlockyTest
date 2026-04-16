from flask import flash, render_template, request, redirect, url_for
from app.db import execute_query
from app.Overzichtspagina import bp

@bp.route('/projects')
def overview():
    """
    Render the project overview page with all projects ordered by newest first.
    """
    query = "SELECT * FROM testflow ORDER BY created_at DESC"
    result = execute_query(query)

    projects = result if isinstance(result, list) else []

    return render_template('projects.html', projects=projects)


@bp.route('/project/<int:id>')
def project_detail(id):
    """
    Return the detail view for a single project.
    """
    return f"Project detail page for project {id}"



@bp.route('/delete/<int:id>')
def delete_project(id):
    """
    Delete a project by its ID and redirect back to the overview page.
    """

    query = "DELETE FROM testflow WHERE testflow_id = ?"
    result = execute_query(query, [id])

    if isinstance(result, dict) and (result.get("error") or result.get("reason")):
        return f"Databasefout: {result.get('error') or result.get('reason')}"

    return redirect(url_for('projects.overview'))



@bp.route('/add', methods=['GET', 'POST']) 
def add_project():
    """
    Show the add-project form and handle creation of a new project.

    On POST, validates the project name, inserts the record into the
    database, and redirects to the overview page after a successful save.
    """

    if request.method == 'POST':
        # heeft gebruiker iets ingevuld?
        name = request.form.get('name', '').strip()
        description = request.form.get('description')
        if not name:
            flash("Projectnaam is verplicht", "error")
            return render_template('add_project.html')

        # user_id is verplicht in schema.sql, gebruik tijdelijk user 1
        query = "INSERT INTO testflow (name, description, user_id, status) VALUES (?, ?, ?, ?)"
        result = execute_query(query, [name, description, 1, "nieuw"])
        
        if isinstance(result, dict) and (result.get("error") or result.get("reason")):
            flash(f"Databasefout: {result.get('error') or result.get('reason')}", "error")
            return render_template('add_project.html')

        flash("Project succesvol toegevoegd", "success")

        return redirect(url_for('projects.overview'))

    return render_template('add_project.html')
