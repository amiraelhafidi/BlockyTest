from app.db import execute_query

class BlocklyEditor:

    def __init__(self, workspace_xml, source="manual"):
        self.workspace_xml = workspace_xml
        self.source = source
        self.project_name = "Autosave project" if source == "autosave" else "Project"
        self.messages = {
            "autosave": "Automatisch opgeslagen",
            "manual": "Opgeslagen in database"
        }

    def save(self):
        query = """
        INSERT INTO blockly_project (project_name, workspace_xml)
        VALUES (?, ?)
        """
        result = execute_query(query, [self.project_name, self.workspace_xml])

        if isinstance(result, dict) and "reason" in result:
            return {
                "success": False,
                "message": "Opslaan mislukt",
                "result": result
            }

        return {
            "success": True,
            "message": self.get_message()
        }
    def get_message(self):
        return self.messages.get(self.source, "Opgeslagen")
 