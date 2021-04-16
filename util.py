from shlex import split
from subprocess import DEVNULL, Popen, run


def subprocessRun(command, stdout=DEVNULL, stderr=DEVNULL, cwd=None):
    args = split(command)

    return run(args, stdout=stdout, stderr=stderr, text=True, cwd=cwd)


def subprocessPopen(command, stdout=DEVNULL, stderr=DEVNULL, cwd=None):
    args = split(command)

    return Popen(args, stdout=stdout, stderr=stderr, text=True, cwd=cwd)
