#!/usr/bin/env python3

import argparse
import json
import pathlib
import shutil
import subprocess
import time

from failureParser import parseFailures
from util import getFilesWithExtension, subprocessPopen, subprocessRun


def toolPytest(directory, arguments, outputFolder, configFile):
    subprocess.run('if [ -f requirements.txt ]; then pip install -r requirements.txt; fi',
                   text=True, shell=True, cwd=str(directory))

    # No stress-ng
    currentReportFile = outputFolder / 'report.no-stress' / 'report.xml'
    testCommand = f"pytest {arguments} --junitxml {currentReportFile.absolute()}"
    subprocessRun(testCommand, cwd=str(directory), stdout=subprocess.DEVNULL)

    # With stress-ng
    with open(configFile) as jsonFile:
        configurations = json.load(jsonFile)

    for i, config in enumerate(configurations):
        stressNgCommand = f"stress-ng --cpu {config['cpuWorkers']} --cpu-load {config['cpuLoad']} --vm {config['vmWorkers']} --vm-bytes {config['vmBytes']}%"
        stressNgSubprocess = subprocessPopen(stressNgCommand)

        time.sleep(1)

        currentReportFile = outputFolder / f"report.{i}" / 'report.xml'
        testCommand = f"pytest {arguments} --junitxml {currentReportFile.absolute()}"
        subprocessRun(testCommand, cwd=str(directory),
                      stdout=subprocess.DEVNULL)

        stressNgSubprocess.kill()


def toolMaven(directory, arguments, outputFolder, configFile):
    outputFolder.mkdir(parents=True, exist_ok=True)

    # No stress-ng
    testCommand = f"mvn test {arguments}"
    subprocessRun(testCommand, cwd=str(directory), stdout=subprocess.DEVNULL)

    reports = getFilesWithExtension(
        directory, 'TEST-*.xml', recursively=True)
    (outputFolder / 'report.no-stress').mkdir(parents=True, exist_ok=True)
    for report in reports:
        shutil.copy(report, outputFolder / 'report.no-stress' / report.name)

    # With stress-ng
    with open(configFile) as jsonFile:
        configurations = json.load(jsonFile)

    for i, config in enumerate(configurations):
        stressNgCommand = f"stress-ng --cpu {config['cpuWorkers']} --cpu-load {config['cpuLoad']} --vm {config['vmWorkers']} --vm-bytes {config['vmBytes']}%"
        stressNgSubprocess = subprocessPopen(stressNgCommand)

        time.sleep(1)

        testCommand = f"mvn test {arguments}"
        subprocessRun(testCommand, cwd=str(directory),
                      stdout=subprocess.DEVNULL)

        reports = getFilesWithExtension(directory, 'TEST-*.xml', recursively=True)
        (outputFolder / f"report.{i}").mkdir(parents=True, exist_ok=True)
        for report in reports:
            shutil.copy(report, outputFolder / f"report.{i}" / report.name)

        stressNgSubprocess.kill()


def main(args):
    tool = args.tool
    directory = pathlib.Path(args.directory)
    outputFolder = pathlib.Path(
        args.output_folder if args.output_folder else '.') / 'output'

    configFile = pathlib.Path(__file__).parent / 'stressConfigurations.json'

    arguments = ''

    if tool == 'pytest':
        toolPytest(directory, arguments, outputFolder, configFile)
    elif tool == 'maven':
        toolMaven(directory, arguments, outputFolder, configFile)
    else:
        pass

    failures = parseFailures(outputFolder)

    if len(failures) != 0:
        print("The following tests have failed")

        for failure in failures:
            print(f"stress-ng configuration: {failure.configuration}")
            print(f"classname: {failure.className}")
            print(f"name: {failure.name}")
            print(f"description: {failure.description}")
            print('')

        exit(1)
    else:
        exit(0)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('tool', choices=['pytest', 'maven'],
                        help='specify testing tool')

    parser.add_argument('directory', help='specify directory')

    parser.add_argument('-e', '--extra-arguments',
                        help="specify extra arguments")

    parser.add_argument('--no-stress',
                        help="don't use stress-ng", action="store_true")

    parser.add_argument('-o', '--output-folder',
                        help="specify output folder")

    args = parser.parse_args()

    main(args)
