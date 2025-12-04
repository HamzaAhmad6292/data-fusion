"""
Base processor class for all dataset processors.

This provides a common interface for processing different types of datasets.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Iterator, Optional


class BaseProcessor(ABC):
    """
    Abstract base class for all dataset processors.
    
    All processors should inherit from this class and implement
    the required methods for reading and processing data.
    """
    
    def __init__(self, file_path: str | Path):
        """
        Initialize the processor with a file path.
        
        Args:
            file_path: Path to the dataset file
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")
    
    @abstractmethod
    def read(self, **kwargs) -> Any:
        """
        Read the dataset from the file.
        
        Args:
            **kwargs: Additional arguments specific to the processor type
            
        Returns:
            The dataset in its native format (e.g., DataFrame, dict, list)
        """
        pass
    
    @abstractmethod
    def read_chunks(self, chunk_size: int = 1000, **kwargs) -> Iterator[Any]:
        """
        Read the dataset in chunks (for large files).
        
        Args:
            chunk_size: Number of records per chunk
            **kwargs: Additional arguments specific to the processor type
            
        Yields:
            Chunks of the dataset
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the dataset.
        
        Returns:
            Dictionary containing metadata (e.g., row count, columns, file size)
        """
        pass
    
    def validate(self) -> bool:
        """
        Validate that the file can be processed.
        
        Returns:
            True if file is valid, False otherwise
        """
        return self.file_path.exists() and self.file_path.is_file()
    
    def get_file_size(self) -> int:
        """Get the file size in bytes."""
        return self.file_path.stat().st_size
    
    def get_file_extension(self) -> str:
        """Get the file extension."""
        return self.file_path.suffix.lower()

