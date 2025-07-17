"""
Key Replacer - A cross-platform text expansion tool.

This package provides functionality for real-time text expansion,
allowing users to define shortcuts that automatically expand to longer text.
"""

__version__ = "1.0.0"
__author__ = "Kumar Devashish"
__email__ = "kumar@example.com"
__description__ = "A cross-platform text expansion tool for productivity"

from .core import KeyReplacer
from .gui import KeyReplacerGUI
from .config import Config

__all__ = ["KeyReplacer", "KeyReplacerGUI", "Config"]
