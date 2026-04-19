"""Formulierverwerking voor projecten."""

from app.Overzichtspagina.project import Project


class ProjectForm:
    """Leest, valideert en converteert formulierdata voor projecten."""

    def __init__(self, form_data):
        """Maak een formulier-object met ruwe data uit request.form.

        Args:
            form_data (dict): Formulierdata uit de Flask request.
        """
        self.form_data = form_data
        self.errors = []
        self.cleaned_data = {}

    def validate(self):
        """Controleer de formulierdata en bewaar opgeschoonde waarden.

        Returns:
            bool: True als het formulier geldig is, anders False.
        """
        name = self.form_data.get("name", "").strip()
        description = self.form_data.get("description", "").strip()

        self.cleaned_data = {
            "name": name,
            "description": description,
        }

        if not name:
            self.errors.append("Projectnaam is verplicht")

        return len(self.errors) == 0

    def to_project(self, testflow_id=None, status="nieuw"):
        """Maak een Project object van de gevalideerde formulierdata.

        Args:
            testflow_id (int | None): Id van een bestaand project of None bij nieuw.
            status (str): Status die het Project object moet krijgen.

        Returns:
            Project: Project object op basis van cleaned_data.
        """
        return Project(
            testflow_id=testflow_id,
            name=self.cleaned_data.get("name", ""),
            description=self.cleaned_data.get("description", ""),
            status=status,
        )
