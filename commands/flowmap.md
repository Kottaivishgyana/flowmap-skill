# /flowmap

Project architecture visualizer + security analyzer. Scans codebase and generates interactive HTML maps.

## Usage

```
/flowmap                     # Scan current project
/flowmap <name_or_path>      # Scan specific project
```

## Execution

When `/flowmap` is invoked, read `~/.claude/skills/flowmap/SKILL.md` and follow ALL steps there.

The Python scanner auto-opens the browser. Do NOT run `open` separately — it causes duplicate tabs.

## Output

```
flowmap-out/
└── index.html          # Interactive architecture map (self-contained)
```
