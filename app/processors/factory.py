"""
Processor factory for creating appropriate processors based on file type.
"""

from pathlib import Path
from typing import Optional

from .base import BaseProcessor
from .csv_processor import CSVProcessor
from .json_processor import JSONProcessor
from .jsonl_processor import JSONLProcessor
from .xml_processor import XMLProcessor
from .xlsx_processor import XLSXProcessor
from .txt_processor import TXTProcessor


class ProcessorFactory:
    """
    Factory class for creating dataset processors based on file extension.
    """
    
    # Mapping of file extensions to processor classes
    _processors = {
        '.csv': CSVProcessor,
        '.json': JSONProcessor,
        '.jsonl': JSONLProcessor,
        '.xml': XMLProcessor,
        '.xlsx': XLSXProcessor,
        '.xls': XLSXProcessor,  # Legacy Excel format
        '.txt': TXTProcessor,
        '.text': TXTProcessor,
    }
    
    @classmethod
    def create(cls, file_path: str | Path, file_type: Optional[str] = None) -> BaseProcessor:
        """
        Create an appropriate processor for the given file.
        
        Args:
            file_path: Path to the dataset file
            file_type: Optional file type override (e.g., '.csv', '.json').
                      If not provided, inferred from file extension.
        
        Returns:
            Appropriate processor instance
        
        Raises:
            ValueError: If file type is not supported
        """
        file_path = Path(file_path)
        
        # Determine file type
        if file_type:
            extension = file_type.lower()
            if not extension.startswith('.'):
                extension = f'.{extension}'
        else:
            extension = file_path.suffix.lower()
        
        # Get processor class
        processor_class = cls._processors.get(extension)
        if processor_class is None:
            supported = ', '.join(cls._processors.keys())
            raise ValueError(
                f"Unsupported file type: {extension}. "
                f"Supported types: {supported}"
            )
        
        return processor_class(file_path)
    
    @classmethod
    def register(cls, extension: str, processor_class: type[BaseProcessor]) -> None:
        """
        Register a custom processor for a file extension.
        
        Args:
            extension: File extension (e.g., '.csv', '.json')
            processor_class: Processor class that inherits from BaseProcessor
        """
        if not extension.startswith('.'):
            extension = f'.{extension}'
        extension = extension.lower()
        
        if not issubclass(processor_class, BaseProcessor):
            raise TypeError(
                f"Processor class must inherit from BaseProcessor, "
                f"got {processor_class.__name__}"
            )
        
        cls._processors[extension] = processor_class
    
    @classmethod
    def get_supported_types(cls) -> list[str]:
        """
        Get list of supported file extensions.
        
        Returns:
            List of supported file extensions
        """
        return list(cls._processors.keys())
    
    @classmethod
    def is_supported(cls, file_path: str | Path) -> bool:
        """
        Check if a file type is supported.
        
        Args:
            file_path: Path to the file or file extension
        
        Returns:
            True if file type is supported, False otherwise
        """
        if isinstance(file_path, Path) or '/' in str(file_path) or '\\' in str(file_path):
            extension = Path(file_path).suffix.lower()
        else:
            extension = str(file_path).lower()
            if not extension.startswith('.'):
                extension = f'.{extension}'
        
        return extension in cls._processors


def get_processor(file_path: str | Path, file_type: Optional[str] = None) -> BaseProcessor:
    """
    Convenience function to get a processor for a file.
    
    Args:
        file_path: Path to the dataset file
        file_type: Optional file type override
    
    Returns:
        Appropriate processor instance
    
    Example:
        >>> processor = get_processor('data.csv')
        >>> df = processor.read()
    """
    return ProcessorFactory.create(file_path, file_type)

