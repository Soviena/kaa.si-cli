from setuptools import setup, find_packages
from kaasi_cli.version import versioning
setup(
    name="kaasi-cli",
    version=versioning.ver,
    author="Soviena",
    author_email="rovino.rs@gmail.com",
    description="Stream anime from kaa.si and sync with anilist",
    packages=find_packages(),
    url="https://github.com/Soviena/kaa.si-cli",
    keywords=[
        "stream",
        "anime",
        "cli",
        "scraper",
        "anilist"
    ],
    install_requires=[
        "cloudscraper",
        "requests",
        "bs4",
        "pypresence",
        "pycryptodome",
    ],
    entry_points={
        'console_scripts': ['kaasi=kaasi_cli.kaasi:kaasi']
    }
)