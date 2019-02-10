import os

from setuptools import setup, find_packages

cwd = os.path.dirname(os.path.realpath(__file__))

with open("{}/requirements.txt".format(cwd), "r") as f:
    deps = f.readlines()

setup(
    name="broadway-man",
    version="0.1",
    packages=[ "broadway/man" ],
    install_requires=deps
)
