#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for Large Test Data Generator.
"""
from setuptools import setup, find_packages

setup(
    name="large_test_data_generator",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pymongo",
    ],
    entry_points={
        "console_scripts": [
            "generate-test-data=large_test_data_generator.cli:main",
        ],
    },
    author="Vivek Maswadkar",
    author_email="",
    description="Generate CSV files for large data requirements",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lumensparkxy/LargeTestDataGenerator",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)