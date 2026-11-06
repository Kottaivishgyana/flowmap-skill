# /flowmap

Project architecture visualizer. Scans codebase and generates interactive HTML maps.

## Usage

```
/flowmap                  # Scan current project, generate HTML, open in browser
/flowmap scan             # Same as above
/flowmap scan /path/to/app  # Scan specific app path
/flowmap trace <feature>  # Trace a feature end-to-end (uses AI tokens)
/flowmap api              # Show all API endpoints + callers
/flowmap wiring           # Show frontend→backend connections
/flowmap hooks            # Show all hook chains
```

## Execution

When `/flowmap` or `/flowmap scan` is invoked:

1. Run the standalone Python scanner — **zero tokens**:
   ```bash
   python3 ~/.claude/skills/flowmap/bin/flowmap.py <project_path>
   ```
2. Open the generated HTML:
   ```bash
   open <project>/flowmap-out/index.html
   ```
3. Report: "Generated flowmap at flowmap-out/index.html"

When `/flowmap trace <feature>` is invoked:
1. Read the skill file at `~/.claude/skills/flowmap/SKILL.md`
2. Use AI to trace the feature through the codebase
3. Generate a Mermaid flowchart and add to the HTML

## Output

```
flowmap-out/
├── index.html          # Interactive architecture map (self-contained)
└── flowmap-data.json   # Raw scan data
```
