"""
Unit tests voor projectrechten (User Story #227).

Dit testbestand valideert de autorisatie-logica voor projectaanpassingen.
Het zorgt ervoor dat de `can_change_project()` functie correct controleert
welke gebruikers welke projecten mogen wijzigen.

Test scenario's:
- Admins ALLE projecten mogen aanpassen, ongeacht eigenaar
- Gewone gebruikers ALLEEN hun eigen projecten mogen aanpassen
- Niet-ingelogde gebruikers GEEN projecten mogen aanpassen
"""
from unittest.mock import patch, MagicMock

from app import create_app
from app.Overzichtspagina.routes import can_change_project


def _maak_project(user_id):
    """
    Hulpfunctie: creëert een gemockt projectobject.
    
    Dit simuleert een project met een bepaalde eigenaar (user_id).
    Wordt gebruikt in tests om projectrechten te controleren zonder
    de echte database te raadplegen.
    
    Args:
        user_id (int): Het ID van de gebruiker die eigenaar van het project is.
        
    Returns:
        MagicMock: Een gemockt project object met een user_id attribuut.
    """
    project = MagicMock()
    project.user_id = user_id
    return project


@patch("app.Overzichtspagina.routes.is_admin")
def test_admin_mag_project_van_andere_gebruiker_aanpassen(mock_is_admin):
    """
    Test: Een admin mag elk project aanpassen, ook van iemand anders.
    
    Scenario:
    - Ingelogde gebruiker met ID=1
    - is_admin() geeft True terug (is een admin)
    - Project eigenaar is gebruiker met ID=42
    
    Verwacht resultaat: can_change_project() geeft True terug,
    omdat admins alle projecten mogen aanpassen.
    """
    # Mock is_admin() om True terug te geven (gebruiker is admin)
    mock_is_admin.return_value = True
    
    # Maak een project dat toebehoort aan gebruiker 42
    project = _maak_project(user_id=42)

    # Creëer Flask app context voor sessiegegevens
    app = create_app()
    with app.test_request_context():
        from flask import session
        # Zet de huidige ingelogde gebruiker op ID=1 (niet de eigenaar)
        session["user_id"] = 1

        # Assert: Admin mag het project van iemand anders aanpassen
        assert can_change_project(project) is True


@patch("app.Overzichtspagina.routes.is_admin")
def test_gebruiker_mag_eigen_project_aanpassen(mock_is_admin):
    """
    Test: Een gewone gebruiker mag zijn eigen project aanpassen.
    
    Scenario:
    - Ingelogde gebruiker met ID=5
    - is_admin() geeft False terug (geen admin)
    - Project eigenaar is ook gebruiker met ID=5
    
    Verwacht resultaat: can_change_project() geeft True terug,
    omdat de gebruiker de eigenaar van het project is.
    """
    # Mock is_admin() om False terug te geven (gebruiker is geen admin)
    mock_is_admin.return_value = False
    
    # Maak een project dat toebehoort aan gebruiker 5
    project = _maak_project(user_id=5)

    # Creëer Flask app context voor sessiegegevens
    app = create_app()
    with app.test_request_context():
        from flask import session
        # Zet de huidige ingelogde gebruiker op ID=5 (is de eigenaar)
        session["user_id"] = 5

        # Assert: Gebruiker mag zijn eigen project aanpassen
        assert can_change_project(project) is True


@patch("app.Overzichtspagina.routes.is_admin")
def test_gebruiker_mag_project_van_anderen_niet_aanpassen(mock_is_admin):
    """
    Test: Een gewone gebruiker mag NIET een project van iemand anders aanpassen.
    
    Scenario:
    - Ingelogde gebruiker met ID=5
    - is_admin() geeft False terug (geen admin)
    - Project eigenaar is gebruiker met ID=99 (ander persoon)
    
    Verwacht resultaat: can_change_project() geeft False terug,
    omdat de gebruiker niet de eigenaar is en geen admin.
    """
    # Mock is_admin() om False terug te geven (gebruiker is geen admin)
    mock_is_admin.return_value = False
    
    # Maak een project dat toebehoort aan gebruiker 99
    project = _maak_project(user_id=99)

    # Creëer Flask app context voor sessiegegevens
    app = create_app()
    with app.test_request_context():
        from flask import session
        # Zet de huidige ingelogde gebruiker op ID=5 (niet de eigenaar)
        session["user_id"] = 5

        # Assert: Gebruiker mag het project van iemand anders NIET aanpassen
        assert can_change_project(project) is False


@patch("app.Overzichtspagina.routes.is_admin")
def test_niet_ingelogde_gebruiker_mag_geen_project_aanpassen(mock_is_admin):
    """
    Test: Zonder inloggen (geen user_id in sessie) mag er geen project worden aangepast.
    
    Scenario:
    - Geen ingelogde gebruiker (geen user_id in sessie)
    - is_admin() geeft False terug
    - Project eigenaar is gebruiker met ID=5
    
    Verwacht resultaat: can_change_project() geeft False terug,
    omdat de gebruiker niet is ingelogd.
    """
    # Mock is_admin() om False terug te geven
    mock_is_admin.return_value = False
    
    # Maak een project dat toebehoort aan gebruiker 5
    project = _maak_project(user_id=5)

    # Creëer Flask app context voor sessiegegevens
    app = create_app()
    with app.test_request_context():
        # Let op: we zetten GEEN user_id in de sessie (geen ingelogde gebruiker)
        
        # Assert: Niet-ingelogde gebruiker mag geen project aanpassen
        assert can_change_project(project) is False