# ============================
# 通用 Makefile 模板
# ============================

.PHONY: deps lint test contract-test build start-deps stop-deps ci help
# ============================
# 1. 安装依赖（各项目必须改成自己的实现）
# ============================
deps:
	@echo "[INFO] deps not implemented, please customize in Makefile."
	# Python 项目示例（请按需取消注释并修改）：
	# python -m pip install --upgrade pip
	# pip install -r requirements.txt

	# Node 项目示例：
	# npm ci

	# Java 项目示例：
	# ./mvnw dependency:resolve

# ============================
# 2. 启动/关闭测试依赖（DB/Redis 等）
# ============================
start-deps:
	@echo "[INFO] start-deps not implemented, skip."
	# 推荐写成：
	# docker compose -f docker-compose.ci.yml up -d

stop-deps:
	@echo "[INFO] stop-deps not implemented, skip."
	# 推荐写成：
	# docker compose -f docker-compose.ci.yml down

# ============================
# 3. 代码静态检查（lint）
# ============================
lint:
	@echo "[INFO] lint not implemented, please customize."
	# Python 示例：
	# ruff check .
	# black --check .
	# mypy .

	# Node 示例：
	# npm run lint
	# npm run typecheck

# ============================
# 4. 单元/集成测试
# ============================
test:
	@echo "[INFO] test not implemented, please customize."
	# Python 示例：
	# pytest -q

	# Node 示例：
	# npm test

	# Java 示例：
	# ./mvnw test

# ============================
# 5. API 合同测试（Schemathesis / Dredd）
# ============================
contract-test:
	@echo "[INFO] contract-test not implemented, skip."
	# 示例如下（使用 Schemathesis）：
	# schemathesis run api-specs/openapi.yaml \
	#   --base-url=http://127.0.0.1:8000

# ============================
# 6. 构建（包 / 镜像 / 前端产物）
# ============================
build:
	@echo "[INFO] build not implemented, please customize."
	# Python 包示例：
	# python -m build

	# Docker 镜像示例：
	# docker build -t your-image-name:$(TAG) .

	# 前端示例：
	# npm run build

# ============================
# 7. 本地一键 CI（开发自测）
# ============================
ci: deps start-deps lint test contract-test
	@echo "[INFO] Local CI finished."
	@$(MAKE) stop-deps

# ============================
# 8. 帮助
# ============================
help:
	@echo "可用目标："
	@echo "  make deps           安装依赖"
	@echo "  make start-deps     启动测试依赖服务（DB/Redis 等）"
	@echo "  make stop-deps      停止测试依赖服务"
	@echo "  make lint           静态检查"
	@echo "  make test           单元/集成测试"
	@echo "  make contract-test  API 合同测试"
	@echo "  make build          构建产物"
	@echo "  make ci             本地一键跑 CI 流程"
