.PHONY: deps lint test contract-test build start-deps stop-deps ci help

deps:
	@echo ">>> [1/3] Installing Backend Dependencies..."
	pip install -r backend/requirements.txt
	pip install pytest playwright allure-pytest
	playwright install chromium
	@echo ">>> [2/3] Installing Frontend Dependencies..."
	cd frontend && npm install
	@echo ">>> [3/3] Dependencies Installed."

start-deps:
	@echo ">>> Test dependencies are handled by CI/Docker."

stop-deps:
	@echo ">>> Stopping dependencies..."

lint:
	@echo ">>> Lint check skipped."

test:
	@echo ">>> Running E2E Tests..."
	export PYTHONPATH=$$PYTHONPATH:. && \
	python -m pytest autotest_framework/test_cases/ --alluredir=allure-results

contract-test:
	@echo ">>> Contract test skipped."

build:
	@echo ">>> Build skipped."

ci: deps test
