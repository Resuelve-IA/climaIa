"""
Script de instalación para el proyecto de Análisis Climático de Cundinamarca.
"""

from setuptools import setup, find_packages
import os

# Leer el README
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Leer requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="clima-cundinamarca",
    version="1.0.0",
    author="Equipo de Desarrollo",
    author_email="desarrollo@example.com",
    description="Sistema de análisis climático para Cundinamarca con datos del IDEAM",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/usuario/clima-cundinamarca",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "clima-api=backend.main:run_app",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    keywords="climate analysis, meteorology, IDEAM, Cundinamarca, Colombia",
    project_urls={
        "Bug Reports": "https://github.com/usuario/clima-cundinamarca/issues",
        "Source": "https://github.com/usuario/clima-cundinamarca",
        "Documentation": "https://clima-cundinamarca.readthedocs.io/",
    },
) 