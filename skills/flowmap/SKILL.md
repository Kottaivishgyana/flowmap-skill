# flowmap

Project architecture visualizer. Finds project folder, scans all files, generates interactive HTML map.

## Trigger
`/flowmap` or `/flowmap <name_or_path>`

## Execution Steps

### Step 1: Find the project folder
- If argument is a full path → use it directly
- If argument is a name (e.g., `martram`) → search for it:
  1. Check current working directory for folder matching the name
  2. Use Glob: `**/<name>` looking for `hooks.py`, `package.json`, `manage.py`, `go.mod`, `Cargo.toml`, `setup.py`, `pyproject.toml`
  3. Check `apps/` subdirectory (common in Frappe bench)
  4. If not found, ask the user for the path
- If no argument → use current working directory

### Step 2: Run the scanner
```bash
python3 ~/.claude/skills/flowmap/bin/flowmap.py <resolved_path>
```
This reads all source files, injects them into the HTML template, and auto-opens in browser.

### Step 3: Report result
Tell user: files scanned, output path, that it's open in browser.

## Examples
```
/flowmap                    → scan current working directory
/flowmap martram            → find "martram" folder, scan it
/flowmap /path/to/project   → scan exact path
```

## What the generated HTML shows
- 5 views: Overview (zoomable canvas), Flows, Wiring, Insights (health score), Live
- Auto-detects 20+ languages, 15+ frameworks
- Maps imports, API calls, events, data references
- Health scoring, cycle detection, impact analysis
- All processing happens in HTML's built-in JS engine — no extra AI tokens after generation
