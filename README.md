# ⚡ Flowmap

> X-ray vision for any project. Scans your codebase and generates interactive HTML architecture maps — zero AI tokens needed.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Zero Tokens](https://img.shields.io/badge/tokens-zero-green)
![Frappe](https://img.shields.io/badge/frappe-supported-orange)
![Claude Code](https://img.shields.io/badge/claude--code-skill-purple)

## Install

```bash
git clone <repo-url> flowmap-skill
cd flowmap-skill
bash scripts/install.sh
```

That's it. Restart your shell.

## Plugin Structure

```
flowmap-skill/
├── .claude-plugin/
│   └── plugin.json              # Plugin metadata
├── skills/
│   └── flowmap/
│       ├── SKILL.md             # Skill definition (Claude reads this)
│       └── references/
│           ├── supported-projects.md
│           └── html-features.md
├── commands/
│   └── flowmap.md               # /flowmap command definition
├── bin/
│   ├── flowmap.py               # Python scanner (zero tokens)
│   └── template.html            # Interactive HTML template
├── scripts/
│   └── install.sh               # One-command installer
└── README.md
```

## Usage

### Terminal (zero tokens)
```bash
flowmap .                        # Scan current project
flowmap /path/to/apps/myapp      # Scan any project
open flowmap-out/index.html      # View result
```

### Claude Code
```
/flowmap scan                    # Scan + open (zero tokens)
/flowmap trace "closing stock"   # AI-powered feature trace
/flowmap api                     # API endpoint map
/flowmap wiring                  # Frontend→Backend connections
```

## Output

```
your-project/
└── flowmap-out/
    ├── index.html               # Interactive architecture map
    └── flowmap-data.json        # Raw scan data (JSON)
```

Open `index.html` in any browser. Fully self-contained, no external dependencies.

## Features

### Interactive HTML
| Feature | Description |
|---------|-------------|
| Zoomable canvas | Scroll to zoom, drag to pan, dot-grid background |
| Node cards | Click → detail panel with endpoints, callers |
| SVG edges | Animated connections between JS→API |
| Minimap | Bottom-right corner overview |
| 3 views | Overview, Flows, Wiring |
| Command palette | ⌘K to search everything |
| Dark/Light theme | Toggle in header |
| Type filters | Show/hide API, Hooks, JS, DocTypes, Pages |

### Scanner
| Feature | Description |
|---------|-------------|
| Auto-detect | Frappe, Django, Node.js, generic Python |
| Frappe hooks | doc_events, permissions, boot_session |
| API mapping | `@frappe.whitelist()` → `frappe.call()` |
| Zero deps | Pure Python 3.6+, no pip install |

## Supported Projects

| Type | Detection | What it maps |
|------|-----------|-------------|
| Frappe/ERPNext | `hooks.py` | Endpoints, hooks, JS callers, DocTypes, Pages |
| Django | `manage.py` | URLs, views, models |
| Node.js | `package.json` | Routes, API calls, components |
| Generic Python | `*.py` | Functions, decorators, imports |

## Adding Features

1. **New scanner logic** → edit `bin/flowmap.py`
2. **UI changes** → edit `bin/template.html`
3. **New views** → add JS in template's `<script>` block
4. **New project type** → add detection in `find_app_root()` and parser function
5. **Reference docs** → add to `skills/flowmap/references/`

After changes, reinstall:
```bash
bash scripts/install.sh
```

## Requirements

- Python 3.6+
- Any modern browser
- No pip dependencies
- No external CDN

## License

MIT
