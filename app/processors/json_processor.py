"""
JSON dataset processor.
"""

import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from .base import BaseProcessor


class JSONProcessor(BaseProcessor):
    """Processor for JSON files."""
    
    def read(self, **kwargs) -> Any:
        """
        Read JSON file.
        
        Args:
            **kwargs: Additional arguments passed to json.load()
                     (e.g., encoding, object_hook)
        
        Returns:
            Parsed JSON data (dict, list, or other JSON-serializable type)
        """
        encoding = kwargs.pop('encoding', 'utf-8')
        with open(self.file_path, 'r', encoding=encoding) as f:
            return json.load(f, **kwargs)
    
    def read_chunks(self, chunk_size: int = 1000, **kwargs) -> Iterator[Any]:
        """
        Read JSON file in chunks (for array-based JSON).
        
        Args:
            chunk_size: Number of items per chunk (only applies to arrays)
            **kwargs: Additional arguments passed to json.load()
        
        Yields:
            Chunks of the JSON data (if it's an array)
        """
        data = self.read(**kwargs)
        if isinstance(data, list):
            for i in range(0, len(data), chunk_size):
                yield data[i:i + chunk_size]
        else:
            # For non-array JSON, yield the whole thing
            yield data
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the JSON file.
        
        Returns:
            Dictionary with metadata including:
            - data_type: Type of root JSON element (dict, list, etc.)
            - item_count: Number of items (if array) or keys (if dict)
            - file_size: File size in bytes
            - structure: Basic structure information
        """
        data = self.read()
        metadata = {
            'data_type': type(data).__name__,
            'file_size': self.get_file_size(),
            'file_path': str(self.file_path),
        }
        
        if isinstance(data, list):
            metadata['item_count'] = len(data)
            if len(data) > 0:
                metadata['structure'] = f"Array of {type(data[0]).__name__}s"
        elif isinstance(data, dict):
            metadata['item_count'] = len(data)
            metadata['structure'] = f"Object with keys: {', '.join(list(data.keys())[:5])}"
            if len(data) > 5:
                metadata['structure'] += "..."
        else:
            metadata['item_count'] = 1
            metadata['structure'] = f"Single {type(data).__name__}"
        
        return metadata

