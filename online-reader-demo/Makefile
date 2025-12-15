# ============================
# Universal Makefile Skeleton v2.1
# - Lint: ruff + black + mypy
# - Unit(API) tests: pytest + coverage.xml (Codecov)
# - E2E(UI) tests: pytest + Playwright + Allure
# - Contract tests: Schemathesis (fuzzing only)
# ============================

SHELL := /bin/bash
.DEFAULT_GOAL := help

# ----------------------------
# Project layout (only edit here for new projects)
# ----------------------------
BACKEND_DIR   ?= backend
FRONTEND_DIR  ?= frontend

BACKEND_REQ   ?= $(BACKEND_DIR)/requirements.txt
TEST_API_DIR  ?= $(BACKEND_DIR)/tests
TEST_E2E_DIR  ?= autotest_framework/test_cases

REPORT_DIR    ?= allure-results

# Ports (CI & local unified)
BACKEND_HOST  ?= 0.0.0.0
BACKEND_PORT  ?= 8000
FRONTEND_HOST ?= 0.0.0.0
FRONTEND_PORT ?= 5173

# Uvicorn app import path (IMPORTANT: package path)
BACKEND_APP   ?= backend.main:app

# DB URL (FastAPI reads it as env)
SQLALCHEMY_DATABASE_URL ?= sqlite:///./reader.db

# OpenAPI / Contract testing
OPENAPI_SPEC ?= api-specs/openapi.yaml
BASE_URL     ?= http://127.0.0.1:$(BACKEND_PORT)
SCHEM_MAX_EXAMPLES ?= 10
SCHEM_TIMEOUT ?= 5.0
SCHEM_MAX_RT ?= 4.0

# Docker
IMAGE_NAME ?= online-reader-backend
IMAGE_TAG  ?= $(shell git rev-parse --short HEAD)

.PHONY: deps deps-backend deps-frontend playwright-install \
        lint fmt mypy unit-test e2e-test \
        start-backend start-frontend wait-backend wait-frontend start-deps stop-deps \
        contract-test build ci help

# ----------------------------
# Dependencies
# ----------------------------
deps: deps-backend deps-frontend playwright-install

deps-backend:
	@echo ">>> [deps-backend] pip install -r $(BACKEND_REQ)"
	pip install -r $(BACKEND_REQ)

deps-frontend:
	@echo ">>> [deps-frontend] npm install"
	cd $(FRONTEND_DIR) && npm install

playwright-install:
	@echo ">>> [playwright] install chromium (browsers)"
	python -m playwright install chromium

# ----------------------------
# Lint / Format
# ----------------------------
lint:
	@echo ">>> [lint] ruff"
	ruff check $(BACKEND_DIR)
	@echo ">>> [lint] black"
	black --check $(BACKEND_DIR)
	@echo ">>> [lint] mypy"
	MYPYPATH=. mypy --explicit-package-bases $(BACKEND_DIR)

fmt:
	@echo ">>> [fmt] black + ruff --fix"
	black $(BACKEND_DIR)
	ruff check $(BACKEND_DIR) --fix

mypy:
	@echo ">>> [mypy] mypy"
	MYPYPATH=. mypy --explicit-package-bases $(BACKEND_DIR)

# ----------------------------
# Unit/API tests (coverage for Codecov)
# NOTE:
#   - 只跑 backend/tests (不要放 Playwright 的 page fixture 用例在这里)
#   - 产出 coverage.xml 在项目根目录 (online-reader-demo/coverage.xml)
# ----------------------------
unit-test:
	@echo ">>> [unit-test] pytest backend/tests + coverage.xml"
	PYTHONPATH=. pytest $(TEST_API_DIR) \
	  --cov=$(BACKEND_DIR) \
	  --cov-branch \
	  --cov-report=xml:coverage.xml

# ----------------------------
# E2E(UI) tests (Allure)
# NOTE:
#   - 只跑 autotest_framework/test_cases
#   - 这里不产覆盖率（覆盖率由 unit-test 负责）
# ----------------------------
e2e-test:
	@echo ">>> [e2e-test] pytest UI tests + allure-results"
	PYTHONPATH=. pytest $(TEST_E2E_DIR) \
	  --alluredir=$(REPORT_DIR)

# ----------------------------
# Start/Stop services
# - 解决你之前端口占用：每次启动前先 kill
# - 解决 curl 卡住：强制 --noproxy '*'
# ----------------------------
start-backend:
	@echo ">>> [start-backend] kill old uvicorn (best effort)"
	- pkill -f "uvicorn.*$(BACKEND_APP)" || true
	- pkill -f "uvicorn.*backend\.main:app" || true
	@echo ">>> [start-backend] start uvicorn on :$(BACKEND_PORT)"
	SQLALCHEMY_DATABASE_URL="$(SQLALCHEMY_DATABASE_URL)" \
	PYTHONPATH=. nohup uvicorn $(BACKEND_APP) \
	  --host $(BACKEND_HOST) --port $(BACKEND_PORT) > $(BACKEND_DIR)/backend.log 2>&1 &

start-frontend:
	@echo ">>> [start-frontend] kill old npm dev (best effort)"
	- pkill -f "npm.*dev" || true
	@echo ">>> [start-frontend] start npm dev on :$(FRONTEND_PORT)"
	cd $(FRONTEND_DIR) && nohup npm run dev -- --host $(FRONTEND_HOST) --port $(FRONTEND_PORT) > frontend.log 2>&1 &

wait-backend:
	@echo ">>> [wait-backend] waiting backend $(BASE_URL)/novels/ ..."
	@i=0; \
	while [ $$i -lt 60 ]; do \
	  if curl -fsS --noproxy '*' "$(BASE_URL)/novels/" > /dev/null; then \
	    echo "✅ backend ready"; exit 0; \
	  fi; \
	  i=$$((i+1)); sleep 1; \
	done; \
	echo "❌ backend not ready in time"; \
	echo "----- backend log -----"; tail -n 120 $(BACKEND_DIR)/backend.log || true; \
	exit 1

wait-frontend:
	@echo ">>> [wait-frontend] waiting frontend http://127.0.0.1:$(FRONTEND_PORT)/ ..."
	@i=0; \
	while [ $$i -lt 60 ]; do \
	  if curl -fsS --noproxy '*' "http://127.0.0.1:$(FRONTEND_PORT)/" > /dev/null; then \
	    echo "✅ frontend ready"; exit 0; \
	  fi; \
	  i=$$((i+1)); sleep 1; \
	done; \
	echo "❌ frontend not ready in time"; \
	echo "----- frontend log -----"; tail -n 120 $(FRONTEND_DIR)/frontend.log || true; \
	exit 1

start-deps: start-backend start-frontend wait-backend wait-frontend
	@echo "✅ all services ready"

stop-deps:
	@echo ">>> [stop-deps] stopping services (best effort)"
	- pkill -f "uvicorn.*$(BACKEND_APP)" || true
	- pkill -f "uvicorn.*backend\.main:app" || true
	- pkill -f "npm.*dev" || true
	@echo "✅ stop done"

# ----------------------------
# Contract tests (Schemathesis)
# - fuzzing only (stateful 容易被“删除后仍可读”等业务语义打爆)
# - 如需 seed：确保 scripts/seed_novels.py 可运行
# ----------------------------
contract-test:
	@echo ">>> [contract-test] seed + schemathesis fuzzing"
	PYTHONPATH=. python scripts/seed_novels.py
	schemathesis run $(OPENAPI_SPEC) \
	  --url=$(BASE_URL) \
	  --phases=fuzzing \
	  --checks=all \
	  --exclude-checks=positive_data_acceptance \
	  --max-examples=$(SCHEM_MAX_EXAMPLES) \
	  --request-timeout=$(SCHEM_TIMEOUT) \
	  --max-response-time=$(SCHEM_MAX_RT)

# ----------------------------
# Docker build
# ----------------------------
build:
	@echo ">>> [build] docker build $(IMAGE_NAME):$(IMAGE_TAG)"
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) -f $(BACKEND_DIR)/Dockerfile $(BACKEND_DIR)

# ----------------------------
# Local CI shortcut
# ----------------------------
ci: deps lint unit-test start-deps e2e-test contract-test stop-deps

help:
	@echo ""
	@echo "Targets:"
	@echo "  make deps              安装后端+前端依赖 + playwright"
	@echo "  make lint              ruff + black + mypy"
	@echo "  make unit-test         后端 API/单元测试 + coverage.xml (Codecov)"
	@echo "  make start-deps        启动后端+前端，并等待可用"
	@echo "  make e2e-test          UI E2E 测试 + allure-results"
	@echo "  make contract-test     Schemathesis 合同测试（fuzzing only）"
	@echo "  make stop-deps         停止后端+前端（best effort）"
	@echo "  make ci                本地一键跑全套"
	@echo ""
