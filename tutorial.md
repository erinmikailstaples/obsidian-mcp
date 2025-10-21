# Building an Obsidian MCP Server - Tutorial

This tutorial documents the step-by-step process of building a comprehensive MCP (Model Context Protocol) server for Obsidian vaults that can be used with Goose and other MCP clients.

## Project Goals

- **Universal compatibility**: Work with any Obsidian vault, not just specific setups
- **Comprehensive functionality**: Read, write, search, organize, and analyze vault content  
- **Safety first**: Explicit confirmations for destructive operations, dry-run modes
- **Performance**: Optimized for 2GB+ vaults with optional acceleration tools
- **Goose integration**: Seamless integration as a Goose extension

## Target Features

### Core Operations
- ✅ Read/write individual notes
- ✅ List files and folders  
- ✅ Create/update/delete files with safety checks
- ✅ Parse and manipulate frontmatter

### Search & Discovery
- ✅ Full-text search with regex support
- ✅ Tag-based search (inline and frontmatter)
- ✅ Metadata querying with JMESPath
- ✅ Date range searches
- ✅ Path/folder-based searches

### Link Management  
- ✅ Navigate forward/backward links
- ✅ Resolve wikilinks and aliases
- ✅ Fix broken links (with dry-run)
- ✅ Generate link graphs

### Organization Tools
- ✅ Generate Maps of Content (MOCs)
- ✅ Bulk tagging operations
- ✅ File moving with link updates
- ✅ Structure validation (configurable rules)

### Analysis & Insights
- ✅ Vault statistics and health metrics
- ✅ Find orphaned notes and stubs
- ✅ Validate folder/naming conventions

## Configuration Approach

Using a hybrid configuration system:
1. **CLI flags** (highest priority): `--vault`, `--config`, `--log-level`, etc.
2. **Environment variables**: `OBSIDIAN_VAULT_PATH`, `OBSIDIAN_MCP_CONFIG`, etc.
3. **Per-vault config**: `.obsidian-mcp.yaml` in vault root
4. **Global defaults** (lowest priority)

This gives maximum flexibility - users can have vault-specific rules while maintaining global defaults.

## Safety & Performance Features

### Safety  
- **Explicit confirmations** required for bulk operations and deletions
- **Dry-run mode** for link fixing and organizational changes
- **Path validation** to prevent operations outside vault root  
- **Atomic writes** with file locking to prevent corruption
- **System trash integration** (send2trash) instead of permanent deletion

### Performance
- **Intelligent indexing** with caching for large vaults
- **Optional ripgrep integration** for faster text search  
- **Optional rapidfuzz** for smart link resolution
- **Watch mode** for real-time index updates (optional)
- **Concurrent processing** for initial vault scanning

## Implementation Log

### Phase 1: Project Setup ✅

**Date**: 2025-10-21

**Objective**: Scaffold the project with proper MCP structure and dependencies.

#### Step 1: MCP SDK Reference ✅
- Cloned latest python-sdk from https://github.com/modelcontextprotocol/python-sdk
- Confirmed FastMCP usage patterns with @mcp.tool() and @mcp.resource() decorators
- Reviewed error handling with McpError and ErrorData types
- Verified structured output support for JSON responses

#### Key Findings:
- FastMCP is the recommended high-level server interface
- Tools should return structured data when possible (JSON/dict responses)
- Resources are read-only, tools handle mutations
- Context injection provides logging, progress reporting, and client communication

---

#### Step 2: Project Scaffolding ✅
- ✅ Created proper directory structure with `src/obsidian_mcp/` layout
- ✅ Configured pyproject.toml with all core dependencies:
  - `mcp[cli]>=1.2.0` for MCP protocol implementation
  - `python-frontmatter` for YAML frontmatter parsing
  - `ruamel.yaml` for formatting-preserving YAML operations
  - `send2trash`, `filelock`, `chardet`, `jmespath`, `rich` for utilities
  - Optional: `watchdog` for watch mode, `rapidfuzz` for fuzzy matching
- ✅ Created package with proper editable installation
- ✅ CLI entry point works: `mcp-obsidian --help`

#### Step 3: CLI and Infrastructure ✅
- ✅ Implemented robust CLI argument parsing with comprehensive help
- ✅ Environment variable fallbacks (OBSIDIAN_VAULT_PATH, etc.)
- ✅ Logging setup with Rich formatting and file output
- ✅ Path safety utilities (safe_join, atomic_write, file locking)
- ✅ Utility functions for encoding detection and data serialization
- ✅ Proper error handling with McpError and structured error data

#### Step 4: Basic MCP Server ✅
- ✅ FastMCP server creation and configuration
- ✅ Resource template: `obsidian://{path}` for reading notes
- ✅ Basic tools: `get_vault_info()` and `list_files()` 
- ✅ Server successfully initializes with your HQ vault
- ✅ Proper logging and error handling throughout

### Next Steps

#### Phase 3: Foundation Components  
- [ ] Markdown parsing (frontmatter, wikilinks, tags)
- [ ] Vault indexing and link graph construction
- [ ] Enhanced resources and core file operations (CRUD)

#### Phase 3: Foundation Components  
- [ ] Markdown parsing (frontmatter, wikilinks, tags)
- [ ] Vault indexing and link graph construction
- [ ] Base MCP server with resource templates
- [ ] Core file operations (CRUD)

#### Phase 4: Advanced Features
- [ ] Search implementations (text, tags, metadata, dates)
- [ ] Link navigation and resolution
- [ ] Organizational tools (MOCs, bulk operations, moves)
- [ ] Analysis tools (stats, orphans, validation)

#### Phase 5: Polish & Integration
- [ ] Testing with sample vault fixtures  
- [ ] Performance optimization and caching
- [ ] Goose integration documentation
- [ ] Final documentation and release prep

---

## Technical Decisions

### Why This Architecture?

1. **Modular Design**: Separate modules for parsing, indexing, operations, etc. makes the codebase maintainable and testable.

2. **FastMCP**: Chosen over low-level MCP for faster development while maintaining full protocol compliance.

3. **Hybrid Config**: Balances flexibility (per-vault customization) with simplicity (sensible defaults).

4. **Optional Dependencies**: Core functionality works without ripgrep/rapidfuzz, but performance improves when available.

5. **Safety-First**: Better to require explicit confirmations than accidentally delete user data.

### Dependencies Rationale

- **mcp[cli]**: Core MCP protocol implementation with CLI tools
- **python-frontmatter**: Robust YAML frontmatter parsing
- **ruamel.yaml**: Preserves formatting/comments when writing YAML
- **send2trash**: Safe deletion to system trash instead of permanent removal
- **filelock**: Prevents concurrent access corruption
- **jmespath**: Powerful JSON/metadata querying
- **chardet**: Robust text encoding detection
- **rich**: Enhanced CLI output and logging  
- **watchdog** (optional): File system event monitoring
- **rapidfuzz** (optional): Fast fuzzy string matching for link resolution

---

*This tutorial will be updated as we build each component. Each phase will include detailed implementation notes, code examples, and lessons learned.*