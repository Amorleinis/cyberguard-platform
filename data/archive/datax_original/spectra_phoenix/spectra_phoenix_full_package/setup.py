from setuptools import setup, find_packages

setup(
    name='spectra_phoenix_producer',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'confluent-kafka',
        'pydantic',
    ],
    entry_points={
        'console_scripts': [
            'spectra-producer = spectra_phoenix_producer.cli:main',
        ],
    },
    author="Your Name",
    description="Spectra Phoenix Kafka event producer CLI with schema validation and interactive editing",
    python_requires='>=3.8',
)
