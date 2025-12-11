"""
CSV dataset processor.
"""

import pandas as pd
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

from .base import BaseProcessor


class CSVProcessor(BaseProcessor):
    """Processor for CSV files."""
    
    def read(self, **kwargs) -> pd.DataFrame:
        """
        Read CSV file into a pandas DataFrame.
        
        Args:
            **kwargs: Additional arguments passed to pd.read_csv()
                     (e.g., sep, encoding, header, index_col)
        
        Returns:
            pandas DataFrame containing the CSV data1
        """
        return pd.read_csv(self.file_path, **kwargs)
    
    def read_chunks(self, chunk_size: int = 1000, **kwargs) -> Iterator[pd.DataFrame]:
        """
        Read CSV file in chunks.
        
        Args:
            chunk_size: Number of rows per chunk
            **kwargs: Additional arguments passed to pd.read_csv()
        
        Yields:
            DataFrames containing chunks of the CSV data
        """
        for chunk in pd.read_csv(self.file_path, chunksize=chunk_size, **kwargs):
            yield chunk
    
    def get_top_n(self, n: int = 5, **kwargs) -> pd.DataFrame:
        """
        Get the top N rows from the CSV file.
        
        Args:
            n: Number of rows to return (default: 5)
            **kwargs: Additional arguments passed to pd.read_csv()
            
        Returns:
            DataFrame containing the top N rows
        """
        return pd.read_csv(self.file_path, nrows=n, **kwargs)
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the CSV file.
        
        Returns:
            Dictionary with metadata including:
            - row_count: Number of rows
            - column_count: Number of columns
            - columns: List of column names
            - file_size: File size in bytes
            - dtypes: Data types of columns
        """
        df = self.read()
        return {
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': df.columns.tolist(),
            'file_size': self.get_file_size(),
            'dtypes': df.dtypes.to_dict(),
            'file_path': str(self.file_path),
        }

