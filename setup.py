"""
setup.py — Backward-compatible installer and cache initializer
==============================================================

"""

from setuptools import setup, find_packages
import os
from pathlib import Path
import shutil

# ═════════════════════════ User cache directory setup ═══════════════════════
base_dir = os.getenv("DATASPIDER_AI_BASE_DIRECTORY")
dataspiderai_folder = Path(base_dir) if base_dir else Path.home()
dataspiderai_folder = dataspiderai_folder / ".dataspiderai"
cache_folder = dataspiderai_folder / "cache"
content_folders = [
    "html_content",
    "cleaned_html",
    "markdown_content",
    "extracted_content",
    "screenshots",
]

if cache_folder.exists():
    shutil.rmtree(cache_folder)

dataspiderai_folder.mkdir(exist_ok=True)
cache_folder.mkdir(exist_ok=True)
for folder in content_folders:
    (dataspiderai_folder / folder).mkdir(exist_ok=True)

# ═════════════════════════ Dynamic version loading ══════════════════════════
version = "0.1.0"
try:
    with open("dataspiderai/__version__.py") as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip('"')
                break
except Exception:
    pass

# ═════════════════════════ Setup invocation ════════════════════════════════
setup(
    name="dataspiderai",
    version=version,
    description="A package for scraping economic data with multi-agents and AI.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/jorgevalverde/dataspiderai",
    author="Jorge Valverde Albelda",
    author_email="jorge.valverdealbe@example.com",
    license="MIT",
    python_requires=">=3.12",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "python-dotenv>=1.0.0",
        "langchain-openai>=0.0.1",
        "playwright>=1.35.0",
        "beautifulsoup4>=4.12.0",
        "pandas>=2.0.0",
        "pyarrow>=12.0.0",
        "tenacity>=8.2.0",
        "browser-use>=0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "dataspiderai = dataspiderai.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
