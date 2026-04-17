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



@bp.route('/delete/<int:id>', methods=['POST'])
def delete_project(id):
    """
    Delete a project by its ID and redirect back to the overview page.
    """
    # 1) Probeer het project te verwijderen
    query = "DELETE FROM testflow WHERE testflow_id = ?"
    result = execute_query(query, [id])

    # 2) Controleer op databasefouten
    error = result.get("error") or result.get("reason") if isinstance(result, dict) else None
    if error:
        return f"Databasefout: {error}"

    # 3) Ga terug naar overzicht
    return redirect(url_for('projects.overview'))

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_project(id):
    """
    Show the edit form for an existing project and handle updates.
    """
    # 1) Haal het bestaande project op
    query = "SELECT * FROM testflow WHERE testflow_id = ?"
    result = execute_query(query, [id])

    if not isinstance(result, list) or not result:
        flash("Project niet gevonden", "error")
        return redirect(url_for('projects.overview'))

    project = result[0]

    if request.method == 'POST':
        # 2) Lees en valideer ingevulde waarden
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        if not name:
            flash("Projectnaam is verplicht", "error")
            return render_template('add_project.html', is_edit=True, project={'name': name, 'description': description})

        # 3) Werk het project bij in de database
        update_query = "UPDATE testflow SET name = ?, description = ? WHERE testflow_id = ?"
        update_result = execute_query(update_query, [name, description, id])

        # 4) Toon foutmelding als update mislukt
        error = update_result.get("error") or update_result.get("reason") if isinstance(update_result, dict) else None
        if error:
            flash(f"Databasefout: {error}", "error")
            return render_template('add_project.html', is_edit=True, project={'name': name, 'description': description})

        # 5) Bij succes terug naar overzicht
        flash("Project succesvol bijgewerkt", "success")
        return redirect(url_for('projects.overview'))

    # GET: laat formulier zien met bestaande projectwaarden
    return render_template(
        'add_project.html',
        is_edit=True,
        project={'name': project.get('name', ''), 'description': project.get('description', '')}
    )


@bp.route('/add', methods=['GET', 'POST']) 
def add_project():
    """
    Show the add-project form and handle creation of a new project.

    On POST, validates the project name, inserts the record into the
    database, and redirects to the overview page after a successful save.
    """

    if request.method == 'POST':
        # 1) Lees en valideer formulier
        name = request.form.get('name', '').strip()
        description = request.form.get('description')
        if not name:
            flash("Projectnaam is verplicht", "error")
            return render_template('add_project.html', is_edit=False, project={'name': name, 'description': description})

        # 2) Sla het project op
        query = "INSERT INTO testflow (name, description, user_id, status) VALUES (?, ?, ?, ?)"
        result = execute_query(query, [name, description, 1, "nieuw"])

        # 3) Toon foutmelding als insert mislukt
        error = result.get("error") or result.get("reason") if isinstance(result, dict) else None
        if error:
            flash(f"Databasefout: {error}", "error")
            return render_template('add_project.html', is_edit=False, project={'name': name, 'description': description})

        # 4) Bij succes terug naar overzicht
        flash("Project succesvol toegevoegd", "success")

        return redirect(url_for('projects.overview'))

    # GET: leeg formulier tonen
    return render_template('add_project.html', is_edit=False, project={'name': '', 'description': ''})
