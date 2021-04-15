from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree


@dataclass
class Failure:
    className: str
    name: str
    description: str
    configuration: str


def parseFailures(dir):
    failures = []

    for subDirectory in dir.iterdir():
        if not subDirectory.is_dir():
            continue

        configuration = subDirectory.name.split('.')[1]
        xmlFiles = subDirectory.glob('*.xml')

        for xmlFile in xmlFiles:
            root = ElementTree.parse(xmlFile).getroot()

            testcases = root.findall('testcase')

            if testcases == []:
                testcases = root.findall('testsuite/testcase')

            for testcase in testcases:
                attributes = testcase.attrib

                for failure in testcase.findall('failure'):
                    failures.append(Failure(attributes['classname'].strip(
                    ), attributes['name'].strip(), failure.text.strip(), configuration.strip()))

    return failures
