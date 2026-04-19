from app.Overzichtspagina.project import Project

# ProjectForm haalt formulierdata uit de request, schoont die op en maakt er een Project object van.
class ProjectForm:
    def __init__(self, form_data):
        self.form_data = form_data
        self.errors = []
        self.cleaned_data = {}

    def validate(self):
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
        return Project(
            testflow_id=testflow_id,
            name=self.cleaned_data.get("name", ""),
            description=self.cleaned_data.get("description", ""),
            status=status,
        )
