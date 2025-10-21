"""Utility functions for the Obsidian MCP Server."""

import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, Union

import chardet
from filelock import FileLock
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INVALID_PARAMS, INTERNAL_ERROR


def safe_join(vault_root: Path, relative_path: str) -> Path:
    """Safely join a relative path to vault root, preventing path traversal.
    
    Args:
        vault_root: Root directory of the vault
        relative_path: Relative path to join (may contain .. or other path components)
        
    Returns:
        Absolute path within vault root
        
    Raises:
        McpError: If the resulting path would be outside vault root
    """
    try:
        # Normalize the relative path and resolve any .. components
        vault_root = vault_root.resolve()
        
        # Handle absolute paths by making them relative
        if os.path.isabs(relative_path):
            # Strip leading slash to make it relative
            relative_path = relative_path.lstrip(os.sep).lstrip("/")
        
        # Join and resolve the path
        result_path = (vault_root / relative_path).resolve()
        
        # Ensure the result is within vault_root
        try:
            result_path.relative_to(vault_root)
        except ValueError:
            raise McpError(
                ErrorData(
                    INVALID_PARAMS,
                    f"Path '{relative_path}' would escape vault root: {vault_root}"
                )
            ) from None
            
        return result_path
        
    except Exception as e:
        if isinstance(e, McpError):
            raise
        raise McpError(
            ErrorData(INTERNAL_ERROR, f"Path validation error: {str(e)}")
        ) from e


@contextmanager
def with_file_lock(file_path: Path, timeout: float = 10.0) -> Generator[None, None, None]:
    """Context manager for file locking to prevent concurrent access.
    
    Args:
        file_path: Path to the file to lock
        timeout: Timeout in seconds for acquiring the lock
        
    Raises:
        McpError: If lock cannot be acquired within timeout
    """
    lock_path = file_path.with_suffix(file_path.suffix + ".lock")
    lock = FileLock(lock_path, timeout=timeout)
    
    try:
        with lock:
            yield
    except TimeoutError:
        raise McpError(
            ErrorData(
                INTERNAL_ERROR,
                f"Could not acquire file lock for {file_path} within {timeout}s"
            )
        ) from None
    except Exception as e:
        raise McpError(
            ErrorData(INTERNAL_ERROR, f"File locking error: {str(e)}")
        ) from e


def atomic_write(file_path: Path, content: str, encoding: str = "utf-8") -> None:
    """Atomically write content to a file using a temporary file and rename.
    
    Args:
        file_path: Target file path
        content: Content to write
        encoding: File encoding (default: utf-8)
        
    Raises:
        McpError: If write operation fails
    """
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to temporary file in the same directory
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding=encoding,
            dir=file_path.parent,
            prefix=f".tmp_{file_path.name}_",
            suffix=".tmp",
            delete=False,
        ) as tmp_file:
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)
        
        # Atomic rename
        tmp_path.replace(file_path)
        
    except Exception as e:
        # Clean up temp file if it exists
        if 'tmp_path' in locals() and tmp_path.exists():
            try:
                tmp_path.unlink()
            except Exception:
                pass
                
        raise McpError(
            ErrorData(INTERNAL_ERROR, f"Failed to write file {file_path}: {str(e)}")
        ) from e


def read_text_autodetect(file_path: Path) -> str:
    """Read text file with automatic encoding detection.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        File content as string
        
    Raises:
        McpError: If file cannot be read
    """
    try:
        # Read raw bytes
        with open(file_path, "rb") as f:
            raw_data = f.read()
        
        if not raw_data:
            return ""
        
        # Detect encoding
        encoding_info = chardet.detect(raw_data)
        encoding = encoding_info.get("encoding", "utf-8")
        
        # Fallback encodings if detection fails
        if not encoding:
            encoding = "utf-8"
        
        # Try to decode
        try:
            content = raw_data.decode(encoding)
        except UnicodeDecodeError:
            # Fallback to utf-8 with error handling
            content = raw_data.decode("utf-8", errors="replace")
        
        return content
        
    except Exception as e:
        raise McpError(
            ErrorData(INTERNAL_ERROR, f"Failed to read file {file_path}: {str(e)}")
        ) from e


def to_json(data: Any, indent: int = 2) -> str:
    """Convert data to formatted JSON string.
    
    Args:
        data: Data to serialize
        indent: JSON indentation
        
    Returns:
        JSON string
    """
    try:
        return json.dumps(data, indent=indent, ensure_ascii=False, default=str)
    except Exception as e:
        return json.dumps({"error": f"Serialization failed: {str(e)}"}, indent=indent)


def to_yaml(data: Any) -> str:
    """Convert data to YAML string using ruamel.yaml.
    
    Args:
        data: Data to serialize
        
    Returns:
        YAML string
    """
    try:
        from ruamel.yaml import YAML
        from io import StringIO
        
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)
        
        stream = StringIO()
        yaml.dump(data, stream)
        return stream.getvalue()
        
    except Exception as e:
        return f"# YAML serialization failed: {str(e)}\n"


def parse_yaml(content: str) -> Dict[str, Any]:
    """Parse YAML content using ruamel.yaml.
    
    Args:
        content: YAML content as string
        
    Returns:
        Parsed data as dictionary
        
    Raises:
        McpError: If YAML parsing fails
    """
    try:
        from ruamel.yaml import YAML
        
        yaml = YAML()
        yaml.preserve_quotes = True
        
        # Handle empty content
        if not content.strip():
            return {}
        
        data = yaml.load(content)
        return data if isinstance(data, dict) else {}
        
    except Exception as e:
        raise McpError(
            ErrorData(INVALID_PARAMS, f"YAML parsing error: {str(e)}")
        ) from e


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to append when truncating
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    truncate_at = max_length - len(suffix)
    if truncate_at <= 0:
        return suffix[:max_length]
        
    return text[:truncate_at] + suffix