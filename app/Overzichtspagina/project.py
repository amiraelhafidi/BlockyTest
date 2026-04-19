"""Project domain class voor de overzichtspagina.

Een Project object stelt een rij uit de database-tabel testflow voor.
"""


class Project:
    """Bewaart projectdata en gedrag dat bij een project hoort."""

    def __init__(self, testflow_id, name, description, status="nieuw", created_at=None):
        """Maak een Project object met data uit het formulier of de database.

        Args:
            testflow_id (int | None): Uniek id uit de testflow-tabel.
            name (str): Naam van het project.
            description (str): Beschrijving van het project.
            status (str): Status van het project.
            created_at (str | None): Aanmaakdatum uit de database.
        """
        self.testflow_id = testflow_id
        self.name = name
        self.description = description
        self.status = status
        self.created_at = created_at

        self.validation_errors = []
        self.display_data = {
            "name": name,
            "description": description or "Geen beschrijving",
            "status": status,
        }

    def is_valid(self):
        """Controleer of het project genoeg data heeft om opgeslagen te worden.

        Returns:
            bool: True als het project geldig is, anders False.
        """
        self.validation_errors = []

        if not self.name or not self.name.strip():
            self.validation_errors.append("Projectnaam is verplicht")

        return len(self.validation_errors) == 0

    def to_template_dict(self):
        """Zet het Project object om naar data voor een Jinja-template.

        Returns:
            dict: Projectdata die de template kan tonen.
        """
        return {
            "testflow_id": self.testflow_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row):
        """Maak een Project object vanuit een database-rij.

        Args:
            row (dict): Een rij uit de testflow-tabel.

        Returns:
            Project: Nieuw Project object met data uit de database.
        """
        return cls(
            testflow_id=row.get("testflow_id"),
            name=row.get("name", ""),
            description=row.get("description", ""),
            status=row.get("status", "nieuw"),
            created_at=row.get("created_at"),
        )
