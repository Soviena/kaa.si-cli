from setuptools import setup, find_packages

setup(
    name="kaa.si-cli",
    version="1.0.0",
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
    entry_points="""
        [console_scripts]
        kaasi=kaasi.py
    """,
)