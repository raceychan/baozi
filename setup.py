import pathlib

from setuptools import find_packages, setup

PROJECT_NAME = "baozi"
PROJECT_ROOT = pathlib.Path.cwd()
URL = "https://github.com/raceychan/baozi"
VERSION = "0.0.2"

import codecs

with codecs.open(str(PROJECT_ROOT / "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

setup(
    name=PROJECT_NAME,
    version=VERSION,
    package_dir={"": "baozi"},
    url=URL,
    packages=find_packages(
        where="baozi", exclude=["tests", "*.tests", "*.tests.*", "tests.*"]
    ),
    long_description_content_type="text/markdown",
    long_description=long_description,
    author="race",
    author_email="raceychan@gmail.com",
    license="MIT",
    python_requires=">=3.11",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
