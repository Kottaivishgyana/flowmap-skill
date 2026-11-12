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
This reads all source files, compresses into HTML template, and auto-opens in browser.

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

**3c. Output Security Report**:
```
## Security & Bug Report

| Sev | File:Line | Issue | Fix |
|-----|-----------|-------|-----|
| CRITICAL | api/auth.py:45 | SQL injection — user input concatenated into query | Use parameterized query: `cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))` |
| HIGH | utils/file.py:23 | Path traversal — request param used in open() | Validate path with `os.path.realpath()` and check it's within allowed directory |
| MED | settings.py:12 | DEBUG=True in non-dev config | Set DEBUG=False or use environment variable |
```

If no issues found: "No vulnerabilities detected in analyzed files."

### Step 4: Report result
Tell user:
1. Files scanned count, output path, browser opened
2. The security report table from Step 3
3. Health score from the HTML (if visible in terminal output)

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
- **Built-in security scanner** detects 15+ vulnerability types with line numbers
- Health scoring, cycle detection, impact analysis
- Virtual rendering for large projects (500+ files) — smooth pan/zoom
- CLI-only mode — no folder picker, no live watch, no upload. Run `/flowmap <project>` to use.
