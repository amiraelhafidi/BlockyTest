"""
Unit tests voor projectrechten (User Story #227).

Test dat:
- Admins ALLE projecten mogen aanpassen
- Gebruikers ALLEEN hun eigen projecten mogen aanpassen
- Niet-ingelogde gebruikers GEEN projecten mogen aanpassen
"""
from unittest.mock import patch, MagicMock

from app import create_app
from app.Overzichtspagina.routes import can_change_project


def _maak_project(user_id):
    """Hulpfunctie: maak een nep-project met een bepaalde eigenaar."""
    project = MagicMock()
    project.user_id = user_id
    return project


@patch("app.Overzichtspagina.routes.is_admin")
def test_admin_mag_project_van_andere_gebruiker_aanpassen(mock_is_admin):
    """Een admin mag elk project aanpassen, ook van iemand anders."""
    mock_is_admin.return_value = True
    project = _maak_project(user_id=42)

    app = create_app()
    with app.test_request_context():
        from flask import session
        session["user_id"] = 1

        assert can_change_project(project) is True


@patch("app.Overzichtspagina.routes.is_admin")
def test_gebruiker_mag_eigen_project_aanpassen(mock_is_admin):
    """Een gewone gebruiker mag zijn eigen project aanpassen."""
    mock_is_admin.return_value = False
    project = _maak_project(user_id=5)

    app = create_app()
    with app.test_request_context():
        from flask import session
        session["user_id"] = 5

        assert can_change_project(project) is True


@patch("app.Overzichtspagina.routes.is_admin")
def test_gebruiker_mag_project_van_anderen_niet_aanpassen(mock_is_admin):
    """Een gewone gebruiker mag NIET een project van iemand anders aanpassen."""
    mock_is_admin.return_value = False
    project = _maak_project(user_id=99)

    app = create_app()
    with app.test_request_context():
        from flask import session
        session["user_id"] = 5

        assert can_change_project(project) is False


@patch("app.Overzichtspagina.routes.is_admin")
def test_niet_ingelogde_gebruiker_mag_geen_project_aanpassen(mock_is_admin):
    """Zonder user_id in de session mag er geen project worden aangepast."""
    mock_is_admin.return_value = False
    project = _maak_project(user_id=5)

    app = create_app()
    with app.test_request_context():
        assert can_change_project(project) is False