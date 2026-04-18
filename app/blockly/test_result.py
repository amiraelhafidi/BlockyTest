"""Class voor het opbouwen van een testresultaat."""

import subprocess


class TestResult:
    """
    Houdt het resultaat van een Blocky testrun bij.

    Attributes:
        return_code (int): Exit code van de test.
        counts (dict[str, int]): Aantallen geslaagd en gefaald.
        output_lines (list[str]): Regels van de opgeschoonde output.
    """

    def __init__(
        self,
        return_code: int,
        counts: dict[str, int],
        output_lines: list[str],
    ) -> None:
        """
        Maakt een nieuw testresultaat.

        Args:
            return_code (int): Exit code van de test.
            counts (dict[str, int]): Aantallen geslaagd en gefaald.
            output_lines (list[str]): Regels van de output.

        Returns:
            None: Deze constructor geeft niets terug.
        """
        self.return_code = return_code
        self.counts = counts
        self.output_lines = output_lines

    @classmethod
    def from_process(cls, result: subprocess.CompletedProcess[str]) -> "TestResult":
        """
        Maakt een TestResult van een subprocess resultaat.

        Args:
            result (subprocess.CompletedProcess[str]): Uitkomst van de test-run.

        Returns:
            TestResult: Nieuw opgebouwd testresultaat.
        """
        hidden_keywords = {"Output:", "Log:", "Report:"}
        output_lines = [
            line
            for line in result.stdout.split("\n")
            if not any(keyword in line for keyword in hidden_keywords)
        ]

        counts = {
            "geslaagd": result.stdout.count("| PASS |"),
            "gefaald": result.stdout.count("| FAIL |"),
        }

        return cls(
            return_code=result.returncode,
            counts=counts,
            output_lines=output_lines,
        )

    def to_dict(self, error_output: str = "") -> dict:
        """
        Zet het testresultaat om naar een dictionary voor JSON.

        Args:
            error_output (str): Extra stderr output.

        Returns:
            dict: Resultaat voor de API response.
        """
        return {
            "return_code": self.return_code,
            "geslaagd": self.counts["geslaagd"],
            "gefaald": self.counts["gefaald"],
            "output": "\n".join(self.output_lines) + error_output,
        }
