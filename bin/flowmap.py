#!/usr/bin/env python3
"""Flowmap — Zero-token project architecture visualizer.

Reads project files, injects them into the Flowmap HTML app so it auto-scans on open.

Usage:
    python3 flowmap.py [project_path]
    python3 flowmap.py .
    flowmap /path/to/project
"""

import os
import sys
import json
from pathlib import Path

IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.next', 'dist', 'build',
               'venv', 'env', '.venv', '.env', '.tox', 'target', 'vendor',
               'flowmap-out', '.claude', 'migrations', 'static', 'assets',
               '.mypy_cache', '.pytest_cache', '.idea', '.vscode', 'coverage',
               '.nyc_output', '.parcel-cache', '.turbo', '.svelte-kit'}

CODE_EXTS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte',
             '.go', '.rs', '.java', '.kt', '.kts', '.scala', '.cs',
             '.php', '.rb', '.dart', '.ex', '.exs',
             '.html', '.htm', '.css', '.scss', '.less',
             '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg',
             '.sql', '.graphql', '.gql', '.proto', '.prisma',
             '.md', '.mdx', '.rst', '.txt',
             '.dockerfile', '.tf', '.sh', '.bash', '.zsh',
             '.xml', '.svg', '.env.example', '.gitignore'}

MAX_FILES = 2000
MAX_FILE_SIZE = 200_000  # 200KB per file


def should_skip_dir(name):
    return name in IGNORE_DIRS or name.startswith('.')


def want_file(name):
    if name.startswith('.') and name not in ('.env.example', '.gitignore'):
        return False
    ext = Path(name).suffix.lower()
    if ext in CODE_EXTS:
        return True
    # Special files without extension
    lname = name.lower()
    return lname in ('dockerfile', 'makefile', 'procfile', 'gemfile',
                     'rakefile', 'vagrantfile', 'jenkinsfile', 'pipfile')


def collect_files(root):
    """Walk project and read all source files."""
    root = Path(root).resolve()
    files = {}
    count = 0

    for dirpath, dirnames, filenames in os.walk(root):
        # Filter directories
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]

        for fname in sorted(filenames):
            if count >= MAX_FILES:
                break
            if not want_file(fname):
                continue

            fpath = Path(dirpath) / fname
            rel = str(fpath.relative_to(root))

            try:
                size = fpath.stat().st_size
                if size > MAX_FILE_SIZE:
                    continue
                text = fpath.read_text(errors='ignore')
                files[rel] = text
                count += 1
            except Exception:
                continue

    return files


def generate(root, files, project_name):
    """Generate HTML with pre-loaded project data."""
    template_path = Path(__file__).parent / "template.html"
    if not template_path.exists():
        print(f"Error: template.html not found at {template_path}")
        sys.exit(1)

    template = template_path.read_text(errors='ignore')

    # Inject project data as _FLOWMAP_PRELOAD before the main <script>
    preload_data = json.dumps({
        "name": project_name,
        "files": files,
    })
    # Escape </script> inside JSON strings to prevent breaking the HTML
    preload_data = preload_data.replace('</script>', '<\\/script>')
    preload_data = preload_data.replace('</Script>', '<\\/Script>')
    preload_data = preload_data.replace('</SCRIPT>', '<\\/SCRIPT>')

    inject_script = f'<script>const _FLOWMAP_PRELOAD = {preload_data};</script>\n'

    # Insert before the main <script> tag
    html = template.replace('<script>\n/* ---', inject_script + '<script>\n/* ---', 1)
    if inject_script not in html:
        # Fallback: insert before </body>
        html = template.replace('</body>', inject_script + '</body>')
    return html


def main():
    start = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    start = Path(start).resolve()

    if not start.exists():
        print(f"Error: Path not found: {start}")
        sys.exit(1)

    # Find project root (go up if needed to find package.json, hooks.py, etc.)
    root = start
    indicators = ['package.json', 'hooks.py', 'manage.py', 'go.mod', 'Cargo.toml',
                  'setup.py', 'pyproject.toml', 'app.py', 'main.py']
    # If start is a subdir (like myapp/myapp), check parent
    if not any((root / f).exists() for f in indicators):
        if any((root.parent / f).exists() for f in indicators):
            root = root.parent

    project_name = root.name
    print(f"⚡ Flowmap — scanning {project_name}")
    print(f"  Path: {root}")

    files = collect_files(root)
    print(f"  Files: {len(files)}")

    if not files:
        print("  No source files found!")
        sys.exit(1)

    # Count by extension
    ext_counts = {}
    for f in files:
        ext = Path(f).suffix or Path(f).name
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
    top_exts = sorted(ext_counts.items(), key=lambda x: -x[1])[:5]
    print(f"  Top: {', '.join(f'{e}({c})' for e, c in top_exts)}")

    # Generate
    html = generate(root, files, project_name)

    out_dir = root / "flowmap-out"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "index.html"
    out_file.write_text(html)

    print(f"\n✅ Generated: {out_file}")
    print(f"   Open: file://{out_file}")

    # Try to open in browser
    import platform
    if platform.system() == 'Darwin':
        os.system(f'open "{out_file}"')
    elif platform.system() == 'Linux':
        os.system(f'xdg-open "{out_file}" 2>/dev/null &')


if __name__ == "__main__":
    main()
