"""
TXT (plain text) dataset processor.
"""

from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from .base import BaseProcessor


class TXTProcessor(BaseProcessor):
    """Processor for plain text files."""
    
    def read(self, encoding: str = 'utf-8', **kwargs) -> str:
        """
        Read text file as a single string.
        
        Args:
            encoding: File encoding (default: utf-8)
            **kwargs: Additional arguments (unused for text files)
        
        Returns:
            String containing the entire file content
        """
        with open(self.file_path, 'r', encoding=encoding) as f:
            return f.read()
    
    def read_lines(self, encoding: str = 'utf-8', strip: bool = True) -> Iterator[str]:
        """
        Read text file line by line.
        
        Args:
            encoding: File encoding (default: utf-8)
            strip: Whether to strip whitespace from lines
        
        Yields:
            Individual lines from the file
        """
        with open(self.file_path, 'r', encoding=encoding) as f:
            for line in f:
                yield line.strip() if strip else line
    
    def read_chunks(self, chunk_size: int = 1000, encoding: str = 'utf-8', **kwargs) -> Iterator[List[str]]:
        """
        Read text file in chunks (by lines).
        
        Args:
            chunk_size: Number of lines per chunk
            encoding: File encoding (default: utf-8)
            **kwargs: Additional arguments (unused)
        
        Yields:
            Lists of lines, each containing chunk_size lines
        """
        chunk = []
        for line in self.read_lines(encoding=encoding):
            chunk.append(line)
            if len(chunk) >= chunk_size:
                yield chunk
                chunk = []
        if chunk:
            yield chunk
    
    def read_bytes(self, chunk_size: int = 8192) -> Iterator[bytes]:
        """
        Read text file in binary chunks.
        
        Args:
            chunk_size: Number of bytes per chunk
        
        Yields:
            Byte chunks from the file
        """
        with open(self.file_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    
    def get_top_n(self, n: int = 5, encoding: str = 'utf-8', **kwargs) -> List[str]:
        """
        Get the top N lines from the text file.
        
        Args:
            n: Number of lines to return (default: 5)
            encoding: File encoding (default: utf-8)
            **kwargs: Additional arguments (unused)
            
        Returns:
            List containing the top N lines
        """
        result = []
        for i, line in enumerate(self.read_lines(encoding=encoding)):
            if i >= n:
                break
            result.append(line)
        return result
    
    def get_metadata(self, encoding: str = 'utf-8') -> Dict[str, Any]:
        """
        Get metadata about the text file.
        
        Args:
            encoding: File encoding (default: utf-8)
        
        Returns:
            Dictionary with metadata including:
            - line_count: Number of lines
            - character_count: Number of characters
            - word_count: Number of words (approximate)
            - file_size: File size in bytes
        """
        content = self.read(encoding=encoding)
        lines = content.split('\n')
        
        return {
            'line_count': len(lines),
            'character_count': len(content),
            'word_count': len(content.split()),
            'file_size': self.get_file_size(),
            'file_path': str(self.file_path),
            'encoding': encoding,
        }

