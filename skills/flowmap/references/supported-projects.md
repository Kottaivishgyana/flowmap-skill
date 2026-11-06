# Supported Project Types

## Auto-Detection Order

The scanner checks these in order:

1. **Frappe** — `hooks.py` + `modules.txt` exist
2. **Django** — `manage.py` exists
3. **Flask** — `app.py` or `wsgi.py` exists
4. **FastAPI** — `main.py` with "FastAPI" in content
5. **Node.js** — `package.json` exists
6. **Go** — `go.mod` exists
7. **Rust** — `Cargo.toml` exists
8. **Generic Python** — any `.py` files found
9. **Generic JavaScript** — any `.js`/`.ts` files found

## API Decorator Detection

Python files are scanned for these decorator patterns:

| Pattern | Framework |
|---------|-----------|
| `@app.route(...)` | Flask |
| `@router.get/post/put/delete(...)` | FastAPI |
| `@api_view(...)` | Django REST Framework |
| `@action(...)` | DRF ViewSets |
| `@require_http_methods(...)` | Django |
| `@login_required` | Django |
| `@csrf_exempt` | Django |
| `@*.whitelist(...)` | Frappe |

## JS/TS Call Detection

Frontend files are scanned for these API call patterns:

| Pattern | Type |
|---------|------|
| `fetch("url")` | Native fetch |
| `axios.get/post("url")` | Axios |
| `$.get/post/ajax("url")` | jQuery |
| `frappe.call({method: "..."})` | Frappe |
| `useQuery("key")` | React Query |
| `api.get/post("url")` | Custom API client |

## Ignored Directories

These are always skipped during scanning:
`.git`, `node_modules`, `__pycache__`, `.next`, `dist`, `build`, `venv`, `env`, `.venv`, `.env`, `.tox`, `target`, `vendor`, `flowmap-out`, `.claude`, `migrations`, `static`, `assets`
