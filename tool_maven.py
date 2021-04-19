import logging
from shutil import copy

from base_tool import BaseTool
from util import subprocess_run


class Maven(BaseTool):
    def setup(self):
        command = "mvn compile -q"
        result = subprocess_run(command, cwd=str(self.directory), stdout=None, stderr=None).returncode
        
        if result != 0:
            logging.error(f"Compilation returned with error code {result}")
            exit(result)

    def run_tests(self, report_folder):
        command = f"mvn test {self.arguments} -q"
        subprocess_run(command, cwd=str(self.directory), stdout=None, stderr=None)

    def post_tests(self, report_folder):
        # Copy reports
        report_folder.mkdir(parents=True, exist_ok=True)

        reports = self.directory.rglob("TEST-*.xml")

        for report in reports:
            dest = report_folder / report.name
            if report != dest:
                copy(report, dest)
