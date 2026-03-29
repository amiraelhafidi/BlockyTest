# db_saver.py
# Doel: slaat de gegenereerde testcode op in de database

import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Laad .env vanuit de projectroot
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))


def save_test_result(generated_code, status="GENERATED"):
    """
    Slaat de testcode op in de database via de API.
    Voegt ook de huidge tijd toe.

    Args:
        generated_code (str): de gegenereerde testcode
        status         (str): status van de test (standaard "GENERATED")

    Returns:
        int: het ID van de opgeslagen rij in de database
    """
    url      = os.getenv("API_URL") + "/db"
    api_key  = os.getenv("API_KEY")
    database = os.getenv("DATABASE")

    query  = "INSERT INTO testresult (generated_code, status, created_at) VALUES (?, ?, ?)"
    values = (generated_code, status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    response = requests.post(
        url=url,
        json={"query": query, "values": values, "database": database},
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10
    )

    result = response.json()

    if response.status_code == 200 and "insertId" in result:
        return result["insertId"]
    else:
        raise ValueError(f"[FOUT] Database error: {result}")