"""
General dataset processors for different file types.

This module provides processors for various dataset types including:
- CSV files
- JSON files
- JSONL files (newline-delimited JSON)
- XLSX files
- TXT files
"""

from .base import BaseProcessor
from .csv_processor import CSVProcessor
from .json_processor import JSONProcessor
from .jsonl_processor import JSONLProcessor
from .xlsx_processor import XLSXProcessor
from .txt_processor import TXTProcessor
from .factory import ProcessorFactory, get_processor

__all__ = [
    'BaseProcessor',
    'CSVProcessor',
    'JSONProcessor',
    'JSONLProcessor',
    'XLSXProcessor',
    'TXTProcessor',
    'ProcessorFactory',
    'get_processor',
]

