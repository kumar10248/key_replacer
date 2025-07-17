#!/usr/bin/env python3
"""
Setup script for Key Replacer application.
"""

from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="key-replacer",
    version="1.0.0",
    author="Kumar Devashish",
    author_email="kumar@example.com",
    description="A cross-platform text expansion tool for productivity",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kumar10248/key-replacer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
        "Topic :: Text Processing",
    ],
    python_requires=">=3.8",
    install_requires=[
        "keyboard>=0.13.5",
        "pyautogui>=0.9.54",
        "pygetwindow>=0.0.9",
        "pillow>=9.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.991",
        ],
    },
    entry_points={
        "console_scripts": [
            "key-replacer=keyreplacer.main:main",
        ],
        "gui_scripts": [
            "key-replacer-gui=keyreplacer.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "keyreplacer": ["assets/*", "config/*"],
    },
)
