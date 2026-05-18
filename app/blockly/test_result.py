import subprocess


class TestResult:

    def __init__(self, return_code, counts, output_lines):
        self.return_code = return_code
        self.counts = counts
        self.output_lines = output_lines

    @classmethod
    def from_process(cls, result):
        hidden_keywords = {"Output:", "Log:", "Report:"}
        output_lines = [
            line for line in result.stdout.split("\n")
            if not any(keyword in line for keyword in hidden_keywords)
        ]

        counts = {
            "geslaagd": sum(1 for line in result.stdout.splitlines() if "| PASS |" in line and line.strip().startswith("|")),
            "gefaald": sum(1 for line in result.stdout.splitlines() if "| FAIL |" in line and line.strip().startswith("|")),
        }

        return cls(return_code=result.returncode, counts=counts, output_lines=output_lines)

    def to_dict(self, error_output=""):
        return {
            "return_code": self.return_code,
            "geslaagd": self.counts["geslaagd"],
            "gefaald": self.counts["gefaald"],
            "output": "\n".join(self.output_lines) + error_output,
        }