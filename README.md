# BlockyTest

> Bouw geautomatiseerde websitetests met sleepblokjes — zonder zelf code te schrijven.

BlockyTest is een webapplicatie waarmee gebruikers visueel een websitetest samenstellen met Blockly-blokken. De blokken worden automatisch vertaald naar een Robot Framework-testbestand en uitgevoerd. De resultaten, met rapport en log, worden opgeslagen en zijn terug te kijken in de testgeschiedenis.

**Workflow:** sleepblokjes → XML → Robot Framework-code → uitvoeren → resultaat opslaan → testgeschiedenis.

## Functionaliteiten

- Visuele testeditor op basis van Blockly
- Automatische vertaling van blokken naar python code
- Testuitvoering met Robot Framework en SeleniumLibrary
- Opslaan van resultaten, rapporten en logs per project
- Testgeschiedenis met status (geslaagd/gefaald) en details
- Project- en gebruikersbeheer met inlogfunctie

## Technologieën

- **Backend:** Python, Flask (Blueprints)
- **Frontend:** Jinja2, JavaScript, Blockly
- **Testuitvoering:** Robot Framework, SeleniumLibrary
- **Database:** externe API (`execute_query` in `app/db.py`)
- **Tests:** pytest
- **Containers:** Docker, docker-compose

## Projectstructuur

```
.
├── app/                  # De Flask-webapplicatie (broncode)
├── docs/                 # Documentatie
├── tests/                # Unit tests
├── Dockerfile            # Image-definitie
├── docker-compose.yml    # Container-setup
├── requirements.txt      # Python-afhankelijkheden
└── wsgi.py               # Startpunt van de applicatie
```

## Documentatie

- **Installatiehandleiding** — de applicatie lokaal opzetten en draaien.
- **Gebruikershandleiding** — hoe je in de applicatie testen bouwt en draait.
- Verdere documentatie staat in de map [`BlockyTest Documentatie`]