from setuptools import find_packages, setup

PROJECT_NAME="domino"

setup(
    name=PROJECT_NAME,
    version="0.0.1",
    package_dir={"":"src"}, 
    packages=find_packages(where="src"),
    author="race",
    author_email="raceychan@gmail.com",
    license="MIT",
    python_requires=">=3.11"
)
