"""Logging configuration for the Obsidian MCP Server."""

import logging
import sys
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.traceback import install
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def setup_logging(
    level: int = logging.INFO,
    vault_path: Optional[Path] = None,
    use_rich: bool = True,
) -> None:
    """Setup logging with optional rich formatting and file output.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        vault_path: Path to vault for log file location  
        use_rich: Whether to use rich formatting (if available)
    """
    # Clear any existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Configure root logger
    root_logger.setLevel(level)
    
    # Console handler with rich formatting if available
    if use_rich and RICH_AVAILABLE:
        # Install rich traceback handler
        install(show_locals=level <= logging.DEBUG)
        
        console = Console(stderr=True)
        console_handler = RichHandler(
            console=console,
            show_path=level <= logging.DEBUG,
            show_time=True,
            rich_tracebacks=True,
            tracebacks_show_locals=level <= logging.DEBUG,
        )
        console_handler.setLevel(level)
    else:
        # Fallback to standard handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)
        
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)
    
    # File handler if vault path is provided
    if vault_path:
        log_file = vault_path / ".obsidian-mcp.log"
        try:
            file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)  # Always debug level in file
            
            file_formatter = logging.Formatter(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
            
            # Log the log file location at INFO level
            logger = logging.getLogger(__name__)
            logger.info(f"Logging to file: {log_file}")
            
        except Exception as e:
            # Don't fail if we can't create log file, just warn
            logger = logging.getLogger(__name__)  
            logger.warning(f"Could not create log file {log_file}: {e}")
    
    # Set specific logger levels to reduce noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("mcp").setLevel(logging.INFO if level <= logging.INFO else level)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.debug(f"Logging configured - level: {logging.getLevelName(level)}")
    logger.debug(f"Rich formatting: {'enabled' if use_rich and RICH_AVAILABLE else 'disabled'}")