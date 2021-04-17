from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree


@dataclass
class Failure:
    class_name: str
    name: str
    description: str
    config: str
    run_number: str


def order(entry):
    if entry.config == "no-stress":
        return (-1, int(entry.run_number))
    else:
        return (int(entry.config), int(entry.run_number))


def parse(dir):
    failures = []

    for subDirectory in dir.iterdir():
        if not subDirectory.is_dir():
            continue

        config = subDirectory.name.split(".")[1]
        run_number = subDirectory.name.split(".")[2]
        xml_files = subDirectory.glob("*.xml")

        for xmlFile in xml_files:
            root = ElementTree.parse(xmlFile).getroot()

            testcases = root.findall("testcase")

            if testcases == []:
                testcases = root.findall("testsuite/testcase")

            for testcase in testcases:
                attributes = testcase.attrib

                for failure in testcase.findall("failure"):
                    failures.append(
                        Failure(
                            attributes["classname"].strip(),
                            attributes["name"].strip(),
                            failure.text.strip(),
                            config.strip(),
                            run_number.strip(),
                        )
                    )

    failures.sort(key=order)
    return failures
