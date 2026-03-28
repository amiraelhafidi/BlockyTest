"""Database functionality for Epic 4"""

import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Load .env from project root (two folders up)
env_path = os.path.join(os.path.dirname(__file__), "../../.env")
load_dotenv(env_path)

api_url = os.getenv("API_URL")
api_key = os.getenv("API_KEY")
database = os.getenv("DATABASE")


def save_test_result(generated_code, status="GENERATED"):
    """
    Saves generated test code to the database.

    Args:
        generated_code (str): contents of the generated .py file
        status (str): test status, default GENERATED

    Returns:
        int: insert ID of the new row
    """
    if not api_url or not api_key or not database:
        raise ValueError("Missing API credentials in .env file")

    url = f"{api_url}/db"
    query = "INSERT INTO s2bima2526_leefooguuxoo98_TESTRESULT (generated_code, status, created_at) VALUES (?, ?, ?)"
    values = (generated_code, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    print(f"[DEBUG] Posting to: {url}")
    print(f"[DEBUG] Database: {database}")
    print(f"[DEBUG] Auth header: Bearer {api_key[:30]}...")

    response = requests.post(
        url=url,
        json={"query": query, "values": values, "database": database},
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10
    )

    print(f"[DEBUG] Status code: {response.status_code}")
    result = response.json()
    print(f"[API Response] {result}")

    if response.status_code == 200 and isinstance(result, dict) and "insertId" in result:
        return result["insertId"]
    else:
        raise ValueError(f"Database error (status {response.status_code}): {result}")


