"""
CyberGuard Enterprise Security Platform
Enterprise-grade AI-powered cybersecurity with real-time threat detection
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
def read_requirements(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='cyberguard-enterprise',
    version='2.0.0',
    author='CyberGuard Security Solutions',
    author_email='support@cyberguard-platform.com',
    description='Enterprise-grade AI-powered cybersecurity platform with real-time threat detection',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/cyberguard/cyberguard-platform',
    project_urls={
        'Documentation': 'https://docs.cyberguard-platform.com',
        'Source': 'https://github.com/cyberguard/cyberguard-platform',
        'Tracker': 'https://github.com/cyberguard/cyberguard-platform/issues',
        'Website': 'https://cyberguard-platform.com',
        'Commercial': 'https://cyberguard-platform.com/pricing',
    },
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Security',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Networking :: Monitoring',
    ],
    keywords='cybersecurity threat-detection machine-learning security-automation intrusion-detection malware-detection siem soar threat-intelligence endpoint-security',
    packages=find_packages(include=['scripts', 'detection', 'intelligence', 'isolation', 'mitigation', 'prevention', 'recovery', 'response', 'orchestration']),
    python_requires='>=3.8',
    install_requires=read_requirements('requirements.txt'),
    extras_require={
        'ml': [
            'scikit-learn>=1.3.0',
            'numpy>=1.24.0',
        ],
        'analytics': [
            'reportlab>=4.0.0',
            'matplotlib>=3.7.0',
            'plotly>=5.17.0',
        ],
        'performance': [
            'redis>=5.0.0',
            'psycopg2-binary>=2.9.0',
        ],
        'enterprise': [
            'scikit-learn>=1.3.0',
            'numpy>=1.24.0',
            'reportlab>=4.0.0',
            'redis>=5.0.0',
            'psycopg2-binary>=2.9.0',
            'celery>=5.3.0',
        ],
        'all': [
            'scikit-learn>=1.3.0',
            'numpy>=1.24.0',
            'reportlab>=4.0.0',
            'redis>=5.0.0',
            'psycopg2-binary>=2.9.0',
            'celery>=5.3.0',
            'matplotlib>=3.7.0',
            'plotly>=5.17.0',
        ],
        'dev': [
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
            'black>=23.7.0',
            'flake8>=6.1.0',
            'mypy>=1.5.0',
            'sphinx>=7.1.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'cyberguard=scripts.cli:main',
            'cyberguard-monitor=scripts.active_threat_monitor:main',
            'cyberguard-dashboard=scripts.threat_dashboard:main',
            'cyberguard-api=scripts.threat_api_server:main',
            'cyberguard-ml=scripts.ml_threat_detection:main',
            'cyberguard-analytics=scripts.advanced_analytics:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.json', '*.txt', '*.md', '*.yml', '*.yaml'],
    },
    zip_safe=False,
    platforms='any',
)
