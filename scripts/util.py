#!/usr/bin/env python3
import subprocess
import os
import yaml
import sys
import re
import asyncio
import pathlib


def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)

    return wrapped


def call(cmd, args, show=False, ret_exit_code=False):
    # print(f"Running command: {cmd} {' '.join(args)}")
    child = subprocess.Popen([cmd] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    fulloutput = b""
    while True:
        output = child.stderr.readline()
        output += child.stdout.readline()
        if output == b"" and child.poll() is not None:
            break
        if output:
            if show:
                print(output.decode("utf-8"), end="")
            fulloutput += output
    fulloutput = fulloutput.decode("utf-8")
    exit_code = child.poll()
    if ret_exit_code:
        return (exit_code, fulloutput)
    if exit_code != 0:
        raise RuntimeError(fulloutput)
    return fulloutput


def find_branches():
    reflog = call("git", ["reflog"])
    match = re.search("^.*from (.*) to (.*)\n", reflog)
    return (match[2], match[1])


def find_instances():
    # Get list of devops.yml files
    devops_paths = pathlib.Path(".").glob("**/devops.yml")

    # Get name of all conan package instances
    ints = set()
    for devops_path in devops_paths:
        if devops_path
        print(devops_path)
        continue
        with open(devops_path, "r") as devops_file:
            conf = yaml.safe_load(devops_file)
            for instance in conf:
                # If version is in sha commit format
                if not instance or "version" not in instance:
                    if instance and "name" in instance:
                        name = instance["name"]
                    else:
                        name = os.path.basename(os.path.dirname(devops_path))
                    yield name


# Create alias from newest commit hash to branch
@background
def create_alias(name, branch, old_branch, fetch_repo, upload_repo=None):
    match = None
    # Find hash locally
    (exit_code, output) = call("conan", ["get", f"{name}/{old_branch}"], ret_exit_code=True)
    if exit_code == 0:
        match = re.search('alias = ".*/(.*)"\n', output)
    # Then try finding hash from remote
    if not match:
        (exit_code, output) = call("conan", ["get", "-r", fetch_repo, f"{name}/{old_branch}"], ret_exit_code=True)
        if exit_code == 0:
            match = re.search('alias = ".*/(.*)"\n', output)
    if match:
        sha = match[1]
    else:
        # Fallback to HEAD commit hash
        sha = sys.argv[1]
    call("conan", ["alias", f"{name}/{branch}", f"{name}/{sha}"])
    if upload_repo:
        call("conan", ["upload", f"{name}/{branch}", "--all", "-c", "-r", upload_repo])


def create_aliases(branch, old_branch, fetch_repo, upload_repo=None):
    for name in find_instances():
        create_alias(name, branch, old_branch, fetch_repo, upload_repo)