#!/usr/bin/env python3
"""Development server script for testing with MCP Inspector."""

import os
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from obsidian_mcp.server import create_server

# Use environment variable or default to the HQ vault for development
DEFAULT_VAULT = "/Users/erinmikail/Library/Mobile Documents/iCloud~md~obsidian/Documents/HQ"
vault_path = Path(os.environ.get("OBSIDIAN_VAULT_PATH", DEFAULT_VAULT))

if not vault_path.exists():
    print(f"Error: Vault path does not exist: {vault_path}", file=sys.stderr)
    print("Set OBSIDIAN_VAULT_PATH environment variable to your vault path", file=sys.stderr)
    sys.exit(1)

print(f"Using vault: {vault_path}", file=sys.stderr)

# Create and configure the server
mcp = create_server(
    vault_path=vault_path,
    config_path=None,
    watch_mode=False,
    dry_run_default=True,  # Enable dry-run by default in development
)

# This allows mcp dev to discover the server
if __name__ == "__main__":
    mcp.run()