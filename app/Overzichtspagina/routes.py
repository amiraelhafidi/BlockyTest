from flask import flash, redirect, render_template, request, url_for

from app.Overzichtspagina import bp
from app.Overzichtspagina.project_form import ProjectForm
from app.Overzichtspagina.project_repository import ProjectRepository


repository = ProjectRepository()


def get_database_error(result):
    if not isinstance(result, dict):
        return None

    return result.get("error") or result.get("reason")


@bp.route("/")
def overview():
    """
    Render the project overview page with all projects ordered by newest first.
    """
    projects = repository.get_all()
    return render_template(
        "projects.html",
        projects=[project.to_template_dict() for project in projects],
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
    return f"Project detail page for project {project_id}"


@bp.route("/delete/<int:id>", methods=["POST"])
def delete_project(id):
    """
    Delete a project by its ID and redirect back to the overview page.
    """
    result = repository.delete(id)
    error = get_database_error(result)

    if error:
        flash("Dit project kan niet worden verwijderd omdat er nog gegevens aan gekoppeld zijn.", "error")
        return redirect(url_for("projects.overview"))

    flash("Project succesvol verwijderd", "success")
    return redirect(url_for("projects.overview"))


@bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_project(id):
    """
    Show the edit form for an existing project and handle updates.
    """
    project = repository.get_by_id(id)

    if not project:
        flash("Project niet gevonden", "error")
        return redirect(url_for("projects.overview"))

    if request.method == "POST":
        form = ProjectForm(request.form)

        if not form.validate():
            flash(form.errors[0], "error")
            return render_template("add_project.html", is_edit=True, project=form.to_project(id, project.status))

        updated_project = form.to_project(testflow_id=id, status=project.status)
        result = repository.update(updated_project)
        error = get_database_error(result)

        if error:
            flash(f"Databasefout: {error}", "error")
            return render_template("add_project.html", is_edit=True, project=updated_project)

        flash("Project succesvol bijgewerkt", "success")
        return redirect(url_for("projects.overview"))

    return render_template("add_project.html", is_edit=True, project=project)


@bp.route("/add", methods=["GET", "POST"])
def add_project():
    """
    Show the add-project form and handle creation of a new project.
    """
    if request.method == "POST":
        form = ProjectForm(request.form)

        if not form.validate():
            flash(form.errors[0], "error")
            return render_template("add_project.html", is_edit=False, project=form.to_project())

        project = form.to_project()
        result = repository.create(project)
        error = get_database_error(result)

        if error:
            flash(f"Databasefout: {error}", "error")
            return render_template("add_project.html", is_edit=False, project=project)

        flash("Project succesvol toegevoegd", "success")
        return redirect(url_for("projects.overview"))

    return render_template("add_project.html", is_edit=False, project={"name": "", "description": ""})
