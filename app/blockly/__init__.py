"""Initialisatie en database functies voor Blockly testruns.

Dit bestand definieert:
- create_testrun(): Maak nieuw testrun record
- update_testrun_result(): Update status en sla resultaten op
"""

from datetime import datetime

from flask import Blueprint

from app.db import execute_query

bp = Blueprint("blockly", __name__)


def create_testrun() -> int:
    """
    Maak een nieuw testrun record in de database.

    Slaat het start moment op en zet status op "running".

    Returns:
        int: ID van de nieuwe testrun record
    """
    # Haal eerste testflow op (moet minstens één bestaan)
    testflows = execute_query("SELECT testflow_id FROM testflow LIMIT 1")
    testflow_id = testflows[0].get("testflow_id")

    # Maak nieuw record met huidige timestamp
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
    Update testrun status en sla testresultaten op.

    Zet de eindstatus van een test run en telt geslaagde/gefaalde
    tests op. Slaat alles in de database op.

    Args:
        testrun_id (int): ID van de testrun
        status (str): Eindstatus ("passed", "failed", "error")
        passed (int): Aantal geslaagde tests
        failed (int): Aantal gefaalde tests

    Returns:
        None
    """
    # Update testrun tabel met eindstatus en finish tijd
    query = "UPDATE testrun SET status = ?, finished_at = ? WHERE testrun_id = ?"
    finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_query(query, (status, finished_at, testrun_id))

    # Sla testresultaten op in testreport tabel
    query_report = """INSERT INTO testreport (testrun_id, passed_count, failed_count, created_at)
                      VALUES (?, ?, ?, ?)"""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_query(query_report, (testrun_id, passed, failed, created_at))
