# Secure Bid Platform

A production-ready auction API built with FastAPI, PostgreSQL, and Docker. Designed to demonstrate SRE-grade engineering practices — structured observability, custom error handling, automated testing, and a complete CI/CD pipeline.

---

## Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 async |
| Migrations | Alembic |
| Authentication | JWT |
| Metrics | Prometheus |
| Reverse proxy | Nginx |
| Containerization | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Language | Python 3.12 |

---

## Quick Start

### Prerequisites
- Docker, Docker Compose, Make

### 1. Clone and configure
```bash
git clone https://github.com/josedevelops/secure-bid-platform
cd secure-bid-platform
cp .env.example .env
```

Generate a secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Start dev environment
```bash
make dev
make migrate
make health
```

API docs at http://localhost:8000/docs

---

## Make Commands

| Command | What it does |
|---|---|
| `make dev` | Start dev with hot reload |
| `make dev-build` | Rebuild and start dev |
| `make down` | Stop all containers |
| `make test` | Run full test suite |
| `make test-auth` | Run auth tests only |
| `make test-auction` | Run auction tests only |
| `make test-bid` | Run bid tests only |
| `make migrate` | Apply pending migrations |
| `make migrate-down` | Roll back one migration |
| `make migration msg="description"` | Generate new migration |
| `make logs` | Tail API logs |
| `make shell` | Shell inside API container |
| `make db-shell` | psql inside database container |
| `make health` | Check health endpoint |
| `make prod` | Start production environment |
| `make ps` | Show container status |

---

## API Endpoints

### Auth
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | /api/v1/auth/signup | None | Create account |
| POST | /api/v1/auth/login | None | Get JWT token |

### Profile
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /api/v1/profile/me | Bearer | Get my profile |
| PATCH | /api/v1/profile/me | Bearer | Update profile |
| POST | /api/v1/profile/me/password | Bearer | Change password |

### Product Types
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /api/v1/product-types/ | None | List categories |
| GET | /api/v1/product-types/{id} | None | Get category |
| POST | /api/v1/product-types/ | Admin | Create category |

### Auctions
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /api/v1/auctions/ | None | List active auctions |
| GET | /api/v1/auctions/{id} | None | Get auction |
| POST | /api/v1/auctions/ | Seller | Create auction |
| PATCH | /api/v1/auctions/{id} | Seller/Admin | Update auction |
| POST | /api/v1/auctions/{id}/close | Seller/Admin | Close auction |

### Bids
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /api/v1/bids/auction/{id} | Bearer | List bids |
| POST | /api/v1/bids/ | Bearer | Place bid |

### Admin
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /api/v1/admin/users | Admin | List all users |
| POST | /api/v1/admin/users/{id}/deactivate | Admin | Deactivate user |

### System
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | /health | None | Health check |
| GET | /metrics | Internal | Prometheus metrics |

---

## Error Response Format

All errors return a consistent JSON structure:

```json
{
  "detail": {
    "code": "MACHINE_READABLE_CODE",
    "message": "Human readable message"
  }
}
```

---

## Role System

| Role | Can do |
|---|---|
| BUYER | Browse auctions, place bids, manage own profile |
| SELLER | Everything buyer can + create and manage own auctions |
| ADMIN | Everything + manage users, create product types, close any auction |

All new accounts default to BUYER.

---

## CI/CD Pipeline

Every push to main triggers GitHub Actions:

1. Spin up postgres service container
2. Install dependencies
3. Run alembic migrations
4. Run pytest 25 tests
5. If green: SSH to server, git pull, alembic upgrade head, docker compose up prod, health check

### Required GitHub Secrets

| Secret | Description |
|---|---|
| SECRET_KEY | JWT signing key |
| SERVER_HOST | Production server IP |
| SERVER_USER | SSH username |
| SERVER_SSH_KEY | Private SSH key |
| SERVER_PORT | SSH port |

---

## Production Deployment

One-time server setup:
```bash
git clone https://github.com/josedevelops/secure-bid-platform
cd secure-bid-platform
cp .env.example .env
make prod
make migrate
```

After initial setup all deploys are automatic on push to main.

---

## Phases

| Phase | Status | Description |
|---|---|---|
| 1 Foundation | done | Project structure, Docker, dependencies |
| 2 Data Layer | done | Models, Alembic migrations |
| 3 Core Infrastructure | done | Config, security, logging, metrics |
| 4 API Contract | done | Schemas, repositories, routes |
| 5 Reliability | done | Custom errors, global handlers, test suite |
| 6 Deployment | done | Nginx, Prometheus, GitHub Actions, README |
| 7 Kubernetes | deferred | Container orchestration |
| 8 Terraform | deferred | Infrastructure as code |
