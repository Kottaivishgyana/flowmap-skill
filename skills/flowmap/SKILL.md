# flowmap

Project architecture visualizer + security analyzer. Finds project folder, scans all files, generates interactive HTML map, then Claude analyzes for vulnerabilities.

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
Do NOT open the browser yet. Wait until Step 3 is done.

### Step 3: Claude vulnerability & bug analysis (MANDATORY)
After HTML generation, Claude MUST analyze the project for real bugs and vulnerabilities.

**3a. Find high-risk files** — Run these Grep searches in parallel on the project:
```
Grep: "cursor\.execute|\.query\(|\.raw\(|\.extra\(" (SQL)
Grep: "innerHTML|dangerouslySetInnerHTML|document\.write|\.html\(" (XSS)
Grep: "exec\(|eval\(|os\.system|subprocess|child_process|spawn" (Command injection)
Grep: "pickle\.load|yaml\.load|ObjectInputStream|deserialize" (Deserialization)
Grep: "password|secret|api_key|token.*=.*['\"]" (Hardcoded secrets)
Grep: "open\(.*request|readFile.*req|sendFile.*param" (Path traversal)
Grep: "redirect\(.*req|location.*=.*req" (Open redirect)
Grep: "CORS|cors.*origin.*\*|verify.*False|rejectUnauthorized.*false" (Misconfig)
```

**3b. Read and analyze** — Read the top 8-10 files that matched above. For each file, check for:
- **SQL Injection**: string concatenation in queries, f-strings in SQL, unsanitized user input
- **XSS**: user data rendered without escaping, innerHTML with dynamic content
- **Command Injection**: user input in shell commands, os.system with variables
- **Broken Authentication**: hardcoded passwords, weak token generation, missing auth middleware
- **Insecure Deserialization**: pickle on untrusted data, yaml.unsafe_load, eval of user input
- **SSRF**: user-controlled URLs in fetch/requests/http calls
- **Path Traversal**: user input in file paths without sanitization
- **Broken Access Control**: missing permission decorators, IDOR patterns, admin without auth
- **Security Misconfig**: DEBUG=True in prod, CORS *, SSL verify disabled, verbose error pages
- **Sensitive Data Exposure**: secrets in code, PII logged, missing encryption
- **Logic Bugs**: unchecked return values, race conditions, missing null checks, infinite loops
- **Error Handling**: bare except/catch, swallowed errors, missing error responses

**3c. Inject findings into HTML** — Use the Edit tool on `<resolved_path>/flowmap-out/index.html`:

Replace this exact string:
```
<!-- FLOWMAP_FINDINGS_INJECT -->
```
With:
```
<script>const _FLOWMAP_FINDINGS = [
  {"sev":"CRITICAL","file":"api/auth.py:45","issue":"SQL injection","fix":"Use parameterized query"},
  {"sev":"HIGH","file":"utils/file.py:23","issue":"Path traversal","fix":"Validate path"}
];</script>
<!-- FLOWMAP_FINDINGS_INJECT -->
```

Keep the marker after the script tag. Valid sev: CRITICAL, HIGH, MED, LOW, INFO.

If no issues: inject `const _FLOWMAP_FINDINGS = [];`

### Step 4: Open browser and report
ONLY after findings are injected, open the HTML:
```bash
open <resolved_path>/flowmap-out/index.html
```

Then output the security report table in terminal:
```
## Security & Bug Report

| Sev | File:Line | Issue | Fix |
|-----|-----------|-------|-----|
```

The HTML page shows:
- **Insights tab** → "Claude AI Analysis" card with all findings in a table
- **Detail panel** → Click any file → right panel shows Claude findings for that file

## Examples
```
/flowmap                    → scan current directory
/flowmap martram            → find "martram" folder, scan it
/flowmap /path/to/project   → scan exact path
```

## What the generated HTML shows
- 4 views: Overview (zoomable canvas), Flows, Wiring, Insights (health score + security scan)
- Auto-detects 20+ languages, 15+ frameworks
- Maps imports, API calls, events, data references
- **Pattern Scanner**: 15+ regex vulnerability detectors with line numbers
- **Claude AI Analysis**: real findings injected after AI review
- Health scoring, cycle detection, impact analysis
- Virtual rendering for large projects (500+ files) — smooth pan/zoom
- CLI-only mode — run `/flowmap <project>` to use
