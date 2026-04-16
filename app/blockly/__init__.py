from datetime import datetime
from flask import Blueprint
from app.db import execute_query

bp = Blueprint("blockly", __name__)


def create_testrun():
    """Creates a new testrun entry in the database
    
    Returns:
        int: testrun_id of the created entry
    """
    # Use or create default testflow
    testflows = execute_query("SELECT testflow_id FROM testflow LIMIT 1")
    
    if testflows and len(testflows) > 0:
        testflow_id = testflows[0].get("testflow_id")
    else:
        # Create default testflow if none exists
        result = execute_query(
            "INSERT INTO testflow (name, description, status) VALUES (?, ?, ?)",
            ("Default Testflow", "Auto-created default testflow", "active")
        )
        testflow_id = result.get("insertId")
    
    query = """INSERT INTO testrun (testflow_id, started_at, status) 
               VALUES (?, ?, 'running')"""
    started_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result = execute_query(query, (testflow_id, started_at))
    return result.get("insertId")


def update_testrun_result(testrun_id: int, status: str, passed: int = 0, failed: int = 0):
    """Updates testrun with final status and results
    
    Args:
        testrun_id (int): ID of the testrun to update
        status (str): Final status ('passed', 'failed', 'error')
        passed (int): Number of passed tests
        failed (int): Number of failed tests
    """
    query = """UPDATE testrun SET status = ?, finished_at = ? WHERE testrun_id = ?"""
    finished_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    execute_query(query, (status, finished_at, testrun_id))
    
    # Create testreport
    query_report = """INSERT INTO testreport (testrun_id, passed_count, failed_count, created_at)
                      VALUES (?, ?, ?, ?)"""
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    execute_query(query_report, (testrun_id, passed, failed, created_at))


from app.blockly import routes
