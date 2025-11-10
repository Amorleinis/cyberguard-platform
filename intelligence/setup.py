"""
Setup script for Threat Intelligence Engine (Standalone)
"""

from setuptools import setup, find_packages
from pathlib import Path

setup(
    name="threat-intelligence-engine",
    version="1.0.0",
    author="CyberGuard Industries - Lance Brady & AI Collaboration",
    author_email="lance.ceo@cyberguard-industries.com",
    description="CVE analysis, threat actor profiling, and IOC extraction engine by CyberGuard Industries",
    long_description=open("README.md").read() if Path("README.md").exists() else "",
    long_description_content_type="text/markdown",
    url="https://github.com/cyberguard-industries/threat-intelligence-engine",
    py_modules=['threat_intelligence_engine'],
    python_requires=">=3.8",
    install_requires=[
        "neo4j>=4.4.0",
        "requests>=2.26.0",
        "python-dateutil>=2.8.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    license="Apache 2.0",
    keywords="threat intelligence, cybersecurity, cve, vulnerability analysis, cyberguard",
)
