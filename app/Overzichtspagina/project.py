# Eén Project object stelt één rij uit de database-tabel testflow voor

class Project:
    def __init__(self, testflow_id, name, description, status="nieuw", created_at=None):
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
        self.validation_errors = []

        if not self.name or not self.name.strip():
            self.validation_errors.append("Projectnaam is verplicht")

        return len(self.validation_errors) == 0

    def to_template_dict(self):
        return {
            "testflow_id": self.testflow_id,
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row):
        return cls(
            testflow_id=row.get("testflow_id"),
            name=row.get("name", ""),
            description=row.get("description", ""),
            status=row.get("status", "nieuw"),
            created_at=row.get("created_at"),
        )
