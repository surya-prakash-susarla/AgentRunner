from setuptools import setup, find_packages

setup(
    name="replica-llm",
    version="0.1.0",
    author="Surya Prakash Susarla",
    description="A sophisticated multi-agent orchestration system for LLMs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=[
        "typer[all]>=0.9.0",
        "rich>=13.7.0",
        "python-dotenv>=1.0.0",
        "fastmcp>=0.1.0",
        "google-generativeai>=0.3.0",
        "textual>=0.52.1",  # For the upcoming TUI
        "pydantic>=2.5.0",  # For better data validation
        "asyncio>=3.4.3",
        "aiohttp>=3.9.0",  # For async HTTP requests
        "structlog>=24.1.0",  # For better logging
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",  # For coverage reporting
            "black>=24.1.0",
            "isort>=5.13.0",
            "mypy>=1.8.0",
            "ruff>=0.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "replica-llm=src.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
