class TestResult:
    """Maakt de uitkomst van een test klaar om aan de gebruiker te laten zien.

    Haalt de regels weg die naar bestanden op de server wijzen, want die zijn
    niet nuttig voor de gebruiker.
    """

    def __init__(self, result):
        """Pak de uitkomst van de test en haal de onnodige regels eruit.

        Args:
            result: De uitkomst van de test, met de returncode en de tekst.
        """
        # Deze regels verwijzen naar bestanden op de server; niet nuttig voor de gebruiker.
        robot_file_lines = {"Output:", "Log:", "Report:"}

        # 0 betekent geslaagd, een ander getal betekent dat de test is gefaald.
        self.return_code = result.returncode

        # Splits de uitvoer in losse regels en laat de bestandsregels weg.
        self.output_lines = [
            line for line in result.stdout.split("\n")
            if not any(word in line for word in robot_file_lines)
        ]

    def to_dict(self):
        """Zet de uitkomst in een dict, klaar om naar de browser te sturen.

        Returns:
            dict: De returncode en de tekst van de test.
        """
        return {
            "return_code": self.return_code,
            "output": "\n".join(self.output_lines),
        }
