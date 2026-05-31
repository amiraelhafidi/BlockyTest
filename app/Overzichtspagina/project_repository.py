"""Database-acties voor projecten op de overzichtspagina."""

from app.db import execute_query
from app.Overzichtspagina.project import Project


class ProjectRepository:
    """Haalt projecten op uit de database en slaat projectwijzigingen op."""

    def get_all(self, sort="nieuwst"):
        """Haal alle projecten op, gesorteerd van nieuw naar oud.

        Returns:
            list[Project]: Lijst met Project objecten.
        """
        # Bepaal sorteerrichting: DESC = nieuwste eerst, ASC = oudste eerst
        order = "ASC" if sort == "oudste" else "DESC"
        # Sorteer eerst op updated_at (datum wijziging), dan op created_at als fallback
        query = f"SELECT * FROM testflow ORDER BY updated_at {order}, created_at {order}"
        result = execute_query(query)

        # execute_query kan None, dict of list returnen - we verwachten een list
        # Return lege list als query geen resultaten oplevert
        if not isinstance(result, list):
            return []

        # Zet elke database-rij om naar een Project object
        return [Project.from_row(row) for row in result]

    def get_for_user(self, user_id, sort="nieuwst"):
        """
        Haal projecten op die bij een gebruiker horen.
        """
        # Bepaal sorteerrichting: DESC = nieuwste eerst, ASC = oudste eerst
        order = "ASC" if sort == "oudste" else "DESC"
        # Zelfde query als get_all() maar gefilterd op user_id
        query = f"SELECT * FROM testflow WHERE user_id = ? ORDER BY updated_at {order}, created_at {order}"
        result = execute_query(query, [user_id])

        # Zelfde veiligheidscheck als in get_all() - zorg voor consistent gedrag
        if not isinstance(result, list):
            return []

        # Zet elke database-rij om naar een Project object
        return [Project.from_row(row) for row in result]

    def get_by_id(self, project_id):
        """Haal een project op via het testflow_id.

        Args:
            project_id (int): Id van het project.

        Returns:
            Project | None: Gevonden project of None als het project niet bestaat.
        """
        # SELECT specifiek project op basis van ID
        query = "SELECT * FROM testflow WHERE testflow_id = ?"
        result = execute_query(query, [project_id])

        # Controleer of query resultaten opleverde
        if not isinstance(result, list) or not result:
            # Project niet gevonden
            return None

        # Zet eerste (enige) resultaat om naar Project object
        return Project.from_row(result[0])

    def create(self, project, user_id):
        """Sla een nieuw project op in de testflow-tabel.

        Args:
            project (Project): Project dat opgeslagen moet worden.

        Returns:
            dict: Antwoord van de database-API.
        """
        # INSERT nieuwe rij met projectgegevens
        # user_id wordt opgeslagen zodat we later kunnen controleren wie eigenaar is
        query = "INSERT INTO testflow (name, description, user_id, status) VALUES (?, ?, ?, ?)"
        return execute_query(query, [project.name, project.description, user_id, project.status])

    def update(self, project):
        """Werk de naam en beschrijving van een bestaand project bij.

        Args:
            project (Project): Project met bijgewerkte data.

        Returns:
            dict: Antwoord van de database-API.
        """
        # UPDATE bestaande rij
        # CURRENT_TIMESTAMP zorgt dat updated_at automatisch gezet wordt naar huidige datum/tijd
        query = "UPDATE testflow SET name = ?, description = ?, updated_at = CURRENT_TIMESTAMP WHERE testflow_id = ?"
        return execute_query(query, [project.name, project.description, project.testflow_id])

    def update_saved_at(self, project_id):
        """Werk de wijzigingsdatum bij wanneer een project wordt opgeslagen."""
        # Dit wordt aangeroepen wanneer gebruiker in de editor 'opslaan' klikt
        # Zonder inhoudelijke wijzigingen bij te werken, updaten we alleen de timestamp
        query = "UPDATE testflow SET updated_at = CURRENT_TIMESTAMP WHERE testflow_id = ?"
        return execute_query(query, [project_id])

    def delete(self, project_id):
        """Verwijder een project uit de testflow-tabel.

        Args:
            project_id (int): Id van het project dat verwijderd moet worden.

        Returns:
            dict: Antwoord van de database-API.
        """
        # DELETE verwijdert rij uit database
        # Als er foreign keys zijn, kan dit falen (bv. als er noch gelinkte data bestaat)
        query = "DELETE FROM testflow WHERE testflow_id = ?"
        return execute_query(query, [project_id])
