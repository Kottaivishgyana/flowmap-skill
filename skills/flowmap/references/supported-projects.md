# Supported Languages & Frameworks

## Languages (auto-detected from file extension)
Python, JavaScript, TypeScript, JSX, TSX, Go, Rust, Java, Kotlin, Scala, C#, PHP, Ruby, Dart, Elixir, Prisma, SQL, GraphQL, Protobuf, YAML, Docker, Terraform, HTML, CSS, Markdown

## Frameworks (auto-detected from code patterns)

| Framework | Detection |
|-----------|-----------|
| Flask | `@app.route`, `Flask(` |
| Django | `manage.py`, `urls.py`, `@api_view` |
| FastAPI | `@router.get/post`, `FastAPI(` |
| Express | `app.get/post`, `router.` |
| NestJS | `@Controller`, `@Get/@Post` |
| Next.js | `next.config`, `pages/` |
| React | `import React`, `useState` |
| Vue | `.vue` files, `defineComponent` |
| Svelte | `.svelte` files |
| Spring Boot | `@RestController`, `@RequestMapping` |
| Laravel | `Route::get`, `artisan` |
| Rails | `routes.rb`, `rails` |
| Frappe | `hooks.py`, `@frappe.whitelist` |
| Actix/Rocket | `#[get]`, `#[post]` |
| Gin/Echo | `r.GET`, `e.GET` |
| Phoenix | `pipe_through`, `get/post` |

## Edge Types
| Type | Visual | Detection |
|------|--------|-----------|
| Import | Gray solid | `import`, `require`, `from`, `use` |
| HTTP | Blue dashed | `fetch`, `axios`, API calls |
| Event | Red dotted | Event emitters, hooks, signals |
| Data | Green dotted | Model references, DB queries |

## Layer Classification
| Layer | Color | Examples |
|-------|-------|---------|
| UI | Yellow | Components, pages, views |
| API | Blue | Routes, controllers, endpoints |
| Service | Purple | Business logic, services |
| Event | Red | Hooks, signals, middleware |
| Data | Green | Models, schemas, migrations |
| Infra | Orange | Docker, CI/CD, deploy |
| Config | Gray | Settings, env, manifests |
| Test | Cyan | Test files, specs |
| Docs | Gray | README, docs, comments |
