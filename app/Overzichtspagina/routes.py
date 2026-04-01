from flask import render_template, request, redirect, url_for
from app.db import execute_query
from app.Overzichtspagina import bp

@bp.route('/projects')
def overview():
    """
    Show an overview of all projects.
    """
    query = "SELECT * FROM projects"
    result = execute_query(query)

    projects = result if isinstance(result, list) else []

    return render_template('projects.html', projects=projects)


@bp.route('/project/<int:id>')
def project_detail(id):
    """
    Show the details of a project.
    """
    return f"Project detail page for project {id}"


@bp.route('/add', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        # heeft gebruiker iets ingevuld?
        name = request.form.get('name')
        description = request.form.get('description')
        if not name:
            return "Projectnaam is verplicht."

        query = "INSERT INTO projects (name, description) VALUES (?, ?)"
        result = execute_query(query, [name, description])

        if isinstance(result, dict) and result.get("error"):
            return f"Databasefout: {result['error']}"

        return redirect(url_for('projects.overview'))
    # doe iets daarna

    return render_template('add_project.html')

