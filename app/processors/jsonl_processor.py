"""
JSONL (newline-delimited JSON) dataset processor.
"""

import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from .base import BaseProcessor


class JSONLProcessor(BaseProcessor):
    """Processor for JSONL (newline-delimited JSON) files."""
    
    def read(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Read JSONL file into a list of dictionaries.
        
        Args:
            **kwargs: Additional arguments (e.g., encoding)
        
        Returns:
            List of dictionaries, one per line
        """
        encoding = kwargs.pop('encoding', 'utf-8')
        result = []
        with open(self.file_path, 'r', encoding=encoding) as f:
            for line in f:
                line = line.strip()
                if line:
                    result.append(json.loads(line))
        return result
    
    def read_chunks(self, chunk_size: int = 1000, **kwargs) -> Iterator[List[Dict[str, Any]]]:
        """
        Read JSONL file in chunks.
        
        Args:
            chunk_size: Number of lines per chunk
            **kwargs: Additional arguments (e.g., encoding)
        
        Yields:
            Lists of dictionaries, each containing chunk_size items
        """
        encoding = kwargs.pop('encoding', 'utf-8')
        chunk = []
        with open(self.file_path, 'r', encoding=encoding) as f:
            for line in f:
                line = line.strip()
                if line:
                    chunk.append(json.loads(line))
                    if len(chunk) >= chunk_size:
                        yield chunk
                        chunk = []
            if chunk:
                yield chunk
    
    def read_lines(self) -> Iterator[Dict[str, Any]]:
        """
        Read JSONL file line by line (memory efficient).
        
        Yields:
            One dictionary per line
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)
    
    def get_top_n(self, n: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Get the top N records from the JSONL file.
        
        Args:
            n: Number of records to return (default: 5)
            **kwargs: Additional arguments (e.g., encoding)
            
        Returns:
            List containing the top N dictionaries
        """
        encoding = kwargs.pop('encoding', 'utf-8')
        result = []
        with open(self.file_path, 'r', encoding=encoding) as f:
            for i, line in enumerate(f):
                if i >= n:
                    break
                line = line.strip()
                if line:
                    result.append(json.loads(line))
        return result
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the JSONL file.
        
        Returns:
            Dictionary with metadata including:
            - line_count: Number of non-empty lines
            - file_size: File size in bytes
            - sample_keys: Keys from the first record (if available)
        """
        line_count = 0
        sample_keys = None
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    line_count += 1
                    if sample_keys is None:
                        try:
                            first_record = json.loads(line)
                            if isinstance(first_record, dict):
                                sample_keys = list(first_record.keys())
                        except json.JSONDecodeError:
                            pass
        
        return {
            'line_count': line_count,
            'file_size': self.get_file_size(),
            'file_path': str(self.file_path),
            'sample_keys': sample_keys,
        }

