# Obsidian MCP Server

A comprehensive [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for Obsidian vaults that enables AI assistants and tools like [Goose](https://github.com/square/goose) to read, write, search, organize, and analyze your notes.

## Features

### 🚀 **Universal Compatibility**
- Works with **any** Obsidian vault structure
- Configurable folder conventions and naming rules
- Supports custom frontmatter standards and tag hierarchies

### 🔧 **Core Operations** 
- Read and write individual notes with frontmatter support
- List files with flexible filtering and glob patterns
- Safe file operations with path validation and atomic writes
- Resource access via `obsidian://{path}` URIs

### 🛡️ **Safety First**
- Path traversal protection 
- Explicit confirmations for destructive operations
- Dry-run mode for link fixing and bulk operations
- System trash integration instead of permanent deletion
- File locking to prevent corruption

### 📊 **Rich Tool Set** *(Coming Soon)*
- Full-text search with regex support
- Tag-based search and metadata queries  
- Link navigation and broken link detection
- Vault analysis and health metrics
- Organizational tools (MOCs, bulk operations)

## Installation

```bash
# Install from PyPI (coming soon)
pip install mcp-obsidian

# Or install from source
git clone https://github.com/erinmikailstaples/obsidian-mcp
cd obsidian-mcp
uv sync
uv pip install -e .
```

## Quick Start

### Basic Usage

```bash
# Start with specific vault
mcp-obsidian --vault /path/to/your/vault

# Use environment variable
export OBSIDIAN_VAULT_PATH=/path/to/your/vault
mcp-obsidian

# Enable debug logging
mcp-obsidian --vault /path/to/vault --log-level DEBUG
```

### With Goose

The server integrates seamlessly with Goose as an MCP extension:

```bash
# Test your setup
goose session --with-extension "mcp-obsidian --vault /path/to/vault"
```

In Goose, you can then:
- Read notes: "Show me the content of my daily note"
- List files: "What markdown files do I have in the Projects folder?"
- Get vault info: "Give me statistics about my vault"

### Available Tools & Resources

**Resources:**
- `obsidian://{path}` - Read any note content including frontmatter

**Tools:**
- `get_vault_info()` - Vault statistics and configuration
- `list_files(folder, recursive, glob_pattern, include_folders)` - File listing with filtering

*More tools coming soon: search, create/update/delete files, link analysis, etc.*

## Configuration

### Environment Variables

- `OBSIDIAN_VAULT_PATH` - Default vault path
- `OBSIDIAN_MCP_CONFIG` - Configuration file path  
- `OBSIDIAN_MCP_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

### Per-Vault Configuration *(Coming Soon)*

Create `.obsidian-mcp.yaml` in your vault root:

```yaml
# Folder naming conventions
folder_rules:
  prefix_required: true
  prefix_pattern: "\\d{2}-\\d{2}"

# Tag hierarchy rules  
tag_hierarchy:
  separator: "/"
  case_sensitive: false
  
# Frontmatter standards
frontmatter_standards:
  required_fields: ["created", "updated"]
  date_format: "YYYY-MM-DD"
```

## Development

### Setup

```bash
git clone https://github.com/erinmikailstaples/obsidian-mcp
cd obsidian-mcp
uv sync
uv pip install -e .
```

### Testing with MCP Inspector

```bash
# Set your vault path
export OBSIDIAN_VAULT_PATH=/path/to/your/vault

# Start development server
uv run mcp dev dev_server.py

# Open http://localhost:5173 to test with MCP Inspector
```

### Project Structure

```
obsidian-mcp/
├── src/obsidian_mcp/
│   ├── __main__.py      # CLI entry point
│   ├── server.py        # MCP server implementation
│   ├── utils.py         # Path safety and file utilities
│   ├── logging_setup.py # Rich logging configuration
│   └── operations/      # Feature modules (coming soon)
├── tests/              # Test suite (coming soon)
└── tutorial.md        # Development log and tutorial
```

## Architecture

Built on solid foundations:

- **MCP Protocol**: Uses [FastMCP](https://github.com/modelcontextprotocol/python-sdk) for full protocol compliance
- **Safety**: Path validation, atomic writes, file locking, and explicit confirmations
- **Performance**: Optional acceleration with ripgrep and rapidfuzz for large vaults  
- **Flexibility**: Hybrid configuration system (CLI → env vars → per-vault config → defaults)

## Roadmap

### Phase 3: Foundation Components *(In Progress)*
- [ ] Markdown parsing (frontmatter, wikilinks, tags)
- [ ] Vault indexing and link graph construction
- [ ] Core file operations (create, update, delete)

### Phase 4: Advanced Features *(Planned)*
- [ ] Search implementations (text, tags, metadata, dates)  
- [ ] Link navigation and resolution
- [ ] Organizational tools (MOCs, bulk operations, file moves)
- [ ] Vault analysis (stats, orphans, structure validation)

### Phase 5: Polish & Integration *(Planned)*
- [ ] Comprehensive testing with sample vaults
- [ ] Performance optimization and caching
- [ ] Goose integration documentation
- [ ] PyPI package release

## Contributing

We welcome contributions! See our development tutorial for details on the architecture and implementation approach.

## License

MIT License - see LICENSE file for details.

---

**Status**: Early development - basic functionality working, advanced features coming soon.

Built for the [Goose](https://github.com/square/goose) ecosystem and the broader MCP community
