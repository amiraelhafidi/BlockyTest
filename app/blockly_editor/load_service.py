from app.db import execute_query

class LoadService:
   def load_latest(self):
       query = """
       SELECT workspace_xml
       FROM blockly_project
       ORDER BY id DESC
       LIMIT 1
       """
       result = execute_query(query)
       if isinstance(result, list) and len(result) > 0:
           return {
               "success": True,
               "workspace_xml": result[0]["workspace_xml"]
           }
       return {
           "success": False,
           "message": "Geen data gevonden"
       }