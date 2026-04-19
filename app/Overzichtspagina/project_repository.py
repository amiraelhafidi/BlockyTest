from app.db import execute_query
from app.Overzichtspagina.project import Project

#ProjectRepository regelt alle SQL voor projecten. Daardoor staat de databasecode niet meer los door mijn routes verspreid.

class ProjectRepository:
    def get_all(self):
        query = "SELECT * FROM testflow ORDER BY created_at DESC"
        result = execute_query(query)

        if not isinstance(result, list):
            return []

        return [Project.from_row(row) for row in result]

    def get_by_id(self, project_id):
        query = "SELECT * FROM testflow WHERE testflow_id = ?"
        result = execute_query(query, [project_id])

        if not isinstance(result, list) or not result:
            return None

        return Project.from_row(result[0])

    def create(self, project):
        query = "INSERT INTO testflow (name, description, user_id, status) VALUES (?, ?, ?, ?)"
        return execute_query(query, [project.name, project.description, 1, project.status])

    def update(self, project):
        query = "UPDATE testflow SET name = ?, description = ? WHERE testflow_id = ?"
        return execute_query(query, [project.name, project.description, project.testflow_id])

    def delete(self, project_id):
        query = "DELETE FROM testflow WHERE testflow_id = ?"
        return execute_query(query, [project_id])
