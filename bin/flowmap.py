#!/usr/bin/env python3
"""Flowmap — Zero-token project architecture visualizer.

Scans a Frappe app folder, parses hooks/APIs/JS, generates interactive HTML.
No AI needed. Pure code parsing.

Usage:
    python3 ~/.claude/skills/flowmap/flowmap.py [app_path]

    # From inside a Frappe app:
    python3 ~/.claude/skills/flowmap/flowmap.py .

    # Specific path:
    python3 ~/.claude/skills/flowmap/flowmap.py /path/to/apps/myapp/myapp
"""

import os
import re
import sys
import json
from pathlib import Path


def find_app_root(start_path):
    """Find Frappe app root by looking for hooks.py."""
    p = Path(start_path).resolve()
    # Check if hooks.py is here
    if (p / "hooks.py").exists():
        return p
    # Check subdirectories (e.g., given myapp/, look in myapp/myapp/)
    for child in p.iterdir():
        if child.is_dir() and (child / "hooks.py").exists():
            return child
    return None


def parse_hooks(hooks_path):
    """Parse hooks.py for doc_events, app_include_js, etc."""
    with open(hooks_path) as f:
        content = f.read()

    result = {
        "app_include_js": [],
        "app_include_css": [],
        "doctype_js": {},
        "doc_events": {},
        "permission_query_conditions": {},
        "boot_session": [],
        "fixtures": [],
        "override_whitelisted_methods": {},
        "scheduler_events": {},
    }

    # app_include_js
    m = re.search(r'app_include_js\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if m:
        result["app_include_js"] = re.findall(r'"([^"]+)"', m.group(1))

    # app_include_css
    m = re.search(r'app_include_css\s*=\s*\[(.*?)\]', content, re.DOTALL)
    if m:
        result["app_include_css"] = re.findall(r'"([^"]+)"', m.group(1))

    # doctype_js - parse the dict
    m = re.search(r'doctype_js\s*=\s*\{(.*?)\}', content, re.DOTALL)
    if m:
        for dt, js in re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', m.group(1)):
            result["doctype_js"][dt] = js

    # doc_events - nested dict
    m = re.search(r'doc_events\s*=\s*\{(.*?)\n\}', content, re.DOTALL)
    if m:
        block = m.group(1)
        # Find each doctype block
        for dt_match in re.finditer(r'"([^"]+)"\s*:\s*\{([^}]+)\}', block):
            dt = dt_match.group(1)
            events = {}
            for ev, handler in re.findall(r'"(\w+)"\s*:\s*"([^"]+)"', dt_match.group(2)):
                events[ev] = handler
            # Also handle list handlers
            for ev, handlers in re.findall(r'"(\w+)"\s*:\s*\[(.*?)\]', dt_match.group(2), re.DOTALL):
                events[ev] = re.findall(r'"([^"]+)"', handlers)
            if events:
                result["doc_events"][dt] = events

    # permission_query_conditions
    m = re.search(r'permission_query_conditions\s*=\s*\{(.*?)\}', content, re.DOTALL)
    if m:
        for dt, fn in re.findall(r'"([^"]+)"\s*:\s*"([^"]+)"', m.group(1)):
            result["permission_query_conditions"][dt] = fn

    # extend_bootinfo
    m = re.search(r'extend_bootinfo\s*=\s*"([^"]+)"', content)
    if m:
        result["boot_session"].append(m.group(1))

    # fixtures
    m = re.search(r'fixtures\s*=\s*\[(.*?)\n\]', content, re.DOTALL)
    if m:
        # Simple strings
        result["fixtures"] = re.findall(r'"([^"]+)"', m.group(1))

    return result


def parse_python_file(filepath):
    """Parse a Python file for whitelisted endpoints and functions."""
    with open(filepath) as f:
        content = f.read()
        lines = content.split('\n')

    endpoints = []
    functions = []

    for i, line in enumerate(lines, 1):
        # @frappe.whitelist()
        if '@frappe.whitelist' in line:
            # Next non-decorator line should be def
            for j in range(i, min(i + 5, len(lines) + 1)):
                fn_match = re.match(r'\s*def\s+(\w+)\s*\((.*?)\)', lines[j - 1])
                if fn_match:
                    name = fn_match.group(1)
                    args_str = fn_match.group(2)
                    args = [a.strip().split('=')[0].strip() for a in args_str.split(',') if a.strip() and a.strip() != 'self']
                    args = [a for a in args if a not in ('method', 'kwargs')]
                    endpoints.append({"name": name, "line": j, "args": args})
                    break

        # All def functions
        fn_match = re.match(r'def\s+(\w+)\s*\((.*?)\)', line)
        if fn_match:
            functions.append({"name": fn_match.group(1), "line": i})

    # Get module docstring as purpose
    purpose = ""
    m = re.match(r'^"""(.*?)"""', content, re.DOTALL)
    if m:
        purpose = m.group(1).strip().split('\n')[0]
    elif re.match(r"^'''(.*?)'''", content, re.DOTALL):
        m = re.match(r"^'''(.*?)'''", content, re.DOTALL)
        purpose = m.group(1).strip().split('\n')[0]

    return {"endpoints": endpoints, "functions": functions, "purpose": purpose}


def parse_js_file(filepath):
    """Parse a JS file for frappe.call, frappe.xcall, frappe.set_route calls."""
    with open(filepath) as f:
        content = f.read()
        lines = content.split('\n')

    calls = []
    routes = []

    for i, line in enumerate(lines, 1):
        # frappe.call({method: "..."}) or frappe.xcall("...")
        for m in re.finditer(r'(?:frappe\.call|frappe\.xcall)\s*\(\s*[{\"]?\s*(?:method\s*:\s*)?["\']([^"\']+)["\']', line):
            method = m.group(1)
            if method and not method.startswith('//'):
                calls.append({"method": method, "line": i})

        # frappe.set_route(...)
        for m in re.finditer(r'frappe\.set_route\s*\(\s*["\']([^"\']+)["\']', line):
            routes.append(m.group(1))

    # Get purpose from first comment block
    purpose = ""
    m = re.match(r'/\*\*?\s*\n?\s*\*?\s*(.*?)(?:\n|\*/)', content)
    if m:
        purpose = m.group(1).strip()
    elif content.startswith('//'):
        purpose = content.split('\n')[0].lstrip('/ ').strip()

    return {"calls": calls, "routes": list(set(routes)), "purpose": purpose}


def scan_doctypes(app_root):
    """Find all custom DocType folders."""
    doctypes = []
    # Look in */doctype/ folders
    for module_dir in app_root.iterdir():
        if not module_dir.is_dir():
            continue
        dt_dir = module_dir / "doctype"
        if not dt_dir.exists():
            continue
        for dt_folder in sorted(dt_dir.iterdir()):
            if not dt_folder.is_dir():
                continue
            json_file = dt_folder / f"{dt_folder.name}.json"
            if json_file.exists():
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                    name = data.get("name", dt_folder.name.replace("_", " ").title())
                    is_child = data.get("istable", 0)
                    doctypes.append({
                        "name": name,
                        "folder": dt_folder.name,
                        "is_child": bool(is_child),
                        "fields": len(data.get("fields", [])),
                    })
                except (json.JSONDecodeError, KeyError):
                    doctypes.append({"name": dt_folder.name, "folder": dt_folder.name, "is_child": False, "fields": 0})

    return doctypes


def scan_pages(app_root):
    """Find all custom Page folders."""
    pages = []
    for module_dir in app_root.iterdir():
        if not module_dir.is_dir():
            continue
        page_dir = module_dir / "page"
        if not page_dir.exists():
            continue
        for page_folder in sorted(page_dir.iterdir()):
            if not page_folder.is_dir():
                continue
            json_file = page_folder / f"{page_folder.name}.json"
            title = page_folder.name.replace("_", " ").title()
            if json_file.exists():
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                    title = data.get("title", title)
                except (json.JSONDecodeError, KeyError):
                    pass
            pages.append({"name": page_folder.name, "title": title})

    return pages


def scan_project(app_root):
    """Full project scan."""
    app_root = Path(app_root)
    app_name = app_root.name

    print(f"Scanning {app_name} at {app_root}...")

    # Parse hooks
    hooks = parse_hooks(app_root / "hooks.py")
    print(f"  hooks.py: {len(hooks['doc_events'])} doc_events, {len(hooks['doctype_js'])} doctype_js")

    # Parse API files
    api_dir = app_root / "api"
    api_files = []
    if api_dir.exists():
        for py_file in sorted(api_dir.glob("*.py")):
            if py_file.name.startswith("__"):
                continue
            parsed = parse_python_file(py_file)
            rel_path = f"api/{py_file.name}"
            api_files.append({
                "path": rel_path,
                "name": py_file.stem,
                "endpoints": parsed["endpoints"],
                "functions": parsed["functions"],
                "purpose": parsed["purpose"],
            })
            ep_count = len(parsed["endpoints"])
            if ep_count:
                print(f"  {rel_path}: {ep_count} endpoints")

    # Identify hook handler files
    hook_files = []
    hook_handlers_by_file = {}
    for dt, events in hooks["doc_events"].items():
        for event, handler in events.items():
            handlers = handler if isinstance(handler, list) else [handler]
            for h in handlers:
                parts = h.rsplit(".", 1)
                if len(parts) == 2:
                    module_path = parts[0].replace(f"{app_name}.", "").replace(".", "/") + ".py"
                    fn_name = parts[1]
                    if module_path not in hook_handlers_by_file:
                        hook_handlers_by_file[module_path] = []
                    hook_handlers_by_file[module_path].append({
                        "event": event, "doctype": dt, "fn": fn_name, "full_path": h
                    })

    # Boot session
    for h in hooks.get("boot_session", []):
        parts = h.rsplit(".", 1)
        if len(parts) == 2:
            module_path = parts[0].replace(f"{app_name}.", "").replace(".", "/") + ".py"
            if module_path not in hook_handlers_by_file:
                hook_handlers_by_file[module_path] = []
            hook_handlers_by_file[module_path].append({
                "event": "boot_session", "doctype": None, "fn": parts[1], "full_path": h
            })

    # Permission queries
    for dt, h in hooks.get("permission_query_conditions", {}).items():
        parts = h.rsplit(".", 1)
        if len(parts) == 2:
            module_path = parts[0].replace(f"{app_name}.", "").replace(".", "/") + ".py"
            if module_path not in hook_handlers_by_file:
                hook_handlers_by_file[module_path] = []
            hook_handlers_by_file[module_path].append({
                "event": "permission_query", "doctype": dt, "fn": parts[1], "full_path": h
            })

    for file_path, handlers in hook_handlers_by_file.items():
        purpose = ""
        full_path = app_root / file_path
        if full_path.exists():
            parsed = parse_python_file(full_path)
            purpose = parsed["purpose"]
        hook_files.append({
            "path": file_path,
            "name": Path(file_path).stem,
            "handlers": handlers,
            "purpose": purpose,
        })
        print(f"  {file_path}: {len(handlers)} hooks")

    # Parse JS files
    js_dir = app_root / "public" / "js"
    js_files = []
    if js_dir.exists():
        for js_file in sorted(js_dir.glob("*.js")):
            parsed = parse_js_file(js_file)
            rel_path = f"public/js/{js_file.name}"
            js_files.append({
                "path": rel_path,
                "name": js_file.stem,
                "calls": parsed["calls"],
                "routes": parsed["routes"],
                "purpose": parsed["purpose"],
            })
            if parsed["calls"]:
                print(f"  {rel_path}: {len(parsed['calls'])} API calls")

    # Scan DocTypes
    doctypes = scan_doctypes(app_root)
    parent_doctypes = [d for d in doctypes if not d["is_child"]]
    child_doctypes = {d["name"] for d in doctypes if d["is_child"]}
    print(f"  DocTypes: {len(parent_doctypes)} parent, {len(child_doctypes)} child")

    # Scan Pages
    pages = scan_pages(app_root)
    print(f"  Pages: {len(pages)}")

    # Stats
    total_endpoints = sum(len(f["endpoints"]) for f in api_files)
    total_hooks = sum(len(f["handlers"]) for f in hook_files)
    total_calls = sum(len(f["calls"]) for f in js_files)

    return {
        "project": {"name": app_name, "type": "Frappe App", "root": str(app_root)},
        "stats": {
            "endpoints": total_endpoints,
            "hooks": total_hooks,
            "doctypes": len(parent_doctypes),
            "pages": len(pages),
            "js_files": len(js_files),
            "py_files": len(api_files) + len(hook_files),
            "api_calls": total_calls,
        },
        "hooks_config": hooks,
        "api_files": api_files,
        "hook_files": hook_files,
        "js_files": js_files,
        "doctypes": parent_doctypes,
        "child_doctypes": list(child_doctypes),
        "pages": pages,
    }


def generate_html(data):
    """Generate self-contained HTML from scan data."""
    template_path = Path(__file__).parent / "template.html"
    if template_path.exists():
        with open(template_path) as f:
            template = f.read()
        html = template.replace("__FLOW_DATA__", json.dumps(data))
        html = html.replace("__PROJECT_NAME__", data["project"]["name"])
        return html

    # Inline template if template.html doesn't exist
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Flowmap — {data['project']['name']}</title>
<style>
:root {{ --bg:#0f172a;--bg2:#1e293b;--bg3:#334155;--text:#e2e8f0;--text2:#94a3b8;--text3:#64748b;--blue:#3b82f6;--yellow:#eab308;--green:#22c55e;--red:#ef4444;--purple:#8b5cf6;--cyan:#06b6d4;--orange:#f97316;--border:#334155; }}
* {{ margin:0;padding:0;box-sizing:border-box; }}
body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);padding:24px; }}
.stats {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px;margin-bottom:24px; }}
.stat {{ padding:16px;background:var(--bg2);border-radius:10px;border:1px solid var(--border);text-align:center; }}
.stat-n {{ font-size:28px;font-weight:800;color:var(--cyan); }}
.stat-l {{ font-size:11px;color:var(--text3);margin-top:4px; }}
.section {{ margin-bottom:24px; }}
.section-title {{ font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;color:var(--text3);margin-bottom:12px; }}
.cards {{ display:flex;gap:12px;flex-wrap:wrap; }}
.card {{ padding:12px 16px;border-radius:10px;border:1px solid var(--border);background:var(--bg2);min-width:200px;max-width:300px; }}
.card-name {{ font-weight:600;font-size:14px;margin-bottom:4px; }}
.card-desc {{ font-size:11px;color:var(--text3);line-height:1.4; }}
.badge {{ font-size:10px;padding:2px 8px;border-radius:8px;margin-top:6px;display:inline-block; }}
h1 {{ font-size:24px;margin-bottom:24px;background:linear-gradient(135deg,var(--blue),var(--purple));-webkit-background-clip:text;-webkit-text-fill-color:transparent; }}
</style>
</head>
<body>
<h1>⚡ Flowmap — {data['project']['name']}</h1>
<div class="stats">
{''.join(f'<div class="stat"><div class="stat-n">{v}</div><div class="stat-l">{k.replace("_"," ").title()}</div></div>' for k,v in data['stats'].items())}
</div>

<div class="section"><div class="section-title">📡 API Endpoints</div><div class="cards">
{''.join(f"""<div class="card"><div class="card-name" style="color:var(--blue)">{f['name']}.py</div><div class="card-desc">{f['purpose']}</div>{''.join(f'<span class="badge" style="background:var(--blue)22;color:var(--blue)">{e["name"]}</span> ' for e in f['endpoints'])}</div>""" for f in data['api_files'] if f['endpoints'])}
</div></div>

<div class="section"><div class="section-title">⚡ Hooks & Events</div><div class="cards">
{''.join(f"""<div class="card"><div class="card-name" style="color:var(--red)">{f['name']}.py</div><div class="card-desc">{f['purpose']}</div>{''.join(f'<span class="badge" style="background:var(--red)22;color:var(--red)">{h["event"]}:{h["doctype"] or "boot"}</span> ' for h in f['handlers'])}</div>""" for f in data['hook_files'])}
</div></div>

<div class="section"><div class="section-title">🖥 Frontend Scripts</div><div class="cards">
{''.join(f"""<div class="card"><div class="card-name" style="color:var(--yellow)">{f['name']}.js</div><div class="card-desc">{f['purpose']}</div>{''.join(f'<span class="badge" style="background:var(--yellow)22;color:var(--yellow)">{c["method"].split(".")[-1]}</span> ' for c in f['calls'][:4])}</div>""" for f in data['js_files'])}
</div></div>

<div class="section"><div class="section-title">📋 DocTypes ({len(data['doctypes'])})</div><div class="cards">
{''.join(f"""<div class="card"><div class="card-name" style="color:var(--green)">{d['name']}</div><div class="card-desc">{d['fields']} fields</div></div>""" for d in data['doctypes'])}
</div></div>

<div class="section"><div class="section-title">📄 Pages ({len(data['pages'])})</div><div class="cards">
{''.join(f"""<div class="card"><div class="card-name" style="color:var(--purple)">{p['title']}</div></div>""" for p in data['pages'])}
</div></div>

<div style="margin-top:32px;font-size:11px;color:var(--text3);">Generated by Flowmap • {data['project']['root']}</div>
<script>const FLOW_DATA = {json.dumps(data)};</script>
</body></html>"""


def main():
    # Get app path
    if len(sys.argv) > 1:
        start = sys.argv[1]
    else:
        start = os.getcwd()

    app_root = find_app_root(start)
    if not app_root:
        print(f"Error: No Frappe app found (no hooks.py) in {start}")
        print("Usage: python3 flowmap.py /path/to/apps/myapp/myapp")
        sys.exit(1)

    # Scan
    data = scan_project(app_root)

    # Generate
    out_dir = app_root.parent / "flowmap-out"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "index.html"

    html = generate_html(data)
    with open(out_file, "w") as f:
        f.write(html)

    print(f"\n✅ Generated: {out_file}")
    print(f"   Open in browser: file://{out_file}")

    # Also save JSON data
    json_file = out_dir / "flowmap-data.json"
    with open(json_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"   JSON data: {json_file}")


if __name__ == "__main__":
    main()
