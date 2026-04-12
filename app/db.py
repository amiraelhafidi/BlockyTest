import requests
from flask import current_app

def execute_query(query, values=None):
    url = current_app.config["API_URL"] + "/db"
    api_key = current_app.config["API_KEY"]
    database = current_app.config["DATABASE"]
    
    r = requests.post(
        url=url,
        json={"query": query, "values": values, "database": database},
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10
    )
    return r.json()

