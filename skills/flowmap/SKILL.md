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

### Step 3: Claude security analysis (uses tokens)
After generation, do a **real vulnerability analysis** using Claude's understanding:
1. Read the **API/route files** (files with routes, endpoints, controllers) — max 5 files
2. Read **files handling user input** (forms, request handlers, auth) — max 5 files
3. Read **data layer files** (models, DB queries, ORM usage) — max 3 files
4. For each file read, check for:
   - **Injection**: SQL injection, NoSQL injection, command injection, LDAP injection
   - **Broken auth**: hardcoded credentials, weak password handling, missing auth checks
   - **XSS**: unescaped output, innerHTML, template injection
   - **Insecure deserialization**: pickle, eval, yaml.load, ObjectInputStream
   - **SSRF**: user-controlled URLs in server-side requests
   - **Path traversal**: user input in file operations
   - **Broken access control**: missing permission checks, IDOR patterns
   - **Security misconfig**: debug mode, CORS *, disabled SSL verify, verbose errors
   - **Sensitive data exposure**: secrets in code, logging PII, missing encryption
5. Output a **Security Report** table:
   ```
   | Severity | File:Line | Vulnerability | Fix |
   |----------|-----------|--------------|-----|
   | CRITICAL | auth.py:45 | SQL injection in login query | Use parameterized query |
   ```
6. If no issues found, say "No vulnerabilities detected in sampled files."

**File selection heuristic**: Prioritize files named `auth`, `login`, `api`, `routes`, `views`, `controllers`, `middleware`, `db`, `queries`, `admin`. Use Grep to find files with `req.body`, `request.form`, `cursor.execute`, `.query(`, `eval(`, `exec(` etc.

### Step 4: Report result
Tell user: files scanned, output path, that it's open in browser. Include the security report.

## Examples
```
/flowmap                    → scan current working directory
/flowmap martram            → find "martram" folder, scan it
/flowmap /path/to/project   → scan exact path
```

## What the generated HTML shows
- 5 views: Overview (zoomable canvas), Flows, Wiring, Insights (health score + security scan), Live
- Auto-detects 20+ languages, 15+ frameworks
- Maps imports, API calls, events, data references
- **Security scanner** detects: SQL injection, XSS, command injection, path traversal, SSRF, insecure deserialization, hardcoded secrets, weak crypto, CORS misconfig, prototype pollution, open redirects, ReDoS, dangerous eval, disabled SSL verification, debug mode in prod, insecure cookie flags
- Health scoring, cycle detection, impact analysis
- Virtual rendering for large projects (500+ files) — only visible nodes rendered, smooth pan/zoom
- All processing happens in HTML's built-in JS engine — no extra AI tokens after generation
