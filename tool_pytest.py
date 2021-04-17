from pathlib import Path

from base_tool import BaseTool
from util import subprocess_run


class Pytest(BaseTool):
    def setup(self):
        requirements_file = Path(self.directory / "requirements.txt")

        if requirements_file.exists():
            subprocess_run(
                "pip install -r requirements.txt", cwd=str(requirements_file.parent)
            )

    def run_tests(self, report_folder):
        report_file = report_folder / "TEST-pytest.xml"

        command = f"pytest {self.arguments} --junitxml {report_file.absolute()}"
        subprocess_run(command, cwd=str(self.directory))
