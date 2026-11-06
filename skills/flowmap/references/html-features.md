# HTML Output Features

## Views

### Overview (default)
- Stats bar: endpoint count, hooks, doctypes, pages, JS files, Python files
- Legend bar with type colors and connection indicators
- Zoomable/pannable canvas with dot-grid background
- Section boxes grouping nodes by type (API, Hooks, JS, DocTypes, Pages)
- Node cards with icon, name, description, badges
- SVG edge connections between JS→API nodes
- Minimap (bottom-right)
- Zoom controls (+/-, fit, percentage display)

### Flows
- 2-column grid of flow cards
- Vertical step-by-step with connector lines
- Type icons: radio waves (API), lightning (Hook), brackets (JS), cursor (UI)
- Type badge pills (uppercase)

### Wiring
- Frontend→Backend call map with animated dashed arrows
- `frappe.call` badges
- Doc event chains with numbered steps per DocType

## Interactions
- **Click node** → detail panel shows endpoints, callers, handlers
- **Hover node** → dims unconnected nodes, highlights related edges
- **⌘K** → command palette to search all files/endpoints
- **Scroll** → zoom canvas
- **Drag** → pan canvas
- **Type filters** → show/hide node types (dashed border when off)
- **Theme toggle** → dark ↔ light

## Design Tokens
```
Colors:
  API:     #3b82f6 (blue)
  Hook:    #ef4444 (red)
  JS:      #eab308 (yellow)
  DocType: #22c55e (green)
  Page:    #8b5cf6 (purple)
  Integration: #f97316 (orange)
  Stat:    #06b6d4 (cyan)

Dark theme:
  --bg:      #0f172a
  --panel:   #1e293b
  --node:    #111a2e
  --line:    #334155
  --text:    #e2e8f0
  --muted:   #94a3b8

Light theme:
  --bg:      #f1f5f9
  --panel:   #ffffff
  --node:    #ffffff
  --line:    #cbd5e1
  --text:    #0f172a
  --muted:   #475569
```
