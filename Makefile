# Makefile — single entry point for all project operations
# dev and prod use different compose files — this wraps the complexity

# variables
COMPOSE_DEV  = docker compose
COMPOSE_PROD = docker compose -f docker-compose.yml -f docker-compose.prod.yml

# ── Dev ──────────────────────────────────────────────────────────────────────

dev:
	$(COMPOSE_DEV) up -d

dev-build:
	$(COMPOSE_DEV) up -d --build

down:
	$(COMPOSE_DEV) down

down-volumes:
	$(COMPOSE_DEV) down -v

# ── Testing ───────────────────────────────────────────────────────────────────

test:
	$(COMPOSE_DEV) exec api python3 -m pytest tests/ -v

test-auth:
	$(COMPOSE_DEV) exec api python3 -m pytest tests/test_auth.py -v

test-auction:
	$(COMPOSE_DEV) exec api python3 -m pytest tests/test_auction.py -v

test-bid:
	$(COMPOSE_DEV) exec api python3 -m pytest tests/test_bid.py -v

# ── Database ──────────────────────────────────────────────────────────────────

migrate:
	$(COMPOSE_DEV) exec api alembic upgrade head

migrate-down:
	$(COMPOSE_DEV) exec api alembic downgrade -1

migration:
	$(COMPOSE_DEV) exec api alembic revision --autogenerate -m "$(msg)"

# ── Logs and Debug ────────────────────────────────────────────────────────────

logs:
	$(COMPOSE_DEV) logs api -f

logs-db:
	$(COMPOSE_DEV) logs db -f

logs-nginx:
	$(COMPOSE_PROD) logs nginx -f

shell:
	$(COMPOSE_DEV) exec api bash

db-shell:
	$(COMPOSE_DEV) exec db psql -U $${POSTGRES_USER} -d $${POSTGRES_DB}

# ── Production ────────────────────────────────────────────────────────────────

prod:
	$(COMPOSE_PROD) up -d --build

prod-down:
	$(COMPOSE_PROD) down

prod-logs:
	$(COMPOSE_PROD) logs api -f

# ── Status ────────────────────────────────────────────────────────────────────

ps:
	$(COMPOSE_DEV) ps

health:
	curl -s http://localhost:8000/health | python3 -m json.tool

.PHONY: dev dev-build down down-volumes test test-auth test-auction test-bid \
        migrate migrate-down migration logs logs-db logs-nginx shell db-shell \
        prod prod-down prod-logs ps health
