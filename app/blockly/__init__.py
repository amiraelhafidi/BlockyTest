from datetime import datetime

from flask import Blueprint, session

from app.db import execute_query

bp = Blueprint("blockly", __name__)


def create_testrun(project_id=None):
    if not project_id:
        user_id = session.get("user_id")
        result = execute_query(
            "SELECT testflow_id FROM testflow WHERE user_id = ? ORDER BY testflow_id LIMIT 1",
            [user_id]
        )
        if result:
            project_id = result[0].get("testflow_id")

    if not project_id:
        raise ValueError("Geen project gevonden")

    result = execute_query(
        "INSERT INTO testrun (testflow_id, started_at, status) VALUES (?, ?, 'running')",
        (project_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    return result.get("insertId")


def update_testrun_result(testrun_id, status, passed=0, failed=0, output_xml="", report_html="", log_html=""):
    finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    execute_query(
        "UPDATE testrun SET status = ?, finished_at = ? WHERE testrun_id = ?",
        (status, finished_at, testrun_id)
    )
    execute_query(
        "INSERT INTO testreport (testrun_id, passed_count, failed_count, output_xml, report_html, log_html, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (testrun_id, passed, failed, output_xml, report_html, log_html, finished_at)
    )


from app.blockly import routes