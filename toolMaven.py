from shutil import copy

from util import subprocessPopen, subprocessRun


def toolMaven(directory, arguments, reportFolder):
    testCommand = f"mvn test {arguments}"
    subprocessRun(testCommand, cwd=str(directory))

    # Copy reports
    reportFolder.mkdir(parents=True, exist_ok=True)

    reports = directory.rglob('TEST-*.xml')

    for report in reports:
        dest = reportFolder / report.name
        if report != dest:
            copy(report, dest)
