#!/usr/bin/env python3
"""Flowmap — Zero-token project architecture visualizer.

Scans ALL project files, extracts only code-relevant content (strips large
non-code content), injects into the HTML template for browser rendering.

For large projects: keeps full content of code files (.py, .js, .ts etc),
but for config/data files (.json, .md, .yaml etc) only keeps first few
lines as a stub — enough for the parser to detect models/types but not
enough to bloat the HTML.

Usage:
    python3 flowmap.py [project_path]
    flowmap /path/to/project
"""

import os
import sys
import json
import zlib
import base64
from pathlib import Path

IGNORE_DIRS = {'.git', 'node_modules', '__pycache__', '.next', 'dist', 'build',
               'venv', 'env', '.venv', '.env', '.tox', 'target', 'vendor',
               'flowmap-out', '.claude', 'static', 'assets', 'locale',
               '.mypy_cache', '.pytest_cache', '.idea', '.vscode', 'coverage',
               '.nyc_output', '.parcel-cache', '.turbo', '.svelte-kit',
               'site-packages', 'egg-info', 'patches', 'translations'}

CODE_EXTS = {'.py', '.js', '.ts', '.jsx', '.tsx', '.vue', '.svelte',
             '.go', '.rs', '.java', '.kt', '.kts', '.scala', '.cs',
             '.php', '.rb', '.dart', '.ex', '.exs'}

CONFIG_EXTS = {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg',
               '.html', '.htm', '.css', '.scss', '.less',
               '.sql', '.graphql', '.gql', '.proto', '.prisma',
               '.md', '.mdx', '.rst', '.txt',
               '.dockerfile', '.tf', '.sh', '.bash', '.zsh',
               '.xml', '.svg', '.env.example', '.gitignore'}

ALL_EXTS = CODE_EXTS | CONFIG_EXTS

# Code files: keep full content (up to this size)
MAX_CODE_SIZE = 150_000    # 150KB
# Config/data files: keep only a stub
MAX_CONFIG_STUB = 500      # 500 bytes stub for JSON/YAML/MD etc
# Skip individual files larger than this
MAX_FILE_SIZE = 500_000    # 500KB absolute max


def should_skip_dir(name):
    return name in IGNORE_DIRS or name.startswith('.')


def want_file(name):
    if name.startswith('.') and name not in ('.env.example', '.gitignore'):
        return False
    # Skip test files
    lname = name.lower()
    if lname.startswith('test_') or lname.startswith('test.') or lname.endswith('_test.py'):
        return False
    ext = Path(name).suffix.lower()
    if ext in ALL_EXTS:
        return True
    return lname in ('dockerfile', 'makefile', 'procfile', 'gemfile',
                     'rakefile', 'vagrantfile', 'jenkinsfile', 'pipfile')


def collect_files(root):
    """Walk project, read ALL files. Code files get full content, others get stubs."""
    root = Path(root).resolve()
    files = {}
    total = 0
    skipped = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if not should_skip_dir(d))

        for fname in sorted(filenames):
            if not want_file(fname):
                continue

            fpath = Path(dirpath) / fname
            try:
                size = fpath.stat().st_size
                if size > MAX_FILE_SIZE:
                    skipped += 1
                    continue
            except Exception:
                continue

            rel = str(fpath.relative_to(root))
            ext = fpath.suffix.lower()

            try:
                if ext in CODE_EXTS:
                    # Code files: keep full content
                    if size <= MAX_CODE_SIZE:
                        files[rel] = fpath.read_text(errors='ignore')
                    else:
                        # Truncate very large code files but keep enough for parsing
                        text = fpath.read_text(errors='ignore')[:MAX_CODE_SIZE]
                        files[rel] = text + f'\n# ... truncated ({size} bytes total)\n'
                else:
                    # Config/data/docs: keep just a stub for type detection
                    text = fpath.read_text(errors='ignore')
                    if len(text) <= MAX_CONFIG_STUB:
                        files[rel] = text
                    else:
                        files[rel] = text[:MAX_CONFIG_STUB] + '\n/* ... truncated */\n'
                total += 1
            except Exception:
                continue

    return files, total, skipped


def generate(root, files, project_name):
    """Generate HTML with pre-loaded project data."""
    template_path = Path(__file__).parent / "template.html"
    if not template_path.exists():
        print(f"Error: template.html not found at {template_path}")
        sys.exit(1)

    template = template_path.read_text(errors='ignore')

    preload_json = json.dumps({"name": project_name, "files": files})
    raw_mb = len(preload_json) / (1024 * 1024)

    # For large payloads: compress with zlib + base64 to shrink HTML size
    if raw_mb > 1.0:
        compressed = zlib.compress(preload_json.encode('utf-8'), 9)
        encoded = base64.b64encode(compressed).decode('ascii')
        comp_mb = len(encoded) / (1024 * 1024)
        print(f"  Data: {raw_mb:.1f} MB raw → {comp_mb:.1f} MB compressed ({100 - comp_mb/raw_mb*100:.0f}% smaller)")
        inject_script = f'<script>const _FLOWMAP_COMPRESSED = "{encoded}";</script>\n'
    else:
        # Small projects: inline JSON directly (no decompression overhead)
        preload_data = preload_json
        preload_data = preload_data.replace('</script>', '<\\/script>')
        preload_data = preload_data.replace('</Script>', '<\\/Script>')
        preload_data = preload_data.replace('</SCRIPT>', '<\\/SCRIPT>')
        print(f"  HTML data size: {raw_mb:.1f} MB")
        inject_script = f'<script>const _FLOWMAP_PRELOAD = {preload_data};</script>\n'

    html = template.replace('<script>\n/* ---', inject_script + '<script>\n/* ---', 1)
    if inject_script not in html:
        html = template.replace('</body>', inject_script + '</body>')
    return html


def main():
    start = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    start = Path(start).resolve()

    if not start.exists():
        print(f"Error: Path not found: {start}")
        sys.exit(1)

    # Find project root
    root = start
    indicators = ['package.json', 'hooks.py', 'manage.py', 'go.mod', 'Cargo.toml',
                  'setup.py', 'pyproject.toml', 'app.py', 'main.py']
    if not any((root / f).exists() for f in indicators):
        if any((root.parent / f).exists() for f in indicators):
            root = root.parent

    project_name = root.name
    print(f"⚡ Flowmap — scanning {project_name}")
    print(f"  Path: {root}")

    files, total, skipped = collect_files(root)
    print(f"  Files: {total} scanned ({len(files)} included, {skipped} skipped)")

    if not files:
        print("  No source files found!")
        sys.exit(1)

    # Stats
    ext_counts = {}
    code_count = 0
    for f in files:
        ext = Path(f).suffix.lower()
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
        if ext in CODE_EXTS:
            code_count += 1
    top_exts = sorted(ext_counts.items(), key=lambda x: -x[1])[:5]
    print(f"  Code files: {code_count} (full content)")
    print(f"  Top: {', '.join(f'{e}({c})' for e, c in top_exts)}")

    html = generate(root, files, project_name)

    out_dir = root / "flowmap-out"
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "index.html"
    out_file.write_text(html)

    print(f"\n✅ Generated: {out_file}")
    print(f"   Open: file://{out_file}")

    import platform
    if platform.system() == 'Darwin':
        os.system(f'open "{out_file}"')
    elif platform.system() == 'Linux':
        os.system(f'xdg-open "{out_file}" 2>/dev/null &')


if __name__ == "__main__":
    main()
