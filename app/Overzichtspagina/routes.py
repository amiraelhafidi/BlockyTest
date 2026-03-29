from flask import render_template
from app.db import execute_query
from app.Overzichtspagina import bp

@bp.route('/projects')
def overview():
    """
    Show an overview of all projects.
    """
    query = "SELECT * FROM projects"
    result = execute_query(query)

    projects = result.get("data", [])

    return render_template('projects.html', projects=projects)


@bp.route('/project/<int:id>')
def project_detail(id):
    """
    Show the details of a project.
    """
    return f"Project detail page for project {id}"


@bp.route('/add', methods=['GET', 'POST'])
def add_project():
    """
    Add a project to the database.
    """
    return "Add project page"

