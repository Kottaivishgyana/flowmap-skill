# flowmap

X-ray vision for any project. Generates interactive HTML flowchart files showing architecture, API wiring, and data flow.

## Trigger
`/flowmap` followed by a subcommand.

## Subcommands

### `/flowmap scan`
Full project scan → generates `flowmap-out/index.html` with interactive project map.

### `/flowmap trace <feature>`
Trace a feature end-to-end → generates `flowmap-out/trace-<feature>.html` with step-by-step flow.

### `/flowmap api`
All API endpoints + callers → generates `flowmap-out/api-map.html` with connection diagram.

### `/flowmap wiring`
Frontend→Backend connections → generates `flowmap-out/wiring.html` with interactive graph.

### `/flowmap hooks`
All hook chains → generates `flowmap-out/hooks.html` with event flow diagram.

### `/flowmap doc <DocType>`
DocType lifecycle → generates `flowmap-out/doc-<name>.html` with lifecycle flowchart.

## Execution Steps

When any subcommand is invoked:

### Step 1: Detect Project
- Look for `hooks.py` (Frappe), `package.json` (Node), `manage.py` (Django), etc.
- Set project root and type.

### Step 2: Scan Sources
- **Python**: Parse `@frappe.whitelist()`, `doc_events`, imports, class defs
- **JavaScript**: Parse `frappe.call()`, `frappe.xcall()`, event handlers, `frappe.set_route()`
- **Config**: Parse `hooks.py`, `setup.py`, `package.json`
- Build relationship data as JSON.

### Step 3: Generate HTML File
Create `flowmap-out/` directory in project root and generate self-contained HTML files.

#### HTML File Template Structure:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Flowmap — {title}</title>
    <style>/* Full CSS embedded */</style>
</head>
<body>
    <div id="app">
        <!-- Sidebar: file tree -->
        <!-- Main: interactive flow diagram -->
        <!-- Detail panel: file/function details -->
    </div>
    <script>
        const FLOW_DATA = {/* JSON data from scan */};
        // Interactive rendering logic
    </script>
</body>
</html>
```

#### Required HTML Features:
1. **Interactive nodes** — click to expand, show details
2. **Connection lines** — SVG arrows between frontend→API→backend
3. **Color coding** — Python (blue), JS (yellow), DocType (green), Hook (red)
4. **Search** — filter nodes by name
5. **Zoom/Pan** — for large projects
6. **Sidebar** — file tree with click-to-highlight
7. **Detail panel** — shows file content, endpoint info, callers
8. **Mermaid diagrams** — embedded for flow traces
9. **Responsive** — works on mobile too
10. **Dark/Light mode** — follows system preference

### Step 4: Open in Browser
After generating, show the file path and suggest opening it.

## Output Directory
```
flowmap-out/
├── index.html          # Main project map (from /flowmap scan)
├── api-map.html        # API endpoint map (from /flowmap api)
├── wiring.html         # Frontend→Backend wiring (from /flowmap wiring)
├── hooks.html          # Hook chains (from /flowmap hooks)
├── trace-*.html        # Feature traces (from /flowmap trace)
└── doc-*.html          # DocType lifecycles (from /flowmap doc)
```

## Data Structure for FLOW_DATA

```json
{
  "project": {
    "name": "martram",
    "type": "frappe",
    "root": "/path/to/app"
  },
  "files": [
    {
      "path": "api/workspace.py",
      "type": "python",
      "purpose": "Outlet workspace APIs",
      "endpoints": [
        {"name": "get_user_outlet", "line": 12, "args": [], "returns": "string"}
      ],
      "hooks": [],
      "imports": ["frappe"]
    }
  ],
  "connections": [
    {
      "from": {"file": "public/js/workspace_outlet.js", "line": 150, "type": "frappe.xcall"},
      "to": {"file": "api/workspace.py", "function": "get_user_outlet"},
      "label": "get outlet name"
    }
  ],
  "hooks": [
    {
      "event": "autoname",
      "doctype": "Stock Entry",
      "handler": "martram.api.reference_id.autoname_stock_entry",
      "file": "api/reference_id.py"
    }
  ],
  "doctypes": [
    {"name": "Stock Reconciliation Template", "module": "martram", "fields": 5, "child_tables": 1}
  ]
}
```

## Visual Design Specs

### Node Types & Colors
| Type | Color | Shape |
|------|-------|-------|
| Python API | `#3B82F6` (blue) | Rounded rect |
| JavaScript | `#EAB308` (yellow) | Rounded rect |
| DocType | `#22C55E` (green) | Rectangle |
| Hook/Event | `#EF4444` (red) | Diamond |
| Page | `#8B5CF6` (purple) | Rounded rect |
| Fixture | `#6B7280` (gray) | Dashed rect |

### Connection Types
| Type | Style | Color |
|------|-------|-------|
| frappe.call | Solid arrow | `#3B82F6` |
| doc_event | Dashed arrow | `#EF4444` |
| import | Dotted line | `#6B7280` |
| route | Thick arrow | `#8B5CF6` |

### Layout
- **Left sidebar** (250px): File tree, collapsible folders
- **Center canvas** (flex): Interactive flow diagram with zoom/pan
- **Right panel** (300px, toggleable): Selected node details
- **Top bar**: Search, filter by type, zoom controls, dark/light toggle

## Important Notes
- All HTML files must be **fully self-contained** (no external CDN dependencies)
- Use inline SVG for arrows and connections
- Use CSS Grid/Flexbox for layout
- Canvas rendering via plain DOM + SVG (no heavy libraries)
- Keep file size under 500KB per HTML file
- Add `flowmap-out/` to `.gitignore`
