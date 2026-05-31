from datetime import datetime

from flask import Blueprint

from app.db import execute_query

bp = Blueprint("blockly", __name__)


def create_testrun(project_id):
    """Maak een nieuwe testrun aan vóór de test draait.

    Args:
        project_id (int): Id van het project (testflow) waar de testrun bij hoort.

    Returns:
        int: Het id van de zojuist aangemaakte testrun-rij.

    Raises:
        ValueError: Als er geen project is meegegeven.
    """
    if not project_id:
        raise ValueError("Geen project gekozen")

    result = execute_query(
        "INSERT INTO testrun (testflow_id, started_at, status) VALUES (?, ?, 'running')",
        (project_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    return result.get("insertId")


def update_testrun_result(testrun_id, status, report_html="", log_html=""):
    """Sla het resultaat van een testrun op ná afloop van de test.

    Werkt de bestaande testrun-rij bij naar de eindstatus en eindtijd, en
    bewaart het bijbehorende rapport en de log in de aparte testreport-tabel.

    Args:
        testrun_id (int): Id van de testrun die bijgewerkt moet worden.
        status (str): Eindstatus van de test, bijvoorbeeld 'passed' of 'failed'.
        report_html (str): HTML van het testrapport. Standaard leeg.
        log_html (str): HTML van de testlog. Standaard leeg.
    """
    finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_query(
        "UPDATE testrun SET status = ?, finished_at = ? WHERE testrun_id = ?",
        (status, finished_at, testrun_id)
    )
    execute_query(
        "INSERT INTO testreport (testrun_id, report_html, log_html, created_at) VALUES (?, ?, ?, ?)",
        (testrun_id, report_html, log_html, finished_at)
    )


from app.blockly import routes