"""Main MCP server implementation for Obsidian vaults."""

import logging
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP


logger = logging.getLogger(__name__)


def create_server(
    vault_path: Path,
    config_path: Optional[str] = None,
    watch_mode: bool = False,
    dry_run_default: bool = False,
) -> FastMCP:
    """Create and configure the Obsidian MCP server.
    
    Args:
        vault_path: Path to the Obsidian vault
        config_path: Optional path to configuration file
        watch_mode: Enable real-time vault monitoring
        dry_run_default: Enable dry-run mode by default for destructive operations
        
    Returns:
        Configured FastMCP server instance
    """
    logger.info(f"Creating MCP server for vault: {vault_path}")
    
    # Create FastMCP server instance
    mcp = FastMCP(
        name="obsidian-mcp",
        instructions="MCP Server for Obsidian vaults - read, write, search, organize and analyze your notes",
    )
    
    # Store configuration on the server instance
    mcp.vault_path = vault_path
    mcp.config_path = config_path
    mcp.watch_mode = watch_mode
    mcp.dry_run_default = dry_run_default
    
    logger.debug(f"Server configuration:")
    logger.debug(f"  Vault: {vault_path}")
    logger.debug(f"  Config: {config_path}")
    logger.debug(f"  Watch mode: {watch_mode}")
    logger.debug(f"  Dry-run default: {dry_run_default}")
    
    # Register resources
    _register_resources(mcp)
    
    # Register tools
    _register_tools(mcp)
    
    logger.info("MCP server created successfully")
    return mcp


def _register_resources(mcp: FastMCP) -> None:
    """Register MCP resources for reading vault content."""
    
    @mcp.resource("obsidian://{path}")
    def read_note_resource(path: str) -> str:
        """Read a note from the vault by path.
        
        Args:
            path: Relative path to the note within the vault
            
        Returns:
            Note content including frontmatter
        """
        from obsidian_mcp.utils import safe_join, read_text_autodetect
        
        try:
            vault_path = mcp.vault_path
            file_path = safe_join(vault_path, path)
            
            if not file_path.exists():
                return f"# File not found: {path}\n\nThe requested file does not exist in the vault."
            
            if not file_path.is_file():
                return f"# Not a file: {path}\n\nThe requested path is not a file."
            
            content = read_text_autodetect(file_path)
            logger.debug(f"Read resource: {path} ({len(content)} chars)")
            
            return content
            
        except Exception as e:
            logger.error(f"Error reading resource {path}: {e}")
            return f"# Error reading file: {path}\n\nError: {str(e)}"


def _register_tools(mcp: FastMCP) -> None:
    """Register MCP tools for vault operations."""
    
    @mcp.tool()
    def get_vault_info() -> dict:
        """Get basic information about the current vault.
        
        Returns:
            Dictionary with vault path and basic statistics
        """
        try:
            vault_path = mcp.vault_path
            
            # Count markdown files
            md_files = list(vault_path.glob("**/*.md"))
            total_files = len(md_files)
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in md_files if f.is_file())
            
            from obsidian_mcp.utils import format_file_size
            
            return {
                "vault_path": str(vault_path),
                "total_markdown_files": total_files,
                "total_size": format_file_size(total_size),
                "total_size_bytes": total_size,
                "watch_mode": mcp.watch_mode,
                "dry_run_default": mcp.dry_run_default,
            }
            
        except Exception as e:
            logger.error(f"Error getting vault info: {e}")
            return {"error": str(e)}
    
    @mcp.tool()  
    def list_files(
        folder: Optional[str] = None, 
        recursive: bool = True,
        glob_pattern: Optional[str] = None,
        include_folders: bool = False,
    ) -> dict:
        """List files in the vault or a specific folder.
        
        Args:
            folder: Relative folder path (None for vault root)
            recursive: Include files in subdirectories
            glob_pattern: Glob pattern to filter files (e.g., "*.md", "2024-*")
            include_folders: Include directories in the results
            
        Returns:
            Dictionary with file listing and metadata
        """
        from obsidian_mcp.utils import safe_join, format_file_size
        
        try:
            vault_path = mcp.vault_path
            
            # Determine search path
            if folder:
                search_path = safe_join(vault_path, folder)
                if not search_path.exists():
                    return {"error": f"Folder not found: {folder}"}
                if not search_path.is_dir():
                    return {"error": f"Path is not a directory: {folder}"}
            else:
                search_path = vault_path
            
            # Build glob pattern
            if glob_pattern:
                pattern = glob_pattern
            else:
                pattern = "*"
                
            if recursive:
                pattern = f"**/{pattern}"
            
            # Find matching paths
            paths = list(search_path.glob(pattern))
            
            # Filter and collect results
            files = []
            folders = []
            
            for path in paths:
                relative_path = str(path.relative_to(vault_path))
                
                if path.is_file():
                    stat = path.stat()
                    files.append({
                        "path": relative_path,
                        "name": path.name,
                        "size": format_file_size(stat.st_size),
                        "size_bytes": stat.st_size,
                        "modified": stat.st_mtime,
                        "extension": path.suffix.lower(),
                    })
                elif path.is_dir() and include_folders:
                    folders.append({
                        "path": relative_path,
                        "name": path.name,
                        "type": "directory",
                    })
            
            # Sort results
            files.sort(key=lambda x: x["path"])
            folders.sort(key=lambda x: x["path"])
            
            result = {
                "search_path": str(search_path.relative_to(vault_path)) if folder else ".",
                "pattern": pattern,
                "recursive": recursive,
                "files": files,
                "file_count": len(files),
            }
            
            if include_folders:
                result["folders"] = folders
                result["folder_count"] = len(folders)
            
            logger.debug(f"Listed {len(files)} files in {search_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return {"error": str(e)}


# Main entry point for direct execution
if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    if len(sys.argv) != 2:
        print("Usage: python -m obsidian_mcp.server /path/to/vault", file=sys.stderr)
        sys.exit(1)
    
    vault_path = Path(sys.argv[1])
    if not vault_path.exists() or not vault_path.is_dir():
        print(f"Error: Invalid vault path: {vault_path}", file=sys.stderr)
        sys.exit(1)
    
    # Basic logging for direct execution
    logging.basicConfig(level=logging.INFO)
    
    server = create_server(vault_path)
    print(f"Starting MCP server for vault: {vault_path}")
    server.run()