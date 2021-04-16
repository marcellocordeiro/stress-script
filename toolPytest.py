from pathlib import Path

from util import subprocessPopen, subprocessRun


def pythonSetup(directory):
    requirements = Path(directory / 'requirements.txt')

    if requirements.exists():
        subprocessRun('pip install -r requirements.txt',
                      cwd=str(requirements.parent))


def toolPytest(directory, arguments, reportFolder):
    reportFile = reportFolder / 'TEST-pytest.xml'
    testCommand = f"pytest {arguments} --junitxml {reportFile.absolute()}"
    subprocessRun(testCommand, cwd=str(directory))
