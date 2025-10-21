#!/usr/bin/env python3
"""CLI entry point for the Obsidian MCP Server."""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from obsidian_mcp.logging_setup import setup_logging


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="mcp-obsidian",
        description="MCP Server for Obsidian vaults - read, write, search, organize and analyze your notes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start server with specific vault
  mcp-obsidian --vault /path/to/your/vault
  
  # Use environment variable for vault path
  export OBSIDIAN_VAULT_PATH=/path/to/your/vault
  mcp-obsidian
  
  # Enable watch mode for real-time updates
  mcp-obsidian --vault /path/to/vault --watch
  
  # Custom configuration file
  mcp-obsidian --vault /path/to/vault --config /path/to/config.yaml
  
  # Debug mode with verbose logging
  mcp-obsidian --vault /path/to/vault --log-level DEBUG

Environment Variables:
  OBSIDIAN_VAULT_PATH     Default vault path
  OBSIDIAN_MCP_CONFIG     Default configuration file path  
  OBSIDIAN_MCP_LOG_LEVEL  Default logging level (DEBUG, INFO, WARNING, ERROR)
        """,
    )
    
    # Vault configuration
    parser.add_argument(
        "--vault",
        type=str,
        help="Path to Obsidian vault (overrides OBSIDIAN_VAULT_PATH env var)",
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (overrides OBSIDIAN_MCP_CONFIG env var)",
    )
    
    # Server options
    parser.add_argument(
        "--watch",
        action="store_true", 
        help="Enable watch mode for real-time vault updates (requires watchdog package)",
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=os.environ.get("OBSIDIAN_MCP_LOG_LEVEL", "INFO"),
        help="Logging level (default: INFO)",
    )
    
    # Development options
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Enable dry-run mode by default for destructive operations",
    )
    
    return parser.parse_args()


def validate_vault_path(vault_path: Optional[str]) -> Path:
    """Validate and return the vault path."""
    if not vault_path:
        # Try environment variable
        vault_path = os.environ.get("OBSIDIAN_VAULT_PATH")
    
    if not vault_path:
        print("Error: No vault path specified.", file=sys.stderr)
        print("Use --vault /path/to/vault or set OBSIDIAN_VAULT_PATH environment variable.", file=sys.stderr)
        sys.exit(1)
    
    vault_path_obj = Path(vault_path).resolve()
    
    if not vault_path_obj.exists():
        print(f"Error: Vault path does not exist: {vault_path_obj}", file=sys.stderr)
        sys.exit(1)
        
    if not vault_path_obj.is_dir():
        print(f"Error: Vault path is not a directory: {vault_path_obj}", file=sys.stderr)
        sys.exit(1)
    
    return vault_path_obj


def main() -> None:
    """Main CLI entry point."""
    args = parse_args()
    
    # Validate vault path early
    vault_path = validate_vault_path(args.vault)
    
    # Setup logging
    setup_logging(
        level=getattr(logging, args.log_level),
        vault_path=vault_path,
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Obsidian MCP Server")
    logger.info(f"Vault path: {vault_path}")
    logger.info(f"Watch mode: {'enabled' if args.watch else 'disabled'}")
    
    # Check optional dependencies
    if args.watch:
        try:
            import watchdog  # noqa
        except ImportError:
            logger.error("Watch mode requires watchdog package. Install with: uv add watchdog")
            sys.exit(1)
    
    # Import and start the server
    try:
        from obsidian_mcp.server import create_server
        
        server = create_server(
            vault_path=vault_path,
            config_path=args.config,
            watch_mode=args.watch,
            dry_run_default=args.dry_run,
        )
        
        logger.info("Server initialized, starting MCP protocol handler...")
        server.run()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()