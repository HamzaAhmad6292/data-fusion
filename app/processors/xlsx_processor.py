"""
XLSX (Excel) dataset processor.
"""

import pandas as pd
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

from .base import BaseProcessor


class XLSXProcessor(BaseProcessor):
    """Processor for XLSX (Excel) files."""
    
    def read(self, sheet_name: Optional[str | int] = None, **kwargs) -> pd.DataFrame | Dict[str, pd.DataFrame]:
        """
        Read XLSX file into pandas DataFrame(s).
        
        Args:
            sheet_name: Name or index of sheet to read. If None, reads all sheets.
            **kwargs: Additional arguments passed to pd.read_excel()
                     (e.g., header, index_col, usecols)
        
        Returns:
            DataFrame if single sheet, or dict of DataFrames if multiple sheets
        """
        if sheet_name is not None:
            return pd.read_excel(self.file_path, sheet_name=sheet_name, **kwargs)
        else:
            # Read all sheets
            return pd.read_excel(self.file_path, sheet_name=None, **kwargs)
    
    def read_chunks(self, chunk_size: int = 1000, sheet_name: Optional[str | int] = None, **kwargs) -> Iterator[pd.DataFrame]:
        """
        Read XLSX file in chunks.
        
        Note: Excel files are loaded entirely into memory, so this reads
        the whole sheet first, then yields chunks.
        
        Args:
            chunk_size: Number of rows per chunk
            sheet_name: Name or index of sheet to read
            **kwargs: Additional arguments passed to pd.read_excel()
        
        Yields:
            DataFrames containing chunks of the Excel data
        """
        df = self.read(sheet_name=sheet_name, **kwargs)
        if isinstance(df, dict):
            # If multiple sheets, process first sheet
            df = list(df.values())[0]
        
        for i in range(0, len(df), chunk_size):
            yield df.iloc[i:i + chunk_size]
    
    def get_sheet_names(self) -> List[str]:
        """
        Get list of sheet names in the Excel file.
        
        Returns:
            List of sheet names
        """
        excel_file = pd.ExcelFile(self.file_path)
        return excel_file.sheet_names
    
    def get_metadata(self, sheet_name: Optional[str | int] = None) -> Dict[str, Any]:
        """
        Get metadata about the XLSX file.
        
        Args:
            sheet_name: Name or index of sheet to get metadata for.
                       If None, returns metadata for all sheets.
        
        Returns:
            Dictionary with metadata including:
            - sheet_names: List of sheet names
            - file_size: File size in bytes
            - sheet_metadata: Metadata for each sheet (or single sheet)
        """
        excel_file = pd.ExcelFile(self.file_path)
        sheet_names = excel_file.sheet_names
        
        metadata = {
            'sheet_names': sheet_names,
            'file_size': self.get_file_size(),
            'file_path': str(self.file_path),
        }
        
        if sheet_name is not None:
            # Metadata for specific sheet
            df = self.read(sheet_name=sheet_name)
            metadata['sheet_metadata'] = {
                'sheet_name': sheet_name if isinstance(sheet_name, str) else sheet_names[sheet_name],
                'row_count': len(df),
                'column_count': len(df.columns),
                'columns': df.columns.tolist(),
                'dtypes': df.dtypes.to_dict(),
            }
        else:
            # Metadata for all sheets
            sheet_metadata = {}
            for name in sheet_names:
                df = self.read(sheet_name=name)
                sheet_metadata[name] = {
                    'row_count': len(df),
                    'column_count': len(df.columns),
                    'columns': df.columns.tolist(),
                }
            metadata['sheet_metadata'] = sheet_metadata
        
        return metadata

