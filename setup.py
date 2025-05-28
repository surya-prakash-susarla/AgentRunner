from setuptools import setup, find_packages

setup(
    name="replica-llm",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer[all]",
        "rich",
        "python-dotenv",
        "fastmcp",
        "google-generativeai",
    ],
    entry_points={
        "console_scripts": [
            "replica-llm=src.main:main",
        ],
    },
)
