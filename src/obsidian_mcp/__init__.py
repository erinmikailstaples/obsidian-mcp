"""Obsidian MCP Server - A comprehensive MCP server for Obsidian vaults.

This package provides a Model Context Protocol (MCP) server that enables AI assistants
and other MCP clients to interact with Obsidian vaults. It supports reading, writing,
searching, organizing, and analyzing markdown notes and their metadata.

Key features:
- Universal vault compatibility 
- Safe file operations with confirmations and dry-run modes
- Advanced search (text, tags, metadata, dates)
- Link management and resolution
- Organizational tools (MOCs, bulk operations)
- Vault analysis and health metrics

Usage:
    # CLI usage
    mcp-obsidian --vault /path/to/vault --log-level INFO
    
    # Python usage  
    from obsidian_mcp import ObsidianMCPServer
    server = ObsidianMCPServer(vault_path="/path/to/vault")
"""

__version__ = "0.1.0"
__author__ = "Erin Mikail Staples"
__email__ = "erin@squarecat.io"

__all__ = [
    "__version__",
    "main",
]

def main() -> None:
    """Main entry point for the CLI."""
    from obsidian_mcp.__main__ import main as _main
    _main()