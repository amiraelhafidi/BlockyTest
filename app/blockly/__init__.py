"""Initialisatie en helpers voor Blockly testruns."""

from datetime import datetime

from flask import Blueprint

from app.db import execute_query

bp = Blueprint("blockly", __name__)


def create_testrun() -> int:
    """
    Maakt een nieuw testrun record aan.

    Returns:
        int: Het id van de nieuwe testrun.
    """
    # Gebruik de eerste bestaande testflow.
    testflows = execute_query("SELECT testflow_id FROM testflow LIMIT 1")
    testflow_id = testflows[0].get("testflow_id")

    query = """INSERT INTO testrun (testflow_id, started_at, status)
               VALUES (?, ?, 'running')"""
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = execute_query(query, (testflow_id, started_at))
    return result.get("insertId")


def update_testrun_result(
    testrun_id: int,
    status: str,
    passed: int = 0,
    failed: int = 0,
) -> None:
    """
    Werkt de eindstatus en aantallen van een testrun bij.

    Args:
        testrun_id (int): Id van de testrun.
        status (str): Eindstatus van de run.
        passed (int): Aantal geslaagde tests.
        failed (int): Aantal gefaalde tests.

    Returns:
        None: Deze functie geeft niets terug.
    """
    # Sla eerst de status van de run op.
    query = "UPDATE testrun SET status = ?, finished_at = ? WHERE testrun_id = ?"
    finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_query(query, (status, finished_at, testrun_id))

    # Sla daarna het rapport op.
    query_report = """INSERT INTO testreport (testrun_id, passed_count, failed_count, created_at)
                      VALUES (?, ?, ?, ?)"""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_query(query_report, (testrun_id, passed, failed, created_at))


from app.blockly import routes
