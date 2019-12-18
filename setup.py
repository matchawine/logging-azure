#!/usr/bin/env python

from os import path
from io import open
from setuptools import setup, find_packages
from logging_azure import get_version

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

if __name__ == "__main__":
    setup(
        name="logging-azure",
        version=get_version(),
        description="A python async logging handler and service extension for Azure Log Workspace OMS.",
        long_description=LONG_DESCRIPTION,
        author="Joshua Logan",
        author_email="joshua@matcha.wine",
        url="https://github.com/matchawine/logging-azure",
        packages=find_packages(),
        license="GPL",
        keywords="utils",
        python_requires=">=3.7",
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Environment :: Plugins",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: GNU General Public License (GPL)",
            "Operating System :: OS Independent",
            "Natural Language :: English",
            "Programming Language :: Python :: 3.7",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        install_requires=["injector>=0.18.2", "cython>=0.29.14", "grequests>=0.4.0"],
    )
