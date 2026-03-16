"""
File utility functions for WebScanPro.

This module provides helper functions for file operations such as reading and writing files,
managing directories, and handling file paths.
"""

import os
import json
import yaml
import logging
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

# Set up logger
logger = logging.getLogger('webscanpro.file_utils')

def ensure_directory_exists(directory: str) -> None:
    """
    Ensure that a directory exists. If it doesn't exist, create it.
    
    Args:
        directory: Path to the directory
    """
    try:
        os.makedirs(directory, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create directory {directory}: {e}")
        raise

def read_file(file_path: str) -> str:
    """
    Read the contents of a text file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        str: Contents of the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise

def read_lines(file_path: str) -> List[str]:
    """
    Read all lines from a text file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        List[str]: List of lines in the file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise

def write_file(file_path: str, content: str, mode: str = 'w') -> None:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        mode: File mode ('w' for write, 'a' for append, etc.)
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)
    except IOError as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        raise

def read_json(file_path: str) -> Union[Dict, List]:
    """
    Read and parse a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Union[Dict, List]: Parsed JSON data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in file {file_path}: {e}")
        raise
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except IOError as e:
        logger.error(f"Error reading JSON file {file_path}: {e}")
        raise

def write_json(file_path: str, data: Any, indent: int = 4) -> None:
    """
    Write data to a JSON file.
    
    Args:
        file_path: Path to the JSON file
        data: Data to write (must be JSON serializable)
        indent: Number of spaces for indentation
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
    except TypeError as e:
        logger.error(f"Data not JSON serializable: {e}")
        raise
    except IOError as e:
        logger.error(f"Error writing JSON file {file_path}: {e}")
        raise

def read_yaml(file_path: str) -> Union[Dict, List]:
    """
    Read and parse a YAML file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Union[Dict, List]: Parsed YAML data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in file {file_path}: {e}")
        raise
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except IOError as e:
        logger.error(f"Error reading YAML file {file_path}: {e}")
        raise

def write_yaml(file_path: str, data: Any) -> None:
    """
    Write data to a YAML file.
    
    Args:
        file_path: Path to the YAML file
        data: Data to write (must be YAML serializable)
    """
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
    except yaml.YAMLError as e:
        logger.error(f"Error serializing data to YAML: {e}")
        raise
    except IOError as e:
        logger.error(f"Error writing YAML file {file_path}: {e}")
        raise

def get_file_extension(file_path: str) -> str:
    """
    Get the file extension from a file path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: File extension (with leading dot), or empty string if no extension
    """
    return os.path.splitext(file_path)[1].lower()

def get_file_name(file_path: str, with_extension: bool = True) -> str:
    """
    Get the file name from a file path.
    
    Args:
        file_path: Path to the file
        with_extension: Whether to include the file extension
        
    Returns:
        str: File name
    """
    base_name = os.path.basename(file_path)
    if not with_extension:
        base_name = os.path.splitext(base_name)[0]
    return base_name

def find_files(directory: str, extension: str = None, recursive: bool = True) -> List[str]:
    """
    Find files in a directory with optional filtering by extension.
    
    Args:
        directory: Directory to search in
        extension: File extension to filter by (e.g., '.txt')
        recursive: Whether to search recursively in subdirectories
        
    Returns:
        List[str]: List of file paths matching the criteria
    """
    if not os.path.isdir(directory):
        logger.error(f"Directory not found: {directory}")
        return []
    
    matched_files = []
    
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                if not extension or file.lower().endswith(extension.lower()):
                    matched_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and (not extension or file.lower().endswith(extension.lower())):
                matched_files.append(file_path)
    
    return matched_files

# Example usage
if __name__ == "__main__":
    # Test the file utilities
    test_dir = os.path.join(os.path.dirname(__file__), "test_files")
    os.makedirs(test_dir, exist_ok=True)
    
    # Test writing and reading a text file
    test_file = os.path.join(test_dir, "test.txt")
    write_file(test_file, "Hello, World!")
    print(f"Read from text file: {read_file(test_file)}")
    
    # Test writing and reading a JSON file
    test_json = os.path.join(test_dir, "test.json")
    data = {"key": "value", "list": [1, 2, 3]}
    write_json(test_json, data)
    print(f"Read from JSON file: {read_json(test_json)}")
    
    # Test finding files
    print(f"Found files: {find_files(test_dir, '.txt')}")
