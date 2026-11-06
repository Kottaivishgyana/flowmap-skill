# ⚡ Flowmap

> X-ray vision for any project. Auto-detects project type, scans your codebase, generates interactive HTML architecture maps — zero AI tokens.

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Zero Tokens](https://img.shields.io/badge/tokens-zero-green)
![Claude Code](https://img.shields.io/badge/claude--code-skill-purple)

## Install

```bash
git clone <repo-url> flowmap-skill
cd flowmap-skill
bash scripts/install.sh
```

## Usage

### Terminal (zero tokens)
```bash
flowmap .                        # Auto-detect + scan current project
flowmap /path/to/project         # Scan any project
open flowmap-out/index.html      # View result
```

### Claude Code
```
/flowmap scan                    # Scan + open (zero tokens)
/flowmap trace "login flow"      # AI-powered feature trace
/flowmap api                     # API endpoint map
/flowmap wiring                  # Frontend→Backend connections
```

## Supported Projects

| Type | Auto-detected by | What it maps |
|------|-----------------|-------------|
| Frappe/ERPNext | `hooks.py` | Endpoints, hooks, DocTypes, Pages |
| Django | `manage.py` | URLs, views, models, serializers |
| Flask | `app.py` | Routes, decorators, blueprints |
| FastAPI | `main.py` + FastAPI | Router endpoints, schemas |
| Node.js / React | `package.json` | Imports, API calls, routes |
| Go | `go.mod` | Handlers, structs |
| Rust | `Cargo.toml` | Modules, traits |
| Any Python | `*.py` | Functions, classes, decorators |
| Any JS/TS | `*.js/*.ts` | Exports, imports, API calls |

## Features

| Feature | Description |
|---------|-------------|
| **Auto-detect** | Automatically identifies project type |
| **Zoomable canvas** | Scroll to zoom, drag to pan, dot-grid background |
| **Node cards** | Click → detail panel with endpoints, callers |
| **SVG edges** | Animated connections between frontend→backend |
| **Minimap** | Bottom-right corner overview |
| **3 views** | Overview, Flows, Wiring |
| **Command palette** | ⌘K to search everything |
| **Dark/Light theme** | Toggle in header |
| **Type filters** | Show/hide by category |

## Plugin Structure

```
flowmap-skill/
├── .claude-plugin/plugin.json   # Plugin metadata
├── skills/flowmap/
│   ├── SKILL.md                 # Skill definition
│   └── references/              # Reference docs
├── commands/flowmap.md          # /flowmap command
├── bin/
│   ├── flowmap.py               # Scanner (zero tokens)
│   └── template.html            # Interactive HTML template
├── scripts/install.sh           # Installer
└── README.md
```

## Adding Features

1. **New project type** → add detection in `detect_project()` + scanner in `flowmap.py`
2. **New API pattern** → add regex to `api_decorators` or `call_patterns`
3. **UI changes** → edit `bin/template.html`
4. **New view** → add JS in template's `<script>` block

Reinstall after changes: `bash scripts/install.sh`

## Requirements

- Python 3.6+ (no pip dependencies)
- Any modern browser
