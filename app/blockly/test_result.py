"""Klasse voor het opbouwen van een testresultaat."""

import subprocess


class TestResult:
    """
    Hou het resultaat van een Robot test bij.

    Deze klasse verzamelt de testresultaten van een Robot Framework
    test run. Het parsed de output om geslaagde en gefaalde tests
    te tellen, en bewaart alle output regels.
    """

    def __init__(
        self,
        return_code: int,
        counts: dict[str, int],
        output_lines: list[str],
    ) -> None:
        """
        Maak een testresultaat object.

        Args:
            return_code (int): Exit code van het test process
            counts (dict[str, int]): Teller met "geslaagd" en "gefaald"
            output_lines (list[str]): Test output regels

        Returns:
            None
        """
        self.return_code = return_code
        self.counts = counts
        self.output_lines = output_lines

    @classmethod
    def from_process(cls, result: subprocess.CompletedProcess[str]) -> "TestResult":
        """
        Maak TestResult uit Robot test output.

        Parse de Robot Framework output om geslaagde en gefaalde tests
        te tellen. Verwijdert debug-output lines.

        Args:
            result (subprocess.CompletedProcess[str]): Robot test output

        Returns:
            TestResult: Nieuw TestResult object met getelde resultaten
        """
        # Verwijder debug-output regels die niet relevant zijn
        hidden_keywords = {"Output:", "Log:", "Report:"}
        output_lines = [
            line
            for line in result.stdout.split("\n")
            if not any(keyword in line for keyword in hidden_keywords)
        ]

        # Tel hoeveel tests geslaagd zijn (PASS) en gefaald (FAIL)
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
        Zet testresultaat om naar dictionary voor JSON response.

        Args:
            error_output (str): Extra foutmeldingen om toe te voegen

        Returns:
            dict: Testresultaat met return_code, tellers en output
        """
        return {
            "return_code": self.return_code,
            "geslaagd": self.counts["geslaagd"],
            "gefaald": self.counts["gefaald"],
            # Voeg error_output toe aan het einde van de output
            "output": "\n".join(self.output_lines) + error_output,
        }