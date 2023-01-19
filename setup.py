"""
Setup file for the application.
"""
from setuptools import setup, find_packages

setup(
    name = "ingestion",
    version = "0.0.1",
    author = "Tomiwa Adedokun",
    author_email = "exceltadedokun@gmail.com",
    description = "A demo application created to show a data engineering project",
    keywords = "python project",
    url = "",
    packages = find_packages(),
    entry_points = {"console_scripts": [
        "ingestiond = ingest.backend:main",
    ]},
    install_requires = [
        "spacy == 3.4.4",
        "spacy-lookups-data == 1.0.3",
    ],
    extra_require = {
        "dev": [
            "pytest == 7.2.0",
        ]
    }
)