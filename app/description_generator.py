"""
Description Generator for Dataset Files

This module generates column descriptions for various dataset file types using LLM,
while programmatically determining data types.
"""

import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from llm.unified_client import get_llm_client
from processors.factory import get_processor


class DescriptionGenerator:
    """Generate column descriptions for dataset files."""
    
    def __init__(self, llm_client=None):
        """
        Initialize the description generator.
        
        Args:
            llm_client: Optional LLM client instance. If not provided, creates a new one.
        """
        self.llm_client = llm_client or get_llm_client()
        
        self.system_prompt = """You are an experienced data engineer specializing in dataset analysis and documentation.

Your task is to analyze a given dataset and create comprehensive column descriptions that accurately represent what each column contains.

**Your Responsibilities:**
1. Analyze each column in the provided dataset
2. Understand the data type, format, and semantic meaning of each column
3. Create clear, concise, and accurate descriptions
4. Identify realistic examples from the data
5. Suggest similar keywords that might be used to refer to the same concept

**Output Requirements:**
- Your response MUST be valid JSON format only
- Do NOT include any explanatory text, markdown formatting, or code blocks
- Return a JSON array where each object represents one column
- Each column object must contain exactly these fields:
  - `name`: The exact column name as it appears in the dataset
  - `description`: A clear, concise description of what the column represents
  - `example`: A realistic example value from the data (use actual values when possible)
  - `similar_keywords`: An array of 3-5 alternative terms that could refer to the same concept

**Guidelines for Descriptions:**
- Be specific and accurate based on the actual data
- Use professional, clear language
- Indicate data types when relevant (e.g., "Date when...", "Numeric identifier for...")
- For date fields, note the format if apparent
- For identifiers, specify what they identify

**Example Output Format:**
[
  {
    "name": "matter_id",
    "description": "Unique identifier for the legal matter",
    "example": "MAT-1001",
    "similar_keywords": ["matter code", "case_id", "file_number"]
  },
  {
    "name": "client_ref",
    "description": "Identifier for the client associated with the matter",
    "example": "CL-1001",
    "similar_keywords": ["client code", "customer_ref", "account_id"]
  }
]

Remember: Output ONLY the JSON array, nothing else."""

        self.user_prompt_template = """Analyze the following dataset sample and provide column descriptions in the specified JSON format.

<data>
{data_sample}
</data>

Provide the column descriptions as a JSON array."""

    def _infer_data_type(self, value: Any) -> str:
        """
        Infer Python data type from a value.
        
        Args:
            value: The value to infer type from
            
        Returns:
            String representation of the data type
        """
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "str"
        elif isinstance(value, list):
            return "list"
        elif isinstance(value, dict):
            return "dict"
        else:
            return type(value).__name__


    def _get_data_types_from_dataframe(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Get data types for each column in a DataFrame.
        
        Args:
            df: pandas DataFrame
            
        Returns:
            Dictionary mapping column names to data types
        """
        dtype_map = {}
        for col in df.columns:
            dtype = df[col].dtype
            # Convert pandas dtypes to Python types
            if pd.api.types.is_integer_dtype(dtype):
                dtype_map[col] = "int"
            elif pd.api.types.is_float_dtype(dtype):
                dtype_map[col] = "float"
            elif pd.api.types.is_bool_dtype(dtype):
                dtype_map[col] = "bool"
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                dtype_map[col] = "datetime"
            elif pd.api.types.is_object_dtype(dtype):
                # Check if it's actually a string or mixed
                dtype_map[col] = "str"
            else:
                dtype_map[col] = str(dtype)
        
        return dtype_map

    def _get_data_types_from_records(self, records: List[Dict]) -> Dict[str, str]:
        """
        Get data types for each field in a list of records.
        
        Args:
            records: List of dictionaries (records)
            
        Returns:
            Dictionary mapping field names to data types
        """
        if not records:
            return {}
        
        # Collect all field names
        all_fields = set()
        for record in records:
            if isinstance(record, dict):
                all_fields.update(record.keys())
        
        dtype_map = {}
        for field in all_fields:
            # Sample values from records to infer type
            sample_values = [
                record.get(field) 
                for record in records[:10]  # Sample first 10 records
                if field in record
            ]
            
            if not sample_values:
                dtype_map[field] = "null"
                continue
            
            # Find the most common non-null type
            types = [self._infer_data_type(v) for v in sample_values if v is not None]
            if types:
                # Use the most common type, or first if all different
                dtype_map[field] = max(set(types), key=types.count) if types else "null"
            else:
                dtype_map[field] = "null"
        
        return dtype_map

    def _prepare_data_sample(self, file_path: Path, processor) -> Tuple[str, Dict[str, str]]:
        """
        Prepare data sample for LLM and get data types.
        Uses processors to read files and extracts top 5 entries.
        
        Args:
            file_path: Path to the file
            processor: Processor instance
            
        Returns:
            Tuple of (data_sample_string, data_types_dict)
        """
        file_ext = file_path.suffix.lower()
        data_types = {}
        
        if file_ext in ['.csv', '.xlsx', '.xls']:
            # Structured tabular data - use processor to read
            # For XLSX/XLS, explicitly read first sheet to avoid dict return
            if file_ext in ['.xlsx', '.xls']:
                # Get sheet names first
                if hasattr(processor, 'get_sheet_names'):
                    sheet_names = processor.get_sheet_names()
                    if sheet_names:
                        # Read first sheet explicitly to get DataFrame, not dict
                        data = processor.read(sheet_name=sheet_names[0])
                    else:
                        raise ValueError(f"XLSX file {file_path} has no sheets")
                else:
                    # Fallback: read without sheet_name, handle dict if returned
                    data = processor.read()
            else:
                # CSV files
                data = processor.read()
            
            # Handle XLSX/XLS which may return dict of DataFrames (multiple sheets)
            # This can happen if sheet_name wasn't specified in the read() call
            if isinstance(data, dict):
                # Multiple sheets - use the first sheet
                if not data:
                    raise ValueError(f"XLSX file {file_path} has no sheets")
                sheet_name = list(data.keys())[0]
                df = data[sheet_name]
                if not isinstance(df, pd.DataFrame):
                    raise ValueError(f"Expected DataFrame from sheet '{sheet_name}', got {type(df)}")
            elif isinstance(data, pd.DataFrame):
                # Single DataFrame (CSV or single sheet XLSX)
                df = data
            else:
                raise ValueError(f"Unexpected data type from {file_ext} file: {type(data)}. Expected DataFrame or dict of DataFrames.")
            
            # Verify df is a DataFrame before calling head()
            if not isinstance(df, pd.DataFrame):
                raise ValueError(f"Expected DataFrame, got {type(df)}")
            
            # Get top 5 rows as sample
            sample_df = df.head(5)
            data_sample = sample_df.to_json(orient="records", indent=2)
            # Get data types from full dataframe
            data_types = self._get_data_types_from_dataframe(df)
            
        elif file_ext == '.jsonl':
            # JSONL data - use processor to read (returns list of dicts)
            data = processor.read()
            # Get top 5 entries
            sample_records = data[:5] if len(data) > 5 else data
            data_sample = json.dumps(sample_records, indent=2)
            # Get data types from all records
            data_types = self._get_data_types_from_records(data)
            
        elif file_ext == '.json':
            # JSON data - use processor to read
            data = processor.read()
            if isinstance(data, list):
                # List of records - get top 5 entries
                sample_records = data[:5] if len(data) > 5 else data
                data_sample = json.dumps(sample_records, indent=2)
                # Get data types from all records
                data_types = self._get_data_types_from_records(data)
            elif isinstance(data, dict):
                # Single object or nested structure
                data_sample = json.dumps(data, indent=2)
                # For dict, try to infer types from values
                if data:
                    data_types = {k: self._infer_data_type(v) for k, v in data.items()}
            else:
                data_sample = json.dumps(data, indent=2)
                
        elif file_ext in ['.txt', '.text']:
            # Text file - use processor to read lines
            lines = list(processor.read_lines())[:5]  # Get top 5 lines
            data_sample = '\n'.join(lines)
            # Text files don't have structured columns, so no data types
            
        else:
            # Unknown type - try to use processor if it has read method
            try:
                data = processor.read()
                if isinstance(data, (list, dict)):
                    if isinstance(data, list):
                        sample_data = data[:5] if len(data) > 5 else data
                    else:
                        sample_data = data
                    data_sample = json.dumps(sample_data, indent=2)
                else:
                    data_sample = str(data)
            except:
                # Fallback: read as text using processor
                if hasattr(processor, 'read_lines'):
                    lines = list(processor.read_lines())[:5]
                    data_sample = '\n'.join(lines)
                else:
                    # Last resort: read file directly
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()[:5]
                        data_sample = ''.join(lines)
        
        return data_sample, data_types

    def _extract_json_from_response(self, response: str) -> List[Dict]:
        """
        Extract JSON array from LLM response, handling markdown code blocks.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed JSON as list of dictionaries
        """
        # Try to parse directly
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code blocks
        json_patterns = [
            r'```(?:json)?\s*(\[[\s\S]*?\])',  # JSON in code block
            r'```\s*(\[[\s\S]*?\])',  # JSON in generic code block
            r'(\[[\s\S]*?\])',  # Any JSON array
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, response, re.MULTILINE | re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue
        
        raise ValueError(f"Could not extract valid JSON from LLM response: {response[:200]}")

    def generate(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Generate column descriptions for a dataset file.
        
        Args:
            file_path: Path to the dataset file
            
        Returns:
            Dictionary containing:
            - filename: Name of the input file
            - columns: List of column descriptions with name, description, example, 
                      similar_keywords, and data_type
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get appropriate processor
        processor = get_processor(file_path)
        
        # Prepare data sample and get data types
        data_sample, data_types = self._prepare_data_sample(file_path, processor)
        
        # Prepare user prompt
        user_prompt = self.user_prompt_template.format(data_sample=data_sample)
        
        # Get LLM response with retry logic for rate limiting
        max_retries = 3
        retry_delay = 2  # Start with 2 seconds
        
        for attempt in range(max_retries):
            try:
                response = self.llm_client.generate(
                    prompt=user_prompt,
                    system_prompt=self.system_prompt,
                    temperature=0.3,
                    max_tokens=2000
                )
                break  # Success, exit retry loop
            except Exception as e:
                error_str = str(e)
                # Check if it's a rate limit error (429 or 413)
                is_rate_limit = (
                    '429' in error_str or 
                    '413' in error_str or 
                    'rate_limit' in error_str.lower() or
                    'too many requests' in error_str.lower() or
                    'request too large' in error_str.lower()
                )
                
                if is_rate_limit and attempt < max_retries - 1:
                    # Extract wait time from error if available
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    
                    # Try to extract suggested wait time from error message
                    wait_match = re.search(r'try again in (\d+)ms', error_str, re.IGNORECASE)
                    if wait_match:
                        wait_time = int(wait_match.group(1)) / 1000  # Convert ms to seconds
                        wait_time = max(wait_time, 1)  # At least 1 second
                    
                    print(f"Rate limit hit, waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                else:
                    # Not a rate limit error or out of retries
                    raise
        
        # Parse LLM response
        llm_descriptions = self._extract_json_from_response(response)
        
        # Combine LLM descriptions with programmatically determined data types
        columns = []
        for col_desc in llm_descriptions:
            col_name = col_desc.get('name', '')
            # Add data type if available
            col_desc['data_type'] = data_types.get(col_name, 'unknown')
            columns.append(col_desc)
        
        # Build final output
        result = {
            'filename': file_path.name,
            'file_path': str(file_path),
            'columns': columns
        }
        
        return result

    def generate_to_file(
        self, 
        file_path: Union[str, Path], 
        output_path: Optional[Union[str, Path]] = None
    ) -> Path:
        """
        Generate descriptions and save to JSON file.
        
        Args:
            file_path: Path to the input dataset file
            output_path: Optional path for output JSON file. 
                        If not provided, uses input filename with .json extension.
        
        Returns:
            Path to the output file
        """
        result = self.generate(file_path)
        
        # Determine output path
        if output_path is None:
            input_path = Path(file_path)
            output_path = input_path.parent / f"{input_path.stem}_descriptions.json"
        else:
            output_path = Path(output_path)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        return output_path


def generate_description(
    file_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    llm_client=None
) -> Dict[str, Any]:
    """
    Convenience function to generate column descriptions.
    
    Args:
        file_path: Path to the dataset file
        output_path: Optional path to save JSON output
        llm_client: Optional LLM client instance
    
    Returns:
        Dictionary with filename and column descriptions
    
    Example:
        >>> result = generate_description('data/matters_A.csv')
        >>> print(result['filename'])
        >>> print(result['columns'])
    """
    generator = DescriptionGenerator(llm_client=llm_client)
    
    if output_path:
        generator.generate_to_file(file_path, output_path)
        return generator.generate(file_path)
    else:
        return generator.generate(file_path)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python description_generator.py <file_path> [output_path]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = generate_description(input_file, output_file)
    print(json.dumps(result, indent=2))

