# flowmap

X-ray vision for any project. Auto-detects language and framework, maps architecture, generates interactive HTML with zero tokens.

## Trigger
`/flowmap` followed by optional subcommand.

## Usage

### `/flowmap` or `/flowmap scan`
Open the Flowmap HTML app in the browser. User can:
1. Drop a project folder to scan it instantly
2. Or use the built-in demo projects

```bash
open ~/.claude/skills/flowmap/bin/template.html
```

### `/flowmap scan <path>`
Run the Python pre-scanner on a specific path, then open:
```bash
python3 ~/.claude/skills/flowmap/bin/flowmap.py <path>
open <path>/flowmap-out/index.html
```

## What Flowmap Does (built into the HTML)

### Supported Languages
Python, JavaScript, TypeScript, Go, Rust, Java, Kotlin, Scala, C#, PHP, Ruby, Dart, Elixir, Prisma, SQL, GraphQL, Protobuf, Docker, Terraform, YAML

### Supported Frameworks (auto-detected)
Flask, Django, FastAPI, Express, NestJS, Next.js, React, Vue, Svelte, Spring Boot, Laravel, Rails, Frappe/ERPNext, Actix, Rocket, Gin, Echo, Phoenix

### 5 Views
1. **Overview** — zoomable canvas with nodes, edges, sections, minimap
2. **Flows** — step-by-step user flows with trace replay
3. **Wiring** — frontend→backend call map + event chains
4. **Insights** — health score, issues, hotspots, cycle detection, coverage
5. **Live** — real-time file watching with change feed

### Features
- **Auto-detect** language, framework, and stack from file contents
- **Edge types**: import, HTTP call, event, data reference
- **Layer classification**: UI, API, service, event, data, infra, config, test, docs
- **Path tracer** — find path between any two files (P key)
- **Impact analysis** — what breaks if a file changes (I key)
- **Health scoring** — layering violations, circular deps, untested code
- **Cycle detection** — finds circular import chains
- **Canvas** — zoom, pan, minimap, node selection
- **Command palette** — ⌘K to search everything
- **Export** — Markdown report, JSON graph, Mermaid diagrams
- **Dark/Light theme**
- **Drag-and-drop** — drop any folder to scan instantly
- **Keyboard shortcuts** — /, F, P, I, D, L, T, 1-5, Esc

### Keyboard Shortcuts
| Key | Action |
|-----|--------|
| `/` | Focus search |
| `1-5` | Switch views |
| `F` | Fit canvas to screen |
| `P` | Path tracer mode |
| `I` | Impact analysis mode |
| `D` | Toggle detail panel |
| `T` | Toggle theme |
| `L` | Toggle live mode |
| `⌘K` | Command palette |
| `Esc` | Clear selection/mode |

## Files
- `bin/template.html` — Complete standalone Flowmap app (2400+ lines, self-contained)
- `bin/flowmap.py` — Optional Python pre-scanner for CLI usage
