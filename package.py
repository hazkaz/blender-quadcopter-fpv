#! /usr/bin/env python3

import subprocess

files = [
    "quad.py",
    "README.md"
]
command = "zip -FS Quadcopter-addon.zip {}".format(" ".join(f for f in files))
print("running \"{}\"".format(command))
subprocess.run(command.split(" "))