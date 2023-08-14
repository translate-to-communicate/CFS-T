from setuptools import find_packages, setup
from warnings import simplefilter

simplefilter(action='ignore', category=DeprecationWarning)

with open("README.md", "r", encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="CFS-Translation",
    version="0.0.9",
    description="An automated script to pull in calls-for-service (CFS) data and produce a "
                "single document meant for archiving and future analysis",
    package_dir={"": "app"},
    packages=find_packages(where="app"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Christopher Romeo",
    author_email="caromeo@albany.edu",
    classifiers=[
        "Programming Language :: Python 3.10",
        "Operating System :: OS Independent",
    ],
    install_requires=["pandas >= 2.0.2", "tabulate >= 0.9.0", "numpy >= 1.24.3", "sodapy >= 2.2.0",
                      "geopy >= 2.3.0", "requests >= 2.31.0", "openpyxl >= 3.1.2", "xlrd >= 2.0.1"],
    python_requires=">=3.9.0",
)
