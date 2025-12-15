# ============================
# 通用 Makefile 模板 (E2E Test Focused)
# ============================

# ============================
# 配置变量（接入新项目时仅需修改这里）
# ============================


BACKEND_REQ   := backend/requirements.txt
BACKEND_DIR   := backend
FRONTEND_DIR  := frontend
TEST_DIR      := autotest_framework/test_cases/
REPORT_DIR    := allure-results

# 服务端口配置（CI 和本地统一）
BACKEND_PORT  := 8000
FRONTEND_PORT := 5173

# API 合同测试配置
OPENAPI_SPEC := api-specs/openapi.yaml
BASE_URL     := http://127.0.0.1:$(BACKEND_PORT)
# 数据库连接（给 FastAPI 用）
# CI 环境中 MySQL 服务就是 root/password@127.0.0.1:3306/reader_db
SQLALCHEMY_DATABASE_URL ?= sqlite:///./reader.db
IMAGE_NAME ?= online-reader-backend
IMAGE_TAG  ?= $(shell git rev-parse --short HEAD)

.PHONY: deps lint test contract-test build start-deps stop-deps ci help

# ============================
# 1. 安装依赖
#    说明：包含 Backend (pip) 和 Frontend (npm) 的依赖安装
# ============================
deps:
	@echo ">>> Installing Backend Dependencies..."
	pip install -r $(BACKEND_REQ)
	@echo ">>> Installing Playwright browsers (chromium)..."
	python -m playwright install chromium
	@echo ">>> Installing Frontend Dependencies..."
	cd $(FRONTEND_DIR) && npm install

# ============================
# 2. 启动/关闭测试依赖（DB/Redis/服务等）
#    这里负责：启动后端 + 前端，并等待一段时间
# ============================
start-deps:
	@echo ">>> Starting backend & frontend services..."
	- pkill -f "uvicorn main:app" || true
	@echo ">>> Starting backend (uvicorn on port $(BACKEND_PORT))..."
	cd $(BACKEND_DIR) && \
	  SQLALCHEMY_DATABASE_URL="$(SQLALCHEMY_DATABASE_URL)" \
	  nohup uvicorn main:app --host 0.0.0.0 --port $(BACKEND_PORT) > backend.log 2>&1 &
	@echo ">>> Starting frontend (npm dev on port $(FRONTEND_PORT))..."
	cd $(FRONTEND_DIR) && \
	  nohup npm run dev -- --port $(FRONTEND_PORT) --host 0.0.0.0 > frontend.log 2>&1 &
	@echo ">>> Sleeping 30 seconds for services to start..."
	sleep 30
	@echo "✅ All services are assumed up."

stop-deps:
	@echo ">>> stop-deps is currently a no-op. Services will exit with CI job."
	@echo ">>> 如果需要，可以在这里实现 pkill/kill 等停止逻辑。"

# ============================
# 3. 代码静态检查（lint）
# ============================
lint:
	@echo ">>> Running ruff..."
	ruff check backend
	@echo ">>> Running black (check mode)..."
	black --check backend
	@echo ">>> Running mypy..."
	mypy backend
# === 覆盖率用的后端单元 / API 测试 ===
unit-test:
	@echo ">>> Running backend unit/API tests with coverage..."
	cd backend && \
	  pytest tests \
	    --cov=backend \
	    --cov-branch \
	    --cov-report=xml:../coverage.xml
# ============================
# 4. 单元/集成/E2E 测试
#    说明：运行 Pytest 并生成 Allure 报告数据
# ============================
test:
	@echo ">>> Running Tests with coverage..."
	export PYTHONPATH=$$PYTHONPATH:. && \
	pytest $(TEST_DIR) \
	  --alluredir=$(REPORT_DIR) \


# ============================
# 5. API 合同测试
# ============================
contract-test:
	@echo ">>> Running Schemathesis contract tests (FAST mode)..."
	python scripts/seed_novels.py
	schemathesis run $(OPENAPI_SPEC) \
	  --url=$(BASE_URL) \
	  --phases=fuzzing\
	  --checks=all \
	  --exclude-checks=positive_data_acceptance \
	  --max-examples=10 \
	  --request-timeout=5.0 \
	  --max-response-time=4.0

# ============================
# 6. 构建（包 / 镜像 / 前端产物）
#    说明：当前流程跳过构建步骤
# ============================
build:
	@echo ">>> Building backend Docker image $(IMAGE_NAME):$(IMAGE_TAG)..."
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) -f backend/Dockerfile backend

# ============================
# 7. 本地一键 CI（开发自测）
#    说明：依次执行 依赖安装 -> 启动服务 -> 测试
# ============================
ci: deps start-deps test

# ============================
# 8. 帮助
# ============================
help:
	@echo "可用目标："
	@echo "  make deps           安装前后端依赖"
	@echo "  make start-deps     启动后端和前端，并等待一段时间"
	@echo "  make stop-deps      停止依赖（当前只是占位）"
	@echo "  make lint           静态检查（当前跳过）"
	@echo "  make test           运行 E2E 测试并生成 Allure 结果"
	@echo "  make contract-test  API 合同测试（当前跳过）"
	@echo "  make build          构建产物（当前跳过）"
	@echo "  make ci             一键执行 CI 流程 (deps + start-deps + test)"
