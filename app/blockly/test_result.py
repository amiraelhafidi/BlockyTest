class TestResult:

    def __init__(self, return_code, output_lines):
        self.return_code = return_code
        self.output_lines = output_lines

    @classmethod
    def from_process(cls, result):
        robot_file_lines = {"Output:", "Log:", "Report:"}
        output_lines = [
            line for line in result.stdout.split("\n")
            if not any(word in line for word in robot_file_lines)
        ]
        return cls(
            return_code=result.returncode,
            output_lines=output_lines
        )

    def to_dict(self, error_output=""):
        return {
            "return_code": self.return_code,
            "output": "\n".join(self.output_lines) + error_output,
        }
