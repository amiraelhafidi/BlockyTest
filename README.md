# BlockyTest

> Bouw geautomatiseerde websitetests met sleepblokjes — zonder zelf code te schrijven.

BlockyTest is een webapplicatie waarmee gebruikers visueel een websitetest samenstellen met Blockly-blokken. De blokken worden automatisch vertaald naar een Robot Framework-testbestand en uitgevoerd. De resultaten, met rapport en log, worden opgeslagen en zijn terug te kijken in de testgeschiedenis.

**Workflow:** sleepblokjes → XML → Robot Framework-code → uitvoeren → resultaat opslaan → testgeschiedenis.

## Functionaliteiten

- Visuele testeditor op basis van Blockly
- Automatische vertaling van blokken naar Robot Framework-code
- Testuitvoering met Robot Framework en SeleniumLibrary
- Opslaan van resultaten, rapporten en logs per project
- Testgeschiedenis met status (geslaagd/gefaald) en details
- Project- en gebruikersbeheer met inlogfunctie

## Technologieën

- **Backend:** Python, Flask (Blueprints)
- **Frontend:** Jinja2, JavaScript, Blockly
- **Testuitvoering:** Robot Framework, SeleniumLibrary
- **Database:** externe REST API (`app/db.py`)
- **Tests:** pytest
- **Containers:** Docker, docker-compose

---

## Projectstructuur

```
BlockyTest/
│
├── app/                            # Flask-webapplicatie (alle broncode)
│   ├── __init__.py                 # App factory: maakt de Flask-app aan
│   ├── db.py                       # Database-koppeling via externe REST API
│   ├── schema.sql                  # SQL-schema van alle tabellen
│   ├── settings.py                 # Applicatie-instellingen
│   │
│   ├── main/                       # Blueprint: welkomstpagina (/)
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── Overzichtspagina/           # Blueprint: projecten en gebruikersbeheer (/projects)
│   │   ├── __init__.py
│   │   ├── routes.py               # CRUD voor projecten (overzicht, toevoegen, bewerken, verwijderen)
│   │   ├── loginroutes.py          # Inloggen, registreren, account, uitloggen
│   │   ├── project.py              # Project-dataklasse
│   │   ├── project_form.py         # Formuliervalidatie voor projecten
│   │   └── project_repository.py  # Database-aanroepen voor projecten
│   │
│   ├── blockly/                    # Blueprint: Blockly-editor en testuitvoering (/blockly)
│   │   ├── __init__.py
│   │   ├── routes.py               # Editor, run, opslaan, laden, geschiedenis, testrun-detail
│   │   ├── code_generator.py       # Zet Blockly-XML om naar Robot Framework-code
│   │   ├── robot_translator.py     # Loopt door de XML en vertaalt blokken naar keywords
│   │   └── test_result.py          # Verwerkt de uitvoer van Robot Framework
│   │
│   ├── blockly_editor/             # Hulpmodule voor de editor (laden van workspace)
│   │   ├── blockly_editor.py
│   │   └── load_service.py
│   │
│   ├── events/                     # Blueprint: events (voorbeeldmodule)
│   │   └── routes.py
│   │
│   ├── projects/                   # Oudere projectenmodule (legacy)
│   │   └── routes.py
│   │
│   ├── static/                     # Statische bestanden (CSS, JS, afbeeldingen)
│   │   ├── css/
│   │   │   ├── style.css           # Algemene stijlen
│   │   │   ├── blockly.css         # Stijlen voor de Blockly-editor
│   │   │   ├── projects.css        # Stijlen voor de projectenpagina
│   │   │   ├── welcome.css         # Stijlen voor de welkomstpagina
│   │   │   └── testrun_history.css # Stijlen voor de testgeschiedenispagina
│   │   ├── js/
│   │   │   ├── blockly_editor.js   # Logica van de editor (opslaan, laden, uitvoeren, resultaat tonen)
│   │   │   └── custom_blocks.js    # Definitie en Python-codegenerators van alle Blockly-blokken
│   │   └── img/                    # Logo's en voorbeeldafbeeldingen
│   │
│   └── templates/                  # Jinja2 HTML-templates
│       ├── welcome.html            # Welkomstpagina
│       ├── loginpage.html          # Inlogpagina
│       ├── registerpage.html       # Registratiepagina
│       ├── accountpage.html        # Accountpagina (wachtwoord wijzigen, account verwijderen)
│       ├── projects.html           # Projectenoverzicht
│       ├── add_project.html        # Formulier: project toevoegen / bewerken
│       ├── project_detail.html     # Detailpagina van een project
│       ├── blockly.html            # Blockly-editor pagina
│       ├── testrun_history.html    # Overzicht van testruns per project
│       └── testrun_detail.html     # Detailpagina van één testrun
│
├── tests/                          # Geautomatiseerde tests
│   ├── test_code_generator.py      # Unit tests voor de code-generator
│   ├── test_project_permissions.py # Unit tests voor projectrechten
│   ├── test.robot                  # Robot Framework end-to-end test
│   └── test_input.xml              # Testinvoer voor Robot Framework
│
├── BlocklyTest Documentatie/       # Alle projectdocumentatie
│   ├── BlockyTest - Installatiehandleiding.pdf
│   ├── Gebruikershandleiding van BlockyTest.pdf
│   ├── Diagrammen/                 # ERD, EERD, BPMN, Use Case Diagrammen
│   ├── Huisstijl & Logo/           # Logo, huisstijlkleuren, teamposter
│   ├── Leerproces/                 # Individuele leerverslagen per sprint
│   ├── Onderzoek/                  # Gebruikersonderzoek, technische keuzes, Business Model Canvas
│   ├── Planning/                   # Plan van aanpak en sprintplanningen (sprint 1 t/m 4)
│   ├── Schetsen/                   # Low-fi ontwerpen, wireframes, US-schetsen
│   ├── Sprint reviews/             # Sprint review verslagen (sprint 1 t/m 4)
│   └── Team & Samenwerking/        # Samenwerkingscontract, SLA, merge-afspraken
│
├── docs/                           # MkDocs bronbestanden (technische API-documentatie)
│   └── requirements.txt            # Extra packages voor het bouwen van de docs-site
│
├── .env                            # Omgevingsvariabelen (API_URL, API_KEY, DATABASE)
├── .flaskenv                       # Flask-configuratie (FLASK_APP, FLASK_ENV)
├── requirements.txt                # Python-afhankelijkheden
├── wsgi.py                         # Startpunt van de applicatie
├── Dockerfile                      # Docker image-definitie
├── docker-compose.yml              # Docker Compose setup
├── mkdocs.yml                      # Configuratie voor MkDocs documentatiesite
└── gitlab-ci.yml                   # CI/CD pipeline configuratie
```

---

## Documentatie

Alle handleidingen en projectdocumentatie staan in de map **`BlocklyTest Documentatie/`**:

| Document | Locatie |
|---|---|
| Installatiehandleiding | `BlocklyTest Documentatie/BlockyTest - Installatiehandleiding.pdf` |
| Gebruikershandleiding | `BlocklyTest Documentatie/Gebruikershandleiding van BlockyTest.pdf` |
| ERD / EERD / Diagrammen | `BlocklyTest Documentatie/Diagrammen/` |
| Wireframes & schetsen | `BlocklyTest Documentatie/Schetsen/` |
| Sprintplanningen | `BlocklyTest Documentatie/Planning/` |
| Sprint reviews | `BlocklyTest Documentatie/Sprint reviews/` |
| Onderzoek | `BlocklyTest Documentatie/Onderzoek/` |
| Samenwerkingscontract & SLA | `BlocklyTest Documentatie/Team & Samenwerking/` |
| Leerverslagen | `BlocklyTest Documentatie/Leerproces/` |

---

## Lokaal opstarten

### Vereisten

- Python 3.13 of hoger

### Installatie

```powershell
# 1. Kloon de repository
git clone <repo-url>
cd BlockyTest

# 2. Maak een virtual environment aan en activeer het
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Installeer de afhankelijkheden
pip install -r requirements.txt

# 4. Start de applicatie
flask run
```

De applicatie is daarna bereikbaar op **http://127.0.0.1:5000**.

### Omgevingsvariabelen

Het bestand `.env` bevat de verbindingsgegevens voor de externe database-API:

```
API_URL=https://api.hbo-ict.cloud
API_KEY=<sleutel>
DATABASE=<databasenaam>
```

---

## Tests uitvoeren

```powershell
# Unit tests (pytest)
pytest tests/

# Robot Framework end-to-end test
python -m robot tests/test.robot
```

---

## Docker

```powershell
docker-compose up --build
```
