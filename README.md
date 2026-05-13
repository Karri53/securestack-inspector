# SecureStack Inspector

> Containerized software supply chain risk analyzer. Scans repositories for dependency vulnerabilities, Dockerfile security issues, and generates SBOMs with risk-scored executive reports.

**Status:** 🚧 Active development — Phase 1 complete

## What it does

SecureStack Inspector accepts a GitHub repository URL, clones it inside an isolated scanner container, and analyzes it for software supply chain risks:

- 📦 **Dependency analysis** — parses `requirements.txt`, `package.json`, and other manifests to identify known-vulnerable or outdated packages
- 🐳 **Dockerfile linting** — flags common security mistakes like running as root, using `latest` tags, and exposed secrets
- 📋 **SBOM generation** — produces CycloneDX-format software bills of materials
- 📊 **Risk scoring** — assigns severity levels and generates exportable executive reports

Aligned with [CISA SBOM guidance](https://www.cisa.gov/sbom) and [OWASP Software Component Verification Standard](https://owasp.org/www-project-software-component-verification-standard/).

## Architecture

A multi-container application orchestrated with Docker Compose:

| Service | Role |
|---------|------|
| `frontend` | Next.js dashboard (React + TypeScript + Tailwind) |
| `api` | FastAPI backend serving the REST API |
| `scanner-worker` | Isolated worker that runs the actual scans |
| `postgres` | Stores scan history, findings, and repo metadata |
| `redis` | Job queue between API and worker |

## Quickstart

```bash
git clone https://github.com/Karri53/securestack-inspector.git
cd securestack-inspector
cp .env.example .env
docker compose up --build
```

Then open:
- **Dashboard:** http://localhost:3000
- **API docs:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

## Tech stack

**Backend:** Python 3.12 · FastAPI · SQLAlchemy 2.0 · Pydantic v2 · Alembic
**Frontend:** Next.js 14 · TypeScript · Tailwind CSS · React
**Data:** PostgreSQL 16 · Redis 7
**Infra:** Docker · Docker Compose · GitHub Actions (CI/CD)
**Testing:** Pytest · Vitest

## License

MIT