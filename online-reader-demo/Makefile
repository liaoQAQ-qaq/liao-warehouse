# ============================
# Universal Makefile Skeleton v2.0
# - Lint: ruff/black/mypy
# - Unit/API tests: pytest + coverage.xml (Codecov)
# - E2E(UI) tests: pytest + Allure
# - Contract tests: Schemathesis (fuzzing)
# - Docker build
# ============================

BACKEND_DIR    := backend
FRONTEND_DIR   := frontend

BACKEND_REQ    := $(BACKEND_DIR)/requirements.txt

TEST_API_DIR   := $(BACKEND_DIR)/tests
TEST_E2E_DIR   := autotest_framework/test_cases

REPORT_DIR     := allure-results

BACKEND_PORT   := 8000
FRONTEND_PORT  := 5173

OPENAPI_SPEC   := api-specs/openapi.yaml
BASE_URL       := http://127.0.0.1:$(BACKEND_PORT)

SQLALCHEMY_DATABASE_URL ?= sqlite:///./reader.db

IMAGE_NAME ?= online-reader-backend
IMAGE_TAG  ?= $(shell git rev-parse --short HEAD)

.PHONY: deps deps-backend deps-frontend deps-playwright \
        lint unit-test e2e-test contract-test \
        start-deps stop-deps build ci help

deps: deps-backend deps-frontend deps-playwright

deps-backend:
	@echo ">>> [deps-backend] pip install -r $(BACKEND_REQ)"
	pip install -r $(BACKEND_REQ)

deps-frontend:
	@echo ">>> [deps-frontend] npm install"
	cd $(FRONTEND_DIR) && npm install

deps-playwright:
	@echo ">>> [deps-playwright] install chromium"
	python -m playwright install chromium

# ----------------------------
# Start backend + frontend
# ----------------------------
start-deps:
	@echo ">>> [start-deps] start backend & frontend"
	- pkill -f "uvicorn" || true
	@echo ">>> backend: uvicorn backend.main:app :$(BACKEND_PORT)"
	PYTHONPATH=. SQLALCHEMY_DATABASE_URL="$(SQLALCHEMY_DATABASE_URL)" \
	  nohup uvicorn backend.main:app --host 0.0.0.0 --port $(BACKEND_PORT) > $(BACKEND_DIR)/backend.log 2>&1 &
	@echo ">>> frontend: npm dev :$(FRONTEND_PORT)"
	cd $(FRONTEND_DIR) && \
	  nohup npm run dev -- --port $(FRONTEND_PORT) --host 0.0.0.0 > ../$(FRONTEND_DIR)/frontend.log 2>&1 &
	@echo ">>> sleep 30s"
	sleep 30
	@echo "✅ services assumed up"

stop-deps:
	@echo ">>> [stop-deps] no-op (CI exits will stop processes)"

# ----------------------------
# Lint
# ----------------------------
lint:
	@echo ">>> [lint] ruff/black/mypy"
	ruff check $(BACKEND_DIR)
	black --check $(BACKEND_DIR)
	MYPYPATH=. mypy --explicit-package-bases $(BACKEND_DIR)

# ----------------------------
# Unit/API tests + Coverage
# Output: coverage.xml (for Codecov)
# ----------------------------
unit-test:
	@echo ">>> [unit-test] pytest $(TEST_API_DIR) + coverage.xml"
	PYTHONPATH=. pytest $(TEST_API_DIR) \
	  --cov=$(BACKEND_DIR) \
	  --cov-branch \
	  --cov-report=xml:coverage.xml

# ----------------------------
# E2E(UI) tests + Allure
# IMPORTANT: clean allure dir to avoid stale results
# ----------------------------
e2e-test:
	@echo ">>> [e2e-test] pytest UI tests + allure-results (clean)"
	PYTHONPATH=. pytest $(TEST_E2E_DIR) \
	  --alluredir=$(REPORT_DIR) \
	  --clean-alluredir

# ----------------------------
# Contract tests (FAST fuzzing)
# ----------------------------
contract-test:
	@echo ">>> [contract-test] schemathesis fuzzing"
	python scripts/seed_novels.py
	schemathesis run $(OPENAPI_SPEC) \
	  --url=$(BASE_URL) \
	  --phases=fuzzing \
	  --checks=all \
	  --exclude-checks=positive_data_acceptance \
	  --max-examples=10 \
	  --request-timeout=5.0 \
	  --max-response-time=4.0

# ----------------------------
# Docker build (backend)
# ----------------------------
build:
	@echo ">>> [build] docker build $(IMAGE_NAME):$(IMAGE_TAG)"
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) -f $(BACKEND_DIR)/Dockerfile $(BACKEND_DIR)

# One-click local flow (optional)
ci: deps start-deps unit-test e2e-test

help:
	@echo "make deps          - install deps"
	@echo "make lint          - ruff/black/mypy"
	@echo "make start-deps    - start backend+frontend"
	@echo "make unit-test     - backend tests + coverage.xml"
	@echo "make e2e-test      - UI tests + allure-results"
	@echo "make contract-test - schemathesis fuzzing"
	@echo "make build         - docker build backend image"
