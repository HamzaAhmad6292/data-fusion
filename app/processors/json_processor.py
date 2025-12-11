"""
JSON dataset processor.
"""

import ijson
import json
from collections import defaultdict
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
    
    def get_top_n(self, n: int = 5, **kwargs) -> Dict[str, List[Any]]:
        """
        Stream a JSON file and collect the first N values for every unique field path.
        This is memory-efficient for large JSON files as it doesn't load the entire file.
        
        Args:
            n: Number of sample values to collect per field path (default: 5)
            **kwargs: Additional arguments (unused, kept for compatibility)
            
        Returns:
            Dictionary mapping field paths to lists of sample values:
            {'path.to.key': [val1, val2, val3, ...]}
        """
        samples = defaultdict(list)
        
        with open(self.file_path, 'rb') as f:
            # ijson.parse yields (prefix, event, value)
            # prefix = the path (e.g., "item.address.city")
            # event = type of token (start_map, string, number, etc.)
            # value = the actual data
            parser = ijson.parse(f)
            
            for prefix, event, value in parser:
                # We only care about scalar values (strings, numbers, booleans)
                # We skip structural events like 'start_map', 'end_array'
                if event in ('string', 'number', 'boolean'):
                    # If we haven't collected N samples for this specific key yet...
                    if len(samples[prefix]) < n:
                        samples[prefix].append(value)
        
        return dict(samples)
    
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

