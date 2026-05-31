"""Routes voor projectbeheer op de Overzichtspagina.

Handelt CRUD-operaties voor projecten af, inclusief overzicht, details,
toevoegen, bewerken en verwijderen van projecten.
"""

from flask import flash, jsonify, redirect, render_template, request, session, url_for

from app.Overzichtspagina import bp
from app.Overzichtspagina.loginroutes import is_admin
from app.Overzichtspagina.project_form import ProjectForm
from app.Overzichtspagina.project_repository import ProjectRepository


repository = ProjectRepository()


def can_change_project(project):
    """
    Admins mogen alle projecten aanpassen. Gebruikers alleen hun eigen projecten.
    """
    return is_admin() or project.user_id == session.get("user_id")


def get_database_error(result):
    """Haal een foutmelding uit het database-resultaat als die bestaat.

    Args:
        result (dict | list | None): Antwoord van de database-API.

    Returns:
        str | None: Foutmelding uit het resultaat of None als er geen fout is.
    """
    if not isinstance(result, dict):
        return None

    return result.get("error") or result.get("reason")


@bp.route("/")
def overview():
    """
    Render the project overview page with all projects ordered by newest first.
    """
    sort = request.args.get("sort", "nieuwst")

    # Admins zien alle projecten, normale gebruikers alleen hun eigen projecten
    if is_admin():
        projects = repository.get_all(sort=sort)
        title = "Alle projecten"
    else:
        projects = repository.get_for_user(session.get("user_id"), sort=sort)
        title = "Mijn projecten"

    return render_template(
        "projects.html",
        projects=[project.to_template_dict() for project in projects],
        title=title,
        sort=sort,
    )


@bp.route("/projects")
def legacy_overview():
    """
    Keep the old /projects/projects URL working and redirect to the clean overview URL.
    """
    return redirect(url_for("projects.overview"))


@bp.route("/project/<int:project_id>")
def project_detail(project_id):
    """
    Return the detail view for a single project.
    """
    project = repository.get_by_id(project_id)

    if not project:
        flash("Project niet gevonden", "error")
        return redirect(url_for("projects.overview"))

    if not can_change_project(project):
        flash("Je mag dit project niet bekijken.", "error")
        return redirect(url_for("projects.overview"))

    return f"Project detail page for project {project_id}"


@bp.route("/mark-saved/<int:project_id>", methods=["POST"])
def mark_project_saved(project_id):
    """
    Update de wijzigingsdatum nadat een project is opgeslagen in de editor.
    """
    project = repository.get_by_id(project_id)

    if not project:
        return jsonify({"success": False, "message": "Project niet gevonden"}), 404

    if not can_change_project(project):
        return jsonify({"success": False, "message": "Geen toegang"}), 403

    repository.update_saved_at(project_id)
    return jsonify({"success": True})


@bp.route("/delete/<int:id>", methods=["POST"])
def delete_project(id):
    """
    Delete a project by its ID and redirect back to the overview page.
    """
    # 1. Controleer of project exists
    project = repository.get_by_id(id)

    if not project:
        flash("Project niet gevonden", "error")
        return redirect(url_for("projects.overview"))

    # 2. Controleer permissies - mag deze gebruiker dit project verwijderen?
    if not can_change_project(project):
        flash("Je mag dit project niet verwijderen.", "error")
        return redirect(url_for("projects.overview"))

    # 3. Verwijder project uit database
    result = repository.delete(id)
    error = get_database_error(result)

    # 4. Controleer of er databasefouten waren
    if error:
        flash("Dit project kan niet worden verwijderd omdat er nog gegevens aan gekoppeld zijn.", "error")
        return redirect(url_for("projects.overview"))

    # 5. Succesvol verwijderd - toon feedback en ga terug naar overzicht
    flash("Project succesvol verwijderd", "success")
    return redirect(url_for("projects.overview"))


@bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_project(id):
    """
    Show the edit form for an existing project and handle updates.
    """
    # 1. Haal project op om te controleren of het bestaat
    project = repository.get_by_id(id)

    if not project:
        flash("Project niet gevonden", "error")
        return redirect(url_for("projects.overview"))

    # 2. Controleer permissies - mag deze gebruiker dit project bewerken?
    if not can_change_project(project):
        flash("Je mag dit project niet bewerken.", "error")
        return redirect(url_for("projects.overview"))

    # 3. Verwerk het formulier als POST
    if request.method == "POST":
        # Parse en valideer formulierdata
        form = ProjectForm(request.form)

        if not form.validate():
            # Fout in validatie - toon formulier met foutmelding
            flash(form.errors[0], "error")
            # Behoud de huidige project status, change alleen name en description
            return render_template("add_project.html", is_edit=True, project=form.to_project(id, project.status))

        # Maak updated project object met bestaande ID en status
        updated_project = form.to_project(testflow_id=id, status=project.status)
        result = repository.update(updated_project)
        error = get_database_error(result)

        if error:
            # Databasefout - toon formulier met error
            flash(f"Databasefout: {error}", "error")
            return render_template("add_project.html", is_edit=True, project=updated_project)

        # Succesvol bijgewerkt
        flash("Project succesvol bijgewerkt", "success")
        return redirect(url_for("projects.overview"))

    # 4. GET request - toon bewerken formulier met huidige project data
    return render_template("add_project.html", is_edit=True, project=project)


@bp.route("/add", methods=["GET", "POST"])
def add_project():
    """
    Show the add-project form and handle creation of a new project.
    """
    # 1. Verwerk het formulier als POST
    if request.method == "POST":
        # Parse en valideer formulierdata
        form = ProjectForm(request.form)

        if not form.validate():
            # Fout in validatie - toon formulier met foutmelding
            flash(form.errors[0], "error")
            # Toon formulier met eerder ingevoerde data zodat gebruiker niet alles opnieuw typt
            return render_template("add_project.html", is_edit=False, project=form.to_project())

        # Maak nieuw project object (geen ID, want nog niet in database)
        project = form.to_project()
        # Sla op in database (eerste parameter is user_id van ingelogde gebruiker)
        result = repository.create(project, session.get("user_id"))
        error = get_database_error(result)

        if error:
            # Databasefout - toon formulier met error
            flash(f"Databasefout: {error}", "error")
            return render_template("add_project.html", is_edit=False, project=project)

        # Succesvol aangemaakt
        flash("Project succesvol toegevoegd", "success")
        return redirect(url_for("projects.overview"))

    # 2. GET request - toon leeg aanvoeformulier
    return render_template("add_project.html", is_edit=False, project={"name": "", "description": ""})
