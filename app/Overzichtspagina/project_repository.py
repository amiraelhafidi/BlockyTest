"""Database-acties voor projecten op de overzichtspagina."""

from app.db import execute_query
from app.Overzichtspagina.project import Project


class ProjectRepository:
    """Haalt projecten op uit de database en slaat projectwijzigingen op."""

    def get_all(self):
        """Haal alle projecten op, gesorteerd van nieuw naar oud.

        Returns:
            list[Project]: Lijst met Project objecten.
        """
        query = "SELECT * FROM testflow ORDER BY created_at DESC"
        result = execute_query(query)

        if not isinstance(result, list):
            return []

        return [Project.from_row(row) for row in result]

    def get_for_user(self, user_id):
        """
        Haal projecten op die bij een gebruiker horen.
        """
        query = "SELECT * FROM testflow WHERE user_id = ? ORDER BY created_at DESC"
        result = execute_query(query, [user_id])

        if not isinstance(result, list):
            return []

        return [Project.from_row(row) for row in result]

    def get_by_id(self, project_id):
        """Haal een project op via het testflow_id.

        Args:
            project_id (int): Id van het project.

        Returns:
            Project | None: Gevonden project of None als het project niet bestaat.
        """
        query = "SELECT * FROM testflow WHERE testflow_id = ?"
        result = execute_query(query, [project_id])

        if not isinstance(result, list) or not result:
            return None

        return Project.from_row(result[0])

    def create(self, project, user_id):
        """Sla een nieuw project op in de testflow-tabel.

        Args:
            project (Project): Project dat opgeslagen moet worden.

        Returns:
            dict: Antwoord van de database-API.
        """
        query = "INSERT INTO testflow (name, description, user_id, status) VALUES (?, ?, ?, ?)"
        return execute_query(query, [project.name, project.description, user_id, project.status])

    def update(self, project):
        """Werk de naam en beschrijving van een bestaand project bij.

        Args:
            project (Project): Project met bijgewerkte data.

        Returns:
            dict: Antwoord van de database-API.
        """
        query = "UPDATE testflow SET name = ?, description = ? WHERE testflow_id = ?"
        return execute_query(query, [project.name, project.description, project.testflow_id])

    def delete(self, project_id):
        """Verwijder een project uit de testflow-tabel.

        Args:
            project_id (int): Id van het project dat verwijderd moet worden.

        Returns:
            dict: Antwoord van de database-API.
        """
        query = "DELETE FROM testflow WHERE testflow_id = ?"
        return execute_query(query, [project_id])
