"""Project domain class voor de overzichtspagina.

Een Project object stelt een rij uit de database-tabel testflow voor.
"""

from datetime import datetime


def _to_datetime(date_value):
    """Zet een datumwaarde om naar een datetime object.

    Args:
        date_value: Datumwaarde (datetime, string of None).

    Returns:
        datetime | None: Omgezette datetime object of None als conversie mislukt.
    """
    # Retourneer None voor lege waarden
    if not date_value:
        return None

    # Zit al in datetime format, geen conversie nodig
    if isinstance(date_value, datetime):
        return date_value

    # Database retourneert soms ISO-format met 'Z' (UTC indicatie)
    # Vervang 'Z' door '+00:00' zodat fromisoformat() het begrijpt
    date_text = str(date_value).replace("Z", "+00:00")

    try:
        # Parse ISO-formatted string naar datetime object
        return datetime.fromisoformat(date_text)
    except ValueError:
        # Parsing mislukt - return None ipv exception
        return None


def _format_date(date_value):
    """Formatteer een datumwaarde naar de notatie dd-mm-yyyy.

    Args:
        date_value: Datumwaarde die geformatteerd moet worden.

    Returns:
        str: Geformatteerde datum of lege string als conversie mislukt.
    """
    # Converteer naar datetime object (handling van verschillende input-types)
    date = _to_datetime(date_value)
    if not date:
        # Geef lege string terug in plaats van None (beter voor templates)
        return ""

    # Nederlandse datumformat: 01-05-2026
    return date.strftime("%d-%m-%Y")


def _format_datetime(date_value):
    """Formatteer een datumwaarde naar de notatie dd-mm-yyyy hh:mm.

    Args:
        date_value: Datumwaarde die geformatteerd moet worden.

    Returns:
        str: Geformatteerde datum en tijd of lege string als conversie mislukt.
    """
    # Converteer naar datetime object
    date = _to_datetime(date_value)
    if not date:
        return ""

    # Nederlandse datetime format: 01-05-2026 14:30
    return date.strftime("%d-%m-%Y %H:%M")


class Project:
    """Bewaart projectdata en gedrag dat bij een project hoort."""

    def __init__(self, testflow_id, name, description, status="nieuw", created_at=None, updated_at=None, user_id=None):
        """Maak een Project object met data uit het formulier of de database.

        Args:
            testflow_id (int | None): Uniek id uit de testflow-tabel.
            name (str): Naam van het project.
            description (str): Beschrijving van het project.
            status (str): Status van het project.
            created_at (str | None): Aanmaakdatum uit de database.
            updated_at (str | None): Datum van laatste wijziging uit de database.
        """
        # Basis projectgegevens
        self.testflow_id = testflow_id
        self.name = name
        self.description = description
        self.status = status
        self.created_at = created_at
        # Als updated_at niet gezet is, gebruik created_at (project net aangemaakt)
        self.updated_at = updated_at or created_at
        self.user_id = user_id

        # Validatiefouten opslaan (bv. wanneer is_valid() wordt aangeroepen)
        self.validation_errors = []
        # Geformatteerde data voor template rendering
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
        # Reset validatiefouten van vorige controle
        self.validation_errors = []

        # Projectnaam is verplicht en mag niet alleen spaties bevatten
        if not self.name or not self.name.strip():
            self.validation_errors.append("Projectnaam is verplicht")

        # Retourneer True als geen fouten (validatie geslaagd)
        return len(self.validation_errors) == 0

    def to_template_dict(self):
        """Zet het Project object om naar data voor een Jinja-template.

        Returns:
            dict: Projectdata die de template kan tonen.
        """
        # Dit heet "DTO" (Data Transfer Object) - een aparte laag voor de template
        # Zo can de template niet per ongeluk interne data wijzigen
        return {
            "testflow_id": self.testflow_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            # Korte datumweergave (bijv. 01-05-2026)
            "created_at": _format_date(self.created_at),
            "updated_at": _format_date(self.updated_at),
            # Lange datumweergave met tijd (bijv. 01-05-2026 14:30)
            "created_at_full": _format_datetime(self.created_at),
            "updated_at_full": _format_datetime(self.updated_at),
            "user_id": self.user_id,
        }

    @classmethod
    def from_row(cls, row):
        """Maak een Project object vanuit een database-rij.

        Args:
            row (dict): Een rij uit de testflow-tabel.

        Returns:
            Project: Nieuw Project object met data uit de database.
        """
        # Dit heet "Factory Method" - convenient way om objekten te creëren
        # .get() met default values voorkomt KeyError als veld ontbreekt in database
        return cls(
            testflow_id=row.get("testflow_id"),
            name=row.get("name", ""),
            description=row.get("description", ""),
            status=row.get("status", "nieuw"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
            user_id=row.get("user_id"),
        )
