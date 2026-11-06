# Supported Project Types

## Frappe / ERPNext
**Detection**: `hooks.py` + `modules.txt` in app root

**What it scans**:
- `hooks.py` → doc_events, app_include_js, doctype_js, permission_query_conditions, boot_session, fixtures
- `api/*.py` → `@frappe.whitelist()` endpoints, function definitions
- `public/js/*.js` → `frappe.call()`, `frappe.xcall()`, `frappe.set_route()`
- `*/doctype/*/` → DocType JSON files (name, fields, child tables)
- `*/page/*/` → Custom Page JSON files

**Connections mapped**:
- JS `frappe.call({method: "app.api.module.function"})` → Python endpoint
- `doc_events` hook chains (autoname → validate → on_submit)
- Permission query conditions per DocType
- Boot session extensions

## Django
**Detection**: `manage.py` + `settings.py`

**What it scans**:
- `urls.py` → URL patterns and views
- `views.py` → View functions and classes
- `models.py` → Model definitions
- `serializers.py` → DRF serializers
- `templates/` → Template files

## Node.js / React
**Detection**: `package.json` + `src/`

**What it scans**:
- `package.json` → dependencies, scripts
- `src/**/*.{js,ts,jsx,tsx}` → imports, exports, API calls
- `routes/` or `pages/` → Route definitions

## Generic Python
**Detection**: `*.py` files

**What it scans**:
- Function definitions and decorators
- Import statements
- Class definitions
