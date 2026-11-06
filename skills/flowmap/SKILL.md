# flowmap

X-ray vision for any project. Auto-detects project type, scans files, maps architecture, generates interactive HTML.

## Trigger
`/flowmap` followed by a subcommand.

## Subcommands

### `/flowmap scan`
Full project scan → generates `flowmap-out/index.html`. Zero tokens — runs Python script directly.

### `/flowmap trace <feature>`
Trace a feature end-to-end → generates step-by-step flow (uses AI).

### `/flowmap api`
List all API endpoints + which files call them.

### `/flowmap wiring`
Map every frontend→backend connection.

### `/flowmap hooks`
Show all event/hook chains.

### `/flowmap doc <name>`
Lifecycle of a model/class/component.

## Execution

For `/flowmap scan` — run the standalone scanner (zero tokens):
```bash
python3 ~/.claude/skills/flowmap/bin/flowmap.py <project_path>
open <project>/flowmap-out/index.html
```

For other subcommands — use AI to analyze the codebase and generate output.

## Auto-Detection

The scanner automatically detects project type:

| Detection | Type | What it maps |
|-----------|------|-------------|
| `hooks.py` + `modules.txt` | Frappe | Endpoints, hooks, DocTypes, Pages |
| `manage.py` | Django | URLs, views, models, serializers |
| `app.py` / `wsgi.py` | Flask | Routes, decorators, blueprints |
| `main.py` + FastAPI | FastAPI | Router endpoints, dependencies |
| `package.json` | Node.js | Imports, API calls, routes |
| `go.mod` | Go | Handlers, structs, interfaces |
| `Cargo.toml` | Rust | Modules, traits, implementations |
| `*.py` | Python | Functions, classes, decorators |
| `*.js/*.ts` | JavaScript | Exports, imports, API calls |

## What it Scans

### Python files (`.py`)
- Functions with API decorators (`@route`, `@whitelist`, `@api_view`, etc.)
- All top-level function definitions
- Class definitions
- Import statements
- Module docstrings

### JavaScript/TypeScript files (`.js`, `.ts`, `.jsx`, `.tsx`, `.vue`, `.svelte`)
- API calls (`fetch`, `axios`, `frappe.call`, `$.ajax`, `useQuery`)
- Route definitions
- Export statements
- Import statements

### Config files
- `package.json` — name, dependencies, scripts
- `hooks.py` — event registrations (Frappe)
- `urls.py` — URL patterns (Django)

## Output
```
project/flowmap-out/
├── index.html          # Interactive architecture map
└── flowmap-data.json   # Raw scan data
```

## Ignored Directories
`.git`, `node_modules`, `__pycache__`, `.next`, `dist`, `build`, `venv`, `env`, `target`, `vendor`, `migrations`, `static`, `assets`
