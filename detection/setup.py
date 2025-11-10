"""
Setup script for Threat Detection Engine (Standalone)
"""

from setuptools import setup
from pathlib import Path

setup(
    name="threat-detection-engine",
    version="1.0.0",
    author="CyberGuard Industries - Lance Brady & AI Collaboration",
    author_email="lance.ceo@cyberguard-industries.com",
    description="ML-powered threat detection with signatures, behavioral analysis, and graph correlation by CyberGuard Industries",
    long_description=open("README.md").read() if Path("README.md").exists() else "",
    long_description_content_type="text/markdown",
    url="https://github.com/cyberguard-industries/threat-detection-engine",
    packages=['detection'],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "pandas>=1.3.0",
        "scikit-learn>=1.0.0",
        "torch>=1.9.0",
        "networkx>=2.6.0",
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
    keywords="threat detection, cybersecurity, machine learning, anomaly detection, cyberguard",
)
