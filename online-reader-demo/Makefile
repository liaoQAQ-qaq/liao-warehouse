# ============================
# online-reader-demo/Makefile
# ============================

.PHONY: deps lint test contract-test build start-deps stop-deps ci help

# 1. 安装依赖 (同时处理 Python 后端和 Node 前端)
deps:
	@echo ">>> [1/3] Installing Backend Dependencies..."
	pip install -r backend/requirements.txt
	pip install pytest playwright allure-pytest
	playwright install chromium

	@echo ">>> [2/3] Installing Frontend Dependencies..."
	cd frontend && npm install

	@echo ">>> [3/3] Dependencies Installed."

# 2. 启动测试依赖 (这里留空，因为 CI 中我们会用 Service 和后台进程启动)
start-deps:
	@echo ">>> Test dependencies are handled by CI/Docker."

stop-deps:
	@echo ">>> Stopping dependencies..."

# 3. 静态检查 (先跳过，以后可以加 flake8 或 eslint)
lint:
	@echo ">>> Lint check skipped."

# 4. 运行测试 (核心命令)
# 注意：这里假设后端和前端已经在后台启动了
test:
	@echo "======================================================="
	@echo "🔥 正在使用 Makefile！老板你看，我在这里！ 🔥"
	@echo "======================================================="
	# 设置 PYTHONPATH 确保能找到包，并运行 pytest
	export PYTHONPATH=$PYTHONPATH:. && \
	python -m pytest autotest_framework/test_cases/ --alluredir=allure-results

# 5. 合同测试 (暂时跳过)
contract-test:
	@echo ">>> Contract test skipped."

# 6. 构建 (暂时跳过)
build:
	@echo ">>> Build skipped."

# 7. 本地一键执行 (仅供参考，本地跑需要你先手动启动前后端)
ci: deps test