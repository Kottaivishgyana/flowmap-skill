#!/usr/bin/env python3
"""Flowmap — Zero-token project architecture visualizer.

Scans any project, auto-detects type, maps files/endpoints/connections.
Generates interactive HTML. No AI needed. Pure code parsing.

Usage:
    python3 flowmap.py [project_path]
    python3 flowmap.py .
    python3 flowmap.py /path/to/project
"""

import os
import re
import sys
import json
from pathlib import Path


# ══════════════════════════════════════════
# PROJECT DETECTION
# ══════════════════════════════════════════

def detect_project(start_path):
    """Auto-detect project type and root."""
    p = Path(start_path).resolve()

    # Walk up to find project root indicators
    for check in [p] + list(p.parents)[:3]:
        # Python: Frappe
        if (check / "hooks.py").exists() and (check / "modules.txt").exists():
            return check, "frappe"
        for child in check.iterdir():
            if child.is_dir() and (child / "hooks.py").exists():
                return child, "frappe"

        # Python: Django
        if (check / "manage.py").exists():
            return check, "django"

        # Python: Flask
        if any((check / f).exists() for f in ["app.py", "wsgi.py"]):
            return check, "flask"

        # Python: FastAPI
        if (check / "main.py").exists() and _file_contains(check / "main.py", "FastAPI"):
            return check, "fastapi"

        # Node.js
        if (check / "package.json").exists():
            return check, "node"

        # Go
        if (check / "go.mod").exists():
            return check, "go"

        # Rust
        if (check / "Cargo.toml").exists():
            return check, "rust"

    # Fallback: generic — use start path
    if any(p.glob("**/*.py")):
        return p, "python"
    if any(p.glob("**/*.js")) or any(p.glob("**/*.ts")):
        return p, "javascript"

    return p, "unknown"


def _file_contains(path, text):
    try:
        return text in path.read_text(errors="ignore")[:5000]
    except Exception:
        return False


# ══════════════════════════════════════════
# GENERIC PARSERS
# ══════════════════════════════════════════

def parse_python_file(filepath):
    """Parse any Python file for functions, decorators, classes."""
    try:
        content = filepath.read_text(errors="ignore")
        lines = content.split('\n')
    except Exception:
        return {"endpoints": [], "functions": [], "classes": [], "imports": [], "purpose": ""}

    endpoints = []
    functions = []
    classes = []
    imports = []

    # Common API decorators
    api_decorators = [
        r'@\w+\.whitelist',      # frappe.whitelist
        r'@app\.route',          # Flask
        r'@router\.\w+',        # FastAPI
        r'@api_view',           # DRF
        r'@action',             # DRF viewset
        r'@require_http',       # Django
        r'@login_required',     # Django
        r'@csrf_exempt',        # Django
    ]
    api_pattern = '|'.join(api_decorators)

    for i, line in enumerate(lines, 1):
        # Decorators → endpoint
        if re.match(r'\s*@', line):
            if re.search(api_pattern, line):
                for j in range(i, min(i + 5, len(lines) + 1)):
                    fn_match = re.match(r'\s*def\s+(\w+)\s*\((.*?)\)', lines[j - 1])
                    if fn_match:
                        name = fn_match.group(1)
                        args_raw = fn_match.group(2)
                        args = [a.strip().split('=')[0].split(':')[0].strip()
                                for a in args_raw.split(',')
                                if a.strip() and a.strip() not in ('self', 'cls', 'request', 'method', '*args', '**kwargs')]
                        endpoints.append({"name": name, "line": j, "args": args, "decorator": line.strip()})
                        break

        # All functions
        fn_match = re.match(r'def\s+(\w+)\s*\((.*?)\)', line)
        if fn_match and not line.startswith(' '):
            functions.append({"name": fn_match.group(1), "line": i})

        # Classes
        cls_match = re.match(r'class\s+(\w+)', line)
        if cls_match:
            classes.append({"name": cls_match.group(1), "line": i})

        # Imports
        imp_match = re.match(r'(?:from|import)\s+([\w.]+)', line)
        if imp_match:
            imports.append(imp_match.group(1))

    # Purpose from docstring
    purpose = ""
    m = re.match(r'^(?:"""|\'\'\')(.*?)(?:"""|\'\'\')' , content, re.DOTALL)
    if m:
        purpose = m.group(1).strip().split('\n')[0]

    return {"endpoints": endpoints, "functions": functions, "classes": classes,
            "imports": list(set(imports)), "purpose": purpose}


def parse_js_ts_file(filepath):
    """Parse JS/TS file for API calls, imports, exports, routes."""
    try:
        content = filepath.read_text(errors="ignore")
        lines = content.split('\n')
    except Exception:
        return {"calls": [], "routes": [], "exports": [], "imports": [], "purpose": ""}

    calls = []
    routes = []
    exports = []
    imports = []

    # API call patterns (generic)
    call_patterns = [
        (r'(?:fetch|axios\.\w+|api\.\w+)\s*\(\s*[`"\']([^`"\']+)[`"\']', 'fetch'),
        (r'(?:frappe\.call|frappe\.xcall)\s*\(\s*[{\"]?\s*(?:method\s*:\s*)?["\']([^"\']+)["\']', 'frappe.call'),
        (r'\$\.(get|post|ajax)\s*\(\s*["\']([^"\']+)["\']', 'jquery'),
        (r'(?:useQuery|useMutation)\s*\(\s*["\']([^"\']+)["\']', 'react-query'),
    ]

    for i, line in enumerate(lines, 1):
        for pattern, call_type in call_patterns:
            for m in re.finditer(pattern, line):
                method = m.group(1) if m.lastindex == 1 else m.group(2)
                if method and not method.startswith('//'):
                    calls.append({"method": method, "line": i, "type": call_type})

        # Routes
        for m in re.finditer(r'(?:path|route)\s*[:=]\s*["\']([^"\']+)["\']', line):
            routes.append(m.group(1))
        for m in re.finditer(r'(?:set_route|navigate|push|replace)\s*\(\s*["\']([^"\']+)["\']', line):
            routes.append(m.group(1))

        # Exports
        exp_match = re.match(r'export\s+(?:default\s+)?(?:function|class|const|let|var)\s+(\w+)', line)
        if exp_match:
            exports.append(exp_match.group(1))

        # Imports
        imp_match = re.match(r'import\s+.*?from\s+["\']([^"\']+)["\']', line)
        if imp_match:
            imports.append(imp_match.group(1))

    # Purpose
    purpose = ""
    m = re.match(r'/\*\*?\s*\n?\s*\*?\s*(.*?)(?:\n|\*/)', content)
    if m:
        purpose = m.group(1).strip()
    elif content.startswith('//'):
        purpose = content.split('\n')[0].lstrip('/ ').strip()

    return {"calls": calls, "routes": list(set(routes)), "exports": exports,
            "imports": imports, "purpose": purpose}


def parse_config_file(filepath):
    """Parse config files (JSON, YAML, TOML) for metadata."""
    try:
        if filepath.suffix == '.json':
            return json.loads(filepath.read_text(errors="ignore"))
    except Exception:
        pass
    return {}


# ══════════════════════════════════════════
# PROJECT-SPECIFIC SCANNERS
# ══════════════════════════════════════════

def scan_frappe(root):
    """Frappe/ERPNext specific scanning."""
    hooks = _parse_frappe_hooks(root / "hooks.py") if (root / "hooks.py").exists() else {}
    app_name = root.name

    hook_files = []
    hook_map = {}
    for dt, events in hooks.get("doc_events", {}).items():
        for event, handler in events.items():
            for h in (handler if isinstance(handler, list) else [handler]):
                parts = h.rsplit(".", 1)
                if len(parts) == 2:
                    mod = parts[0].replace(f"{app_name}.", "").replace(".", "/") + ".py"
                    hook_map.setdefault(mod, []).append({"event": event, "doctype": dt, "fn": parts[1], "full_path": h})

    for h in hooks.get("boot_session", []):
        parts = h.rsplit(".", 1)
        if len(parts) == 2:
            mod = parts[0].replace(f"{app_name}.", "").replace(".", "/") + ".py"
            hook_map.setdefault(mod, []).append({"event": "boot_session", "doctype": None, "fn": parts[1], "full_path": h})

    for dt, h in hooks.get("permission_query_conditions", {}).items():
        parts = h.rsplit(".", 1)
        if len(parts) == 2:
            mod = parts[0].replace(f"{app_name}.", "").replace(".", "/") + ".py"
            hook_map.setdefault(mod, []).append({"event": "permission_query", "doctype": dt, "fn": parts[1], "full_path": h})

    for fpath, handlers in hook_map.items():
        purpose = ""
        full = root / fpath
        if full.exists():
            purpose = parse_python_file(full)["purpose"]
        hook_files.append({"path": fpath, "name": Path(fpath).stem, "handlers": handlers, "purpose": purpose})

    # DocTypes
    doctypes = []
    for mod_dir in root.iterdir():
        if not mod_dir.is_dir():
            continue
        dt_dir = mod_dir / "doctype"
        if not dt_dir.exists():
            continue
        for dt_folder in sorted(dt_dir.iterdir()):
            if not dt_folder.is_dir():
                continue
            jf = dt_folder / f"{dt_folder.name}.json"
            if jf.exists():
                try:
                    data = json.loads(jf.read_text(errors="ignore"))
                    if not data.get("istable", 0):
                        doctypes.append({"name": data.get("name", dt_folder.name), "folder": dt_folder.name,
                                         "is_child": False, "fields": len(data.get("fields", []))})
                except Exception:
                    pass

    # Pages
    pages = []
    for mod_dir in root.iterdir():
        if not mod_dir.is_dir():
            continue
        pg_dir = mod_dir / "page"
        if not pg_dir.exists():
            continue
        for pg_folder in sorted(pg_dir.iterdir()):
            if not pg_folder.is_dir():
                continue
            jf = pg_folder / f"{pg_folder.name}.json"
            title = pg_folder.name.replace("_", " ").title()
            if jf.exists():
                try:
                    title = json.loads(jf.read_text(errors="ignore")).get("title", title)
                except Exception:
                    pass
            pages.append({"name": pg_folder.name, "title": title})

    return hooks, hook_files, doctypes, pages


def _parse_frappe_hooks(hooks_path):
    """Parse hooks.py."""
    content = hooks_path.read_text(errors="ignore")
    result = {"doc_events": {}, "permission_query_conditions": {}, "boot_session": []}

    m = re.search(r'doc_events\s*=\s*\{(.*?)\n\}', content, re.DOTALL)
    if m:
        for dt_match in re.finditer(r'"([^"]+)"\s*:\s*\{([^}]+)\}', m.group(1)):
            events = {}
            for ev, h in re.findall(r'"(\w+)"\s*:\s*"([^"]+)"', dt_match.group(2)):
                events[ev] = h
            for ev, hs in re.findall(r'"(\w+)"\s*:\s*\[(.*?)\]', dt_match.group(2), re.DOTALL):
                events[ev] = re.findall(r'"([^"]+)"', hs)
            if events:
                result["doc_events"][dt_match.group(1)] = events

    m = re.search(r'permission_query_conditions\s*=\s*\{(.*?)\}', content, re.DOTALL)
    if m:
        for dt, fn in re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', m.group(1)):
            result["permission_query_conditions"][dt] = fn

    m = re.search(r'extend_bootinfo\s*=\s*"([^"]+)"', content)
    if m:
        result["boot_session"].append(m.group(1))

    return result


# ══════════════════════════════════════════
# GENERIC FILE SCANNER
# ══════════════════════════════════════════

IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.next', 'dist', 'build',
               'venv', 'env', '.venv', '.env', '.tox', 'target', 'vendor',
               'flowmap-out', '.claude', 'migrations', 'static', 'assets'}
IGNORE_FILES = {'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'Pipfile.lock',
                'poetry.lock', '.DS_Store'}


def scan_files(root, extensions):
    """Recursively find files matching extensions, skipping ignored dirs."""
    results = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith('.')]
        for f in sorted(filenames):
            if f in IGNORE_FILES or f.startswith('.'):
                continue
            fp = Path(dirpath) / f
            if fp.suffix in extensions:
                results.append(fp)
    return results


# ══════════════════════════════════════════
# MAIN SCAN
# ══════════════════════════════════════════

def scan_project(root, project_type):
    """Scan entire project."""
    root = Path(root)
    name = root.name
    print(f"Scanning {name} ({project_type}) at {root}...")

    # Scan Python files
    py_files_data = []
    for fp in scan_files(root, {'.py'}):
        parsed = parse_python_file(fp)
        rel = str(fp.relative_to(root))
        if parsed["endpoints"] or parsed["functions"]:
            py_files_data.append({
                "path": rel, "name": fp.stem,
                "endpoints": parsed["endpoints"], "functions": parsed["functions"],
                "classes": parsed.get("classes", []), "purpose": parsed["purpose"],
            })
            if parsed["endpoints"]:
                print(f"  {rel}: {len(parsed['endpoints'])} endpoints")

    # Scan JS/TS files
    js_files_data = []
    for fp in scan_files(root, {'.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte'}):
        parsed = parse_js_ts_file(fp)
        rel = str(fp.relative_to(root))
        js_files_data.append({
            "path": rel, "name": fp.stem,
            "calls": parsed["calls"], "routes": parsed["routes"],
            "exports": parsed.get("exports", []), "purpose": parsed["purpose"],
        })
        if parsed["calls"]:
            print(f"  {rel}: {len(parsed['calls'])} API calls")

    # Project-specific extras
    hook_files = []
    doctypes = []
    pages = []
    hooks_config = {}

    if project_type == "frappe":
        hooks_config, hook_files, doctypes, pages = scan_frappe(root)
        for hf in hook_files:
            print(f"  {hf['path']}: {len(hf['handlers'])} hooks")
        if doctypes:
            print(f"  DocTypes: {len(doctypes)}")
        if pages:
            print(f"  Pages: {len(pages)}")

    elif project_type == "django":
        # Scan for models, views, urls
        for fp in scan_files(root, {'.py'}):
            if fp.name in ('urls.py', 'views.py', 'models.py', 'serializers.py'):
                parsed = parse_python_file(fp)
                rel = str(fp.relative_to(root))
                if parsed["classes"]:
                    for cls in parsed["classes"]:
                        doctypes.append({"name": cls["name"], "folder": fp.parent.name,
                                         "is_child": False, "fields": 0})

    elif project_type == "node":
        pkg = parse_config_file(root / "package.json")
        if pkg:
            print(f"  package.json: {pkg.get('name', 'unnamed')}")

    # Split py_files into api (has endpoints) and non-api
    api_files = [f for f in py_files_data if f["endpoints"]]
    other_py = [f for f in py_files_data if not f["endpoints"] and f not in api_files]

    # Stats
    total_endpoints = sum(len(f["endpoints"]) for f in api_files)
    total_hooks = sum(len(f["handlers"]) for f in hook_files)
    total_calls = sum(len(f["calls"]) for f in js_files_data)
    total_functions = sum(len(f["functions"]) for f in py_files_data)

    return {
        "project": {"name": name, "type": project_type, "root": str(root)},
        "stats": {
            "endpoints": total_endpoints,
            "hooks": total_hooks,
            "functions": total_functions,
            "doctypes": len(doctypes),
            "pages": len(pages),
            "js_files": len(js_files_data),
            "py_files": len(py_files_data),
            "api_calls": total_calls,
        },
        "hooks_config": hooks_config,
        "api_files": api_files,
        "hook_files": hook_files,
        "js_files": js_files_data,
        "doctypes": doctypes,
        "pages": pages,
        "other_py": other_py,
    }


# ══════════════════════════════════════════
# HTML GENERATION
# ══════════════════════════════════════════

def generate_html(data):
    """Generate self-contained HTML from scan data."""
    template_path = Path(__file__).parent / "template.html"
    if template_path.exists():
        template = template_path.read_text(errors="ignore")
        html = template.replace("__FLOW_DATA__", json.dumps(data))
        html = html.replace("__PROJECT_NAME__", data["project"]["name"])
        return html

    # Minimal fallback
    return f"<html><body><pre>{json.dumps(data, indent=2)}</pre></body></html>"


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════

def main():
    start = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    start = Path(start).resolve()

    if not start.exists():
        print(f"Error: Path not found: {start}")
        sys.exit(1)

    root, project_type = detect_project(start)
    print(f"  Detected: {project_type} project")

    data = scan_project(root, project_type)

    # Output
    out_dir = root / "flowmap-out"
    if root.name == root.parent.name:
        out_dir = root.parent / "flowmap-out"
    out_dir.mkdir(exist_ok=True)

    out_file = out_dir / "index.html"
    out_file.write_text(generate_html(data))

    json_file = out_dir / "flowmap-data.json"
    json_file.write_text(json.dumps(data, indent=2))

    s = data["stats"]
    print(f"\n✅ Generated: {out_file}")
    print(f"   {s['endpoints']} endpoints, {s['hooks']} hooks, {s['functions']} functions")
    print(f"   {s['py_files']} Python, {s['js_files']} JS/TS files, {s['api_calls']} API calls")
    print(f"   Open: file://{out_file}")


if __name__ == "__main__":
    main()
