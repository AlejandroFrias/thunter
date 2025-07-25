from setuptools import find_packages
from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="thunter",
    version="1.0.0",
    author="Alejandro Frias",
    author_email="joker454@gmail.com",
    description="A CLI To Do list w/ time tracking.",
    long_description=long_description,
    url="https://github.com/AlejandroFrias/thunter",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Intended Audience :: Developers",
        "Environment :: Console",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        "console_scripts": [
            "thunter = thunter.cli:main",
        ],
    },
    install_requires=[
        "typer",
        "rich",
        "parsimonious",
    ],
)
