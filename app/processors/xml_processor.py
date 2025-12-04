"""
XML dataset processor.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Dict, Iterator, Optional

from .base import BaseProcessor


class XMLProcessor(BaseProcessor):
    """Processor for XML files."""
    
    def read(self, **kwargs) -> ET.Element:
        """
        Read XML file and parse it.
        
        Args:
            **kwargs: Additional arguments passed to ET.parse()
                     (e.g., parser)
        
        Returns:
            Root Element of the parsed XML tree
        """
        tree = ET.parse(self.file_path, **kwargs)
        return tree.getroot()
    
    def read_chunks(self, chunk_size: int = 1000, **kwargs) -> Iterator[ET.Element]:
        """
        Read XML file in chunks (by element).
        
        Note: XML doesn't naturally chunk, so this yields child elements
        of the root in chunks.
        
        Args:
            chunk_size: Number of child elements per chunk
            **kwargs: Additional arguments passed to ET.parse()
        
        Yields:
            Lists of Element objects
        """
        root = self.read(**kwargs)
        children = list(root)
        
        for i in range(0, len(children), chunk_size):
            yield children[i:i + chunk_size]
    
    def to_dict(self, **kwargs) -> Dict[str, Any]:
        """
        Convert XML to dictionary representation.
        
        Args:
            **kwargs: Additional arguments
        
        Returns:
            Dictionary representation of the XML
        """
        root = self.read()
        return self._element_to_dict(root)
    
    def _element_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Recursively convert XML Element to dictionary."""
        result = {}
        
        # Add attributes
        if element.attrib:
            result['@attributes'] = element.attrib
        
        # Add text content
        if element.text and element.text.strip():
            if len(element) == 0:  # Leaf node
                return element.text.strip()
            result['#text'] = element.text.strip()
        
        # Add children
        for child in element:
            child_dict = self._element_to_dict(child)
            child_tag = child.tag
            
            # Handle multiple children with same tag
            if child_tag in result:
                if not isinstance(result[child_tag], list):
                    result[child_tag] = [result[child_tag]]
                result[child_tag].append(child_dict)
            else:
                result[child_tag] = child_dict
        
        return result
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the XML file.
        
        Returns:
            Dictionary with metadata including:
            - root_tag: Root element tag name
            - child_count: Number of direct children
            - file_size: File size in bytes
            - structure: Basic structure information
        """
        root = self.read()
        children = list(root)
        
        return {
            'root_tag': root.tag,
            'child_count': len(children),
            'file_size': self.get_file_size(),
            'file_path': str(self.file_path),
            'structure': f"Root: {root.tag}, {len(children)} children",
            'attributes': root.attrib if root.attrib else None,
        }

