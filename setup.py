"""
Setup script for Threat Intelligence Platform - Unified Bundle
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="threat-intelligence-platform",
    version="1.0.0",
    author="Threat Intelligence Team",
    author_email="security@example.com",
    description="Complete threat intelligence and response platform with 7 integrated engines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourorg/threat-intelligence-platform",
    packages=find_packages(include=[
        'intelligence',
        'prevention',
        'detection',
        'response',
        'isolation',
        'mitigation',
        'recovery',
        'orchestration',
        'tests'
    ]),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "torch>=1.9.0",
        "networkx>=2.6.0",
        "neo4j>=4.4.0",
        "requests>=2.26.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
        'docs': [
            'sphinx>=4.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: System :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        'console_scripts': [
            'tip-orchestrator=orchestration.threat_platform_orchestrator:main',
            'tip-test=tests.run_all_tests:run_all_tests',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
