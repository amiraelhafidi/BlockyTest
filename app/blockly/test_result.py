import xml.etree.ElementTree as ET


class TestResult:

    def __init__(self, return_code, passed, failed, output_lines):
        self.return_code = return_code
        self.passed = passed
        self.failed = failed
        self.output_lines = output_lines

    @classmethod
    def from_process(cls, result, output_xml=""):
        robot_file_lines = {"Output:", "Log:", "Report:"}
        output_lines = [
            line for line in result.stdout.split("\n")
            if not any(word in line for word in robot_file_lines)
        ]

        passed = 0
        failed = 0

        if output_xml:
            try:
                root = ET.fromstring(output_xml)
                for stat in root.iter("stat"):
                    if stat.get("name") == "All Tests":
                        passed = int(stat.get("pass", 0))
                        failed = int(stat.get("fail", 0))
                        break
            except Exception:
                pass

        return cls(
            return_code=result.returncode,
            passed=passed,
            failed=failed,
            output_lines=output_lines
        )

    def to_dict(self, error_output=""):
        return {
            "return_code": self.return_code,
            "geslaagd": self.passed,
            "gefaald": self.failed,
            "output": "\n".join(self.output_lines) + error_output,
        }
