#! /usr/bin/env python3

import subprocess

files = [
    "quad_simulator/__init__.py",
    "quad_simulator/quad.py",
    "quad_simulator/ensure_dependencies.py",
]
command = "zip -FS Quadcopter-addon.zip {}".format(" ".join(f for f in files))
print("running \"{}\"".format(command))
subprocess.run(command.split(" "))