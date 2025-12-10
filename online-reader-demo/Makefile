# ============================
# 通用 Makefile 模板 (E2E Test Focused)
# ============================
# ============================
# 配置变量（接入新项目时仅需修改这里）
# ============================
BACKEND_REQ   := backend/requirements.txt
FRONTEND_DIR  := frontend
TEST_DIR      := autotest_framework/test_cases/
REPORT_DIR    := allure-results
.PHONY: deps lint test contract-test build start-deps stop-deps ci help

# ============================
# 1. 安装依赖
#    说明：包含 Backend (pip/playwright) 和 Frontend (npm) 的依赖安装
# ============================
deps:
	@echo ">>> Installing Backend Dependencies..."
	pip install -r $(BACKEND_REQ)  # 使用变量
	@echo ">>> Installing Frontend Dependencies..."
	cd $(FRONTEND_DIR) && npm install # 使用变量

# ============================
# 2. 启动/关闭测试依赖（DB/Redis 等）
#    说明：当前环境由 CI/Docker 接管，故此处仅做占位或提示
# ============================
start-deps:
	@echo ">>> Test dependencies are handled by CI/Docker."

stop-deps:
	@echo ">>> Stopping dependencies..."

# ============================
# 3. 代码静态检查（lint）
#    说明：当前流程跳过 lint 检查
# ============================
lint:
	@echo ">>> Lint check skipped."

# ============================
# 4. 单元/集成/E2E 测试
#    说明：运行 Pytest 并生成 Allure 报告数据
# ============================
test:
	@echo ">>> Running Tests..."
	export PYTHONPATH=$$PYTHONPATH:. && \
	python -m pytest $(TEST_DIR) --alluredir=$(REPORT_DIR) # 使用变量

# ============================
# 5. API 合同测试
#    说明：当前流程跳过合同测试
# ============================
contract-test:
	@echo ">>> Contract test skipped."

# ============================
# 6. 构建（包 / 镜像 / 前端产物）
#    说明：当前流程跳过构建步骤
# ============================
build:
	@echo ">>> Build skipped."

# ============================
# 7. 本地一键 CI（开发自测）
#    说明：依次执行 依赖安装 -> 测试
# ============================
ci: deps test

# ============================
# 8. 帮助
# ============================
help:
	@echo "可用目标："
	@echo "  make deps           安装前后端及 Playwright 依赖"
	@echo "  make start-deps     启动测试依赖（当前由 CI 处理）"
	@echo "  make stop-deps      停止测试依赖"
	@echo "  make lint           静态检查（当前跳过）"
	@echo "  make test           运行 E2E 测试并生成 Allure 结果"
	@echo "  make contract-test  API 合同测试（当前跳过）"
	@echo "  make build          构建产物（当前跳过）"
	@echo "  make ci             一键执行 CI 流程 (deps + test)"