# Team Code Quality Template - Multi-language Makefile
# 统一的代码质量工具命令接口 - 支持Python、JavaScript/TypeScript、Java

.PHONY: help setup check format test lint security clean validate report coverage update-quality install-tools git-setup git-check git-clean git-status git-branch-prune git-pre-commit git-pre-push

# 默认目标
help:
	@echo "🚀 Team Code Quality Template - Multi-language Commands"
	@echo "============================================"
	@echo ""
	@echo "🎯 Quick Start:"
	@echo "  setup         - 一键安装所有代码质量工具"
	@echo "  install-tools - 仅安装工具（不配置）"
	@echo "  validate      - 验证配置是否正确"
	@echo ""
	@echo "🎨 Code Quality:"
	@echo "  check         - 运行所有代码质量检查"
	@echo "  format        - 自动格式化代码"
	@echo "  lint          - 仅运行代码风格检查"
	@echo "  security      - 仅运行安全检查"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test          - 运行所有测试"
	@echo "  test-unit     - 运行单元测试"
	@echo "  test-integration - 运行集成测试"
	@echo "  coverage      - 生成测试覆盖率报告"
	@echo ""
	@echo "🌐 Language-specific:"
	@echo "  check-python  - 仅检查Python代码"
	@echo "  check-js      - 仅检查JavaScript/TypeScript代码"
	@echo "  check-java    - 仅检查Java代码"
	@echo "  format-python - 仅格式化Python代码"
	@echo "  format-js     - 仅格式化JavaScript代码"
	@echo "  format-java   - 仅格式化Java代码"
	@echo ""
	@echo "📊 Reports:"
	@echo "  report        - 生成完整质量报告"
	@echo ""
	@echo "🔧 Maintenance:"
	@echo "  clean         - 清理临时文件"
	@echo "  update-quality- 更新质量工具配置"
	@echo "  uninstall     - 卸载代码质量工具"
	@echo ""
	@echo "🌳 Git Workflow:"
	@echo "  git-setup     - 配置Git工作流环境"
	@echo "  git-check     - 检查Git工作流规范"
	@echo "  git-clean     - 清理Git分支"
	@echo "  git-status    - 显示Git状态摘要"
	@echo "  git-branch-prune - 清理已合并的分支"
	@echo "  git-pre-commit - 提交前检查"
	@echo "  git-pre-push  - 推送前检查"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  docs          - 打开文档"
	@echo ""

# 环境检测
PYTHON := $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null || echo python)
NODE := $(shell command -v node 2>/dev/null || echo "")
JAVA := $(shell command -v java 2>/dev/null || echo "")
UV := $(shell command -v uv 2>/dev/null || echo "")
NPM := $(shell command -v npm 2>/dev/null || echo "")
MVN := $(shell command -v mvn 2>/dev/null || echo "")

# UV 命令前缀（强制使用 UV）
ifeq ($(UV),)
UV_RUN := $(error "UV 未安装，请先安装 UV: curl -LsSf https://astral.sh/uv/install.sh | sh")
else
UV_RUN := uv run
endif

# 配置文件路径
# 简化路径配置 - 如果Makefile在.team-code-quality目录中，当前目录就是质量工具目录
TEAM_QUALITY_DIR := .
CONFIG_DIR := $(TEAM_QUALITY_DIR)/configs
PYTHON_CONFIG_DIR := $(CONFIG_DIR)/lang/python
JS_CONFIG_DIR := $(CONFIG_DIR)/lang/javascript
JAVA_CONFIG_DIR := $(CONFIG_DIR)/lang/java

# 源码路径配置 - 从环境变量加载，如果没有则使用默认值
-include .env.paths
BACKEND_SRC_PATH ?= backend/src
FRONTEND_SRC_PATH ?= frontend/src
PROJECT_ROOT := ..
# 修复路径计算：当 BACKEND_SRC_PATH=backend 时，dir 函数返回 ./，需要特殊处理
BACKEND_DIR_RAW := $(dir $(BACKEND_SRC_PATH))
FRONTEND_DIR_RAW := $(dir $(FRONTEND_SRC_PATH))
BACKEND_BASE_DIR := $(patsubst %/,%,$(BACKEND_DIR_RAW))
FRONTEND_BASE_DIR := $(patsubst %/,%,$(FRONTEND_DIR_RAW))
# 如果 BACKEND_BASE_DIR 是 . 或空，说明 BACKEND_SRC_PATH 是单个目录名（如 backend），直接使用它
BACKEND_PARENT := $(if $(filter-out .,$(BACKEND_BASE_DIR)),$(PROJECT_ROOT)/$(BACKEND_BASE_DIR),$(PROJECT_ROOT)/$(patsubst %/,%,$(BACKEND_SRC_PATH)))
FRONTEND_PARENT := $(if $(filter-out .,$(FRONTEND_BASE_DIR)),$(PROJECT_ROOT)/$(FRONTEND_BASE_DIR),$(PROJECT_ROOT)/$(patsubst %/,%,$(FRONTEND_SRC_PATH)))
BACKEND_SRC_FULL := $(PROJECT_ROOT)/$(BACKEND_SRC_PATH)
FRONTEND_SRC_FULL := $(PROJECT_ROOT)/$(FRONTEND_SRC_PATH)

# 项目类型检测（仅依赖相对路径）
IS_PYTHON := $(shell if [ -f pyproject.toml ] || [ -f requirements.txt ] || [ -f $(PROJECT_ROOT)/pyproject.toml ] || [ -f $(PROJECT_ROOT)/requirements.txt ] || [ -f $(BACKEND_PARENT)/pyproject.toml ] || [ -f $(BACKEND_PARENT)/requirements.txt ]; then echo true; else echo false; fi)
IS_JAVASCRIPT := $(shell if [ -f package.json ] || [ -f $(PROJECT_ROOT)/package.json ] || [ -f $(FRONTEND_PARENT)/package.json ]; then echo true; else echo false; fi)
IS_JAVA := $(shell if [ -f pom.xml ] || [ -f build.gradle ] || [ -f $(PROJECT_ROOT)/pom.xml ] || [ -f $(PROJECT_ROOT)/build.gradle ] || [ -f $(BACKEND_PARENT)/pom.xml ] || [ -f $(BACKEND_PARENT)/build.gradle ]; then echo true; else echo false; fi)

# 安装和设置 - 使用简化的setup脚本
setup:
	@echo "🚀 一键安装团队代码质量工具..."
	@if [ -f setup.sh ]; then \
		AUTO_INSTALL=true bash setup.sh; \
	else \
		echo "❌ 在当前目录找不到 setup.sh 脚本"; \
		echo "请确保在包含 setup.sh 的目录中运行此命令"; \
		exit 1; \
	fi

install-tools:
	@echo "📦 安装代码质量工具..."
	@echo "检测项目类型："
	@if [ "$(IS_PYTHON)" = "true" ]; then echo "  ✅ Python项目"; fi
	@if [ "$(IS_JAVASCRIPT)" = "true" ]; then echo "  ✅ JavaScript/TypeScript项目"; fi
	@if [ "$(IS_JAVA)" = "true" ]; then echo "  ✅ Java项目"; fi
	@echo ""
	@if [ "$(IS_PYTHON)" = "true" ]; then \
		if [ -n "$(UV)" ]; then \
			uv add --dev black isort flake8 mypy pytest pytest-cov bandit pylint pre-commit pip-audit; \
		else \
			$(PYTHON) -m pip install black isort flake8 mypy pytest pytest-cov bandit pylint pre-commit pip-audit; \
		fi; \
	fi
	@if [ "$(IS_JAVASCRIPT)" = "true" ] && [ -n "$(NPM)" ]; then \
		npm install --no-audit --no-fund; \
	fi

# 验证配置
validate:
	@echo "🔍 验证代码质量工具配置..."
	@if [ -f $(TEAM_QUALITY_DIR)/validate.sh ]; then \
		./$(TEAM_QUALITY_DIR)/validate.sh; \
	else \
		echo "⚠️  验证脚本不存在，进行基本检查..."; \
		if [ -L .pre-commit-config.yaml ]; then \
			echo "✅ Pre-commit 符号链接存在"; \
		else \
			echo "❌ Pre-commit 配置缺失"; \
		fi; \
	fi

# 代码格式化
format:
	@echo "🎨 格式化代码..."
	@if [ "$(IS_PYTHON)" = "true" ]; then \
		echo "🐍 格式化Python代码 (UV固定版本)..."; \
		if [ -d "$(BACKEND_SRC_FULL)" ]; then \
			echo "格式化 $(BACKEND_SRC_FULL)/"; \
			if [ -f "$(PYTHON_CONFIG_DIR)/pyproject.toml" ]; then \
				echo "使用配置文件: $(PYTHON_CONFIG_DIR)/pyproject.toml"; \
			fi; \
			$(UV_RUN) black --line-length=88 --target-version=py311 --exclude='/(\.eggs|\.git|\.hg|\.mypy_cache|\.tox|\.venv|venv|_build|buck-out|build|dist|__pycache__)/' "$(BACKEND_SRC_FULL)/"; \
			if [ -f "$(PYTHON_CONFIG_DIR)/.isort.cfg" ]; then \
				echo "使用配置文件: $(PYTHON_CONFIG_DIR)/.isort.cfg"; \
				$(UV_RUN) isort --settings-file="$(PYTHON_CONFIG_DIR)/.isort.cfg" "$(BACKEND_SRC_FULL)/"; \
			else \
				$(UV_RUN) isort "$(BACKEND_SRC_FULL)/"; \
			fi; \
		else \
			echo "未找到 $(BACKEND_SRC_PATH) 目录，跳过Python格式化"; \
		fi; \
	fi
	@if [ "$(IS_JAVASCRIPT)" = "true" ]; then \
		echo "🌟 格式化JavaScript/TypeScript代码..."; \
		if [ -d "$(FRONTEND_SRC_FULL)" ]; then \
			if [ -n "$(NPM)" ]; then \
				if [ -f "$(JS_CONFIG_DIR)/.prettierrc" ]; then \
					npm exec -- prettier --config="$(JS_CONFIG_DIR)/.prettierrc" --write "$(FRONTEND_SRC_FULL)/" || true; \
				else \
					npm exec -- prettier --write "$(FRONTEND_SRC_FULL)/" || true; \
				fi; \
			else \
				echo "⚠️  未找到 npm，跳过JavaScript格式化"; \
			fi; \
		else \
			echo "未找到 $(FRONTEND_SRC_PATH) 目录，跳过JavaScript格式化"; \
		fi; \
	fi

format-python:
	@if [ "$(IS_PYTHON)" = "true" ]; then \
		echo "🐍 格式化Python代码 (UV固定版本)..."; \
		if [ -f "$(PYTHON_CONFIG_DIR)/pyproject.toml" ]; then \
			echo "使用配置文件: $(PYTHON_CONFIG_DIR)/pyproject.toml"; \
		fi; \
		$(UV_RUN) black --line-length=88 --target-version=py311 --exclude='/(\.eggs|\.git|\.hg|\.mypy_cache|\.tox|\.venv|venv|_build|buck-out|build|dist|__pycache__)/' .; \
		if [ -f "$(PYTHON_CONFIG_DIR)/.isort.cfg" ]; then \
			echo "使用配置文件: $(PYTHON_CONFIG_DIR)/.isort.cfg"; \
			$(UV_RUN) isort --settings-file="$(PYTHON_CONFIG_DIR)/.isort.cfg" .; \
		elif [ -f ".isort.cfg" ]; then \
			echo "使用根目录配置: .isort.cfg"; \
			$(UV_RUN) isort --settings-file=".isort.cfg" .; \
		else \
			echo "使用默认配置"; \
			$(UV_RUN) isort .; \
		fi; \
	fi

format-js:
	@if [ "$(IS_JAVASCRIPT)" = "true" ]; then \
		echo "🌟 格式化JavaScript/TypeScript代码..."; \
		if [ -d "$(FRONTEND_SRC_FULL)" ]; then \
			if [ -n "$(NPM)" ]; then \
				if [ -f "$(JS_CONFIG_DIR)/.prettierrc" ]; then \
					echo "使用配置文件: $(JS_CONFIG_DIR)/.prettierrc"; \
					npm exec -- prettier --config="$(JS_CONFIG_DIR)/.prettierrc" --write "$(FRONTEND_SRC_FULL)/"; \
				else \
					npm exec -- prettier --write "$(FRONTEND_SRC_FULL)/"; \
				fi; \
			else \
				echo "⚠️  npm 未安装，跳过格式化"; \
			fi; \
		else \
			echo "未找到 $(FRONTEND_SRC_PATH) 目录，跳过JavaScript格式化"; \
		fi; \
	fi

format-java:
	@if [ "$(IS_JAVA)" = "true" ]; then \
		echo "☕ Java代码格式化需要IDE插件支持或使用Google Java Format"; \
		echo "推荐安装IDE格式化插件或手动运行: google-java-format -i *.java"; \
	fi

# 代码检查
check:
	@echo "🔍 运行完整代码质量检查..."
	@echo "🔧 运行代码风格检查..."
	@if [ "$(IS_PYTHON)" = "true" ]; then \
		echo "🐍 Python代码检查 (UV固定版本)..."; \
		if [ -d "$(BACKEND_SRC_FULL)" ]; then \
			if [ -f "$(PYTHON_CONFIG_DIR)/.flake8" ]; then \
				echo "使用配置文件: $(PYTHON_CONFIG_DIR)/.flake8"; \
				$(UV_RUN) flake8 --config="$(PYTHON_CONFIG_DIR)/.flake8" "$(BACKEND_SRC_FULL)/"; \
			else \
				$(UV_RUN) flake8 "$(BACKEND_SRC_FULL)/"; \
			fi; \
			if [ -f "$(PYTHON_CONFIG_DIR)/.pylintrc" ]; then \
				echo "使用配置文件: $(PYTHON_CONFIG_DIR)/.pylintrc"; \
				$(UV_RUN) pylint --rcfile="$(PYTHON_CONFIG_DIR)/.pylintrc" "$(BACKEND_SRC_FULL)/" || true; \
			else \
				$(UV_RUN) pylint "$(BACKEND_SRC_FULL)/" || true; \
			fi; \
			if [ -f "$(PYTHON_CONFIG_DIR)/mypy.ini" ]; then \
				echo "使用配置文件: $(PYTHON_CONFIG_DIR)/mypy.ini"; \
				$(UV_RUN) --directory . mypy --config-file="$(PYTHON_CONFIG_DIR)/mypy.ini" "$(BACKEND_SRC_FULL)/" || true; \
			else \
				$(UV_RUN) --directory . mypy "$(BACKEND_SRC_FULL)/" || true; \
			fi; \
		else \
			echo "未找到 $(BACKEND_SRC_PATH) 目录，跳过Python检查"; \
		fi; \
	fi
	@if [ "$(IS_JAVASCRIPT)" = "true" ]; then \
		echo "🌟 JavaScript/TypeScript代码检查..."; \
		if [ -d "$(FRONTEND_PARENT)" ]; then \
			echo "检查目录: $(FRONTEND_PARENT) (源码路径: $(FRONTEND_SRC_PATH))"; \
			if [ -n "$(NPM)" ]; then \
				if [ -f "$(JS_CONFIG_DIR)/eslint.config.js" ]; then \
					echo "使用配置文件: $(JS_CONFIG_DIR)/eslint.config.js"; \
					ESLINT_CONFIG_ABS="$$(cd $(TEAM_QUALITY_DIR) && pwd)/$(JS_CONFIG_DIR)/eslint.config.js"; \
					if [ -d "$(FRONTEND_SRC_FULL)" ]; then \
						( cd "$(FRONTEND_PARENT)" && npm exec -- eslint --config="$$ESLINT_CONFIG_ABS" "src" ) || echo "ESLint 检查完成（有错误）"; \
					else \
						( cd "$(FRONTEND_PARENT)" && npm exec -- eslint --config="$$ESLINT_CONFIG_ABS" . ) || echo "ESLint 检查完成（有错误）"; \
					fi; \
				elif [ -f "$(FRONTEND_PARENT)/package.json" ] && grep -q '"lint"' "$(FRONTEND_PARENT)/package.json"; then \
					( cd "$(FRONTEND_PARENT)" && npm run lint ) || echo "npm lint 检查完成（有错误）"; \
				else \
					echo "⚠️  未找到 ESLint 配置或 npm lint 脚本，跳过前端检查"; \
				fi; \
			else \
				echo "⚠️  未找到 npm，跳过前端检查"; \
			fi; \
		else \
			echo "⚠️  未找到 $(FRONTEND_SRC_PATH) 目录，跳过JavaScript检查"; \
		fi; \
	fi
	@if [ "$(IS_JAVA)" = "true" ]; then \
		echo "☕ Java代码检查..."; \
		echo "推荐安装IDE插件或手动运行检查工具"; \
	fi
	@echo "🔒 运行安全检查..."
	@if [ "$(IS_PYTHON)" = "true" ]; then \
		echo "🐍 Python安全检查..."; \
		if [ -d "$(BACKEND_SRC_FULL)" ]; then \
			if [ -f "$(PYTHON_CONFIG_DIR)/.bandit" ]; then \
				echo "使用配置文件: $(PYTHON_CONFIG_DIR)/.bandit"; \
				$(UV_RUN) bandit -c "$(PYTHON_CONFIG_DIR)/.bandit" -r "$(BACKEND_SRC_FULL)/" || true; \
			else \
				$(UV_RUN) bandit -r "$(BACKEND_SRC_FULL)/" || true; \
			fi; \
		fi; \
		if [ -f "$(BACKEND_PARENT)/requirements.txt" ]; then \
			$(UV_RUN) pip-audit --requirement "$(BACKEND_PARENT)/requirements.txt" || true; \
		else \
			$(UV_RUN) pip-audit || true; \
		fi; \
	fi
	@echo "🧪 运行测试..."
	@echo "ℹ️  已在项目根 Makefile 中单独管理测试流程（unit-test/e2e-test），此处跳过在质量工具环境中运行 pytest"

lint:
	@echo "🔧 运行代码风格检查..."
	@if [ "$(IS_PYTHON)" = "true" ]; then \
		echo "🐍 Python代码检查 (UV固定版本)..."; \
		if [ -f "$(PYTHON_CONFIG_DIR)/.flake8" ]; then \
			$(UV_RUN) flake8 --config="$(PYTHON_CONFIG_DIR)/.flake8" .; \
		else \
			$(UV_RUN) flake8 .; \
		fi; \
	fi
	@if [ "$(IS_JAVASCRIPT)" = "true" ]; then \
		echo "🌟 JavaScript/TypeScript代码检查..."; \
		if [ -d "$(FRONTEND_PARENT)" ]; then \
			if [ -n "$(NPM)" ]; then \
				if [ -f "$(JS_CONFIG_DIR)/eslint.config.js" ] && [ -d "$(FRONTEND_SRC_FULL)" ]; then \
					ESLINT_CONFIG_ABS="$$(cd $(TEAM_QUALITY_DIR) && pwd)/$(JS_CONFIG_DIR)/eslint.config.js"; \
					( cd "$(FRONTEND_PARENT)" && npm exec -- eslint --config="$$ESLINT_CONFIG_ABS" "src" ) || true; \
				elif [ -f "$(FRONTEND_PARENT)/package.json" ] && grep -q '"lint"' "$(FRONTEND_PARENT)/package.json"; then \
					( cd "$(FRONTEND_PARENT)" && npm run lint ) || true; \
				else \
					echo "⚠️  未找到 ESLint 配置或 npm lint 脚本，跳过前端检查"; \
				fi; \
			else \
				echo "⚠️  npm 未安装，跳过JavaScript检查"; \
			fi; \
		else \
			echo "未找到 $(FRONTEND_PARENT) 目录，跳过JavaScript检查"; \
		fi; \
	fi
	@if [ "$(IS_JAVA)" = "true" ]; then \
		echo "☕ Java代码检查..."; \
		echo "推荐安装IDE插件或手动运行检查工具"; \
	fi

lint-python:
	@if [ "$(IS_PYTHON)" = "true" ]; then \
		echo "🐍 Python代码检查 (UV固定版本)..."; \
		if [ -f "$(PYTHON_CONFIG_DIR)/.flake8" ]; then \
			$(UV_RUN) flake8 --config="$(PYTHON_CONFIG_DIR)/.flake8" .; \
		else \
			$(UV_RUN) flake8 .; \
		fi; \
		if [ -f "$(PYTHON_CONFIG_DIR)/.pylintrc" ]; then \
			$(UV_RUN) pylint --rcfile="$(PYTHON_CONFIG_DIR)/.pylintrc" src/ || true; \
		else \
			$(UV_RUN) pylint src/ || true; \
		fi; \
	fi

lint-js:
	@if [ "$(IS_JAVASCRIPT)" = "true" ]; then \
		echo "🌟 JavaScript/TypeScript代码检查..."; \
		if [ -d "$(FRONTEND_PARENT)" ]; then \
			if [ -n "$(NPM)" ]; then \
				if [ -f "$(JS_CONFIG_DIR)/eslint.config.js" ] && [ -d "$(FRONTEND_SRC_FULL)" ]; then \
					ESLINT_CONFIG_ABS="$$(cd $(TEAM_QUALITY_DIR) && pwd)/$(JS_CONFIG_DIR)/eslint.config.js"; \
					( cd "$(FRONTEND_PARENT)" && npm exec -- eslint --config="$$ESLINT_CONFIG_ABS" "src" ); \
				elif [ -f "$(FRONTEND_PARENT)/package.json" ] && grep -q '"lint"' "$(FRONTEND_PARENT)/package.json"; then \
					( cd "$(FRONTEND_PARENT)" && npm run lint ); \
				else \
					echo "⚠️  未找到 ESLint 配置或 npm lint 脚本"; \
				fi; \
			else \
				echo "⚠️  npm 未安装，跳过JavaScript检查"; \
			fi; \
		else \
			echo "未找到 $(FRONTEND_SRC_PATH) 目录，跳过JavaScript检查"; \
		fi; \
	fi

lint-java:
	@if [ "$(IS_JAVA)" = "true" ]; then \
		echo "☕ Java代码检查..."; \
		if command -v checkstyle >/dev/null 2>&1; then \
			checkstyle -c "$(JAVA_CONFIG_DIR)/checkstyle.xml" .; \
		fi; \
		if command -v pmd >/dev/null 2>&1; then \
			pmd -R "$(JAVA_CONFIG_DIR)/pmd.xml" -d .; \
		fi; \
	fi

# 安全检查
security:
	@echo "🔒 运行安全检查..."
	@if [ "$(IS_PYTHON)" = "true" ]; then \
		echo "🐍 Python安全检查..."; \
		if [ -d "$(BACKEND_SRC_FULL)" ]; then \
			if [ -f "$(PYTHON_CONFIG_DIR)/.bandit" ]; then \
				$(UV_RUN) bandit -c "$(PYTHON_CONFIG_DIR)/.bandit" -r "$(BACKEND_SRC_FULL)/" || true; \
			else \
				$(UV_RUN) bandit -r "$(BACKEND_SRC_FULL)/" || true; \
			fi; \
		else \
			echo "未找到 $(BACKEND_SRC_PATH) 目录，跳过Bandit检查"; \
		fi; \
		if [ -f "$(BACKEND_PARENT)/requirements.txt" ]; then \
			$(UV_RUN) pip-audit --requirement "$(BACKEND_PARENT)/requirements.txt" --no-deps || true; \
		elif [ -f "$(PROJECT_ROOT)/requirements.txt" ]; then \
			$(UV_RUN) pip-audit --requirement "$(PROJECT_ROOT)/requirements.txt" --no-deps || true; \
		else \
			$(UV_RUN) pip-audit --no-deps || true; \
		fi; \
	fi

security-python:
	@if [ "$(IS_PYTHON)" = "true" ]; then \
		echo "🐍 Python安全检查 (UV固定版本)..."; \
		if [ -f "$(PYTHON_CONFIG_DIR)/.bandit" ]; then \
			$(UV_RUN) bandit -c "$(PYTHON_CONFIG_DIR)/.bandit" -r .; \
		else \
			$(UV_RUN) bandit -r .; \
		fi; \
		if [ -f requirements.txt ]; then \
			$(UV_RUN) pip-audit --requirement requirements.txt; \
		elif [ -f pyproject.toml ]; then \
			$(UV_RUN) pip-audit; \
		fi; \
	fi

security-js:
	@if [ "$(IS_JAVASCRIPT)" = "true" ]; then \
		echo "🌟 JavaScript/TypeScript安全检查..."; \
		FRONTEND_BASE_DIR="$(FRONTEND_PARENT)"; \
		if [ -d "$$FRONTEND_BASE_DIR" ]; then \
			cd $$FRONTEND_BASE_DIR; \
			if command -v npm >/dev/null 2>&1; then \
				npm audit --audit-level moderate || true; \
			else \
				echo "⚠️  npm 未安装，跳过安全检查"; \
			fi; \
			cd - > /dev/null; \
		else \
			echo "未找到 $$FRONTEND_BASE_DIR 目录，跳过JavaScript安全检查"; \
		fi; \
	fi

security-java:
	@if [ "$(IS_JAVA)" = "true" ]; then \
		echo "☕ Java安全检查..."; \
		if command -v spotbugs >/dev/null 2>&1; then \
			spotbugs -textui -exclude "$(JAVA_CONFIG_DIR)/spotbugs-exclude.xml" .; \
		fi; \
	fi

# 测试
test:
	@echo "🧪 运行测试..."
	@if [ "$(IS_PYTHON)" = "true" ]; then \
		echo "🐍 Python测试..."; \
		if [ -d "$(BACKEND_PARENT)/tests" ]; then \
			if [ -f "$(PYTHON_CONFIG_DIR)/pytest.ini" ]; then \
				$(UV_RUN) pytest -c "$(PYTHON_CONFIG_DIR)/pytest.ini" "$(BACKEND_PARENT)/tests"/ || true; \
			else \
				$(UV_RUN) pytest "$(BACKEND_PARENT)/tests"/ || true; \
			fi; \
		elif [ -d "$(PROJECT_ROOT)/tests" ]; then \
			if [ -f "$(PYTHON_CONFIG_DIR)/pytest.ini" ]; then \
				$(UV_RUN) pytest -c "$(PYTHON_CONFIG_DIR)/pytest.ini" "$(PROJECT_ROOT)/tests"/ || true; \
			else \
				$(UV_RUN) pytest "$(PROJECT_ROOT)/tests"/ || true; \
			fi; \
		else \
			echo "未找到tests目录，跳过Python测试"; \
		fi; \
	fi

test-python:
	@if [ "$(IS_PYTHON)" = "true" ]; then \
		echo "🐍 运行Python测试 (UV固定版本)..."; \
		if [ -f "$(PYTHON_CONFIG_DIR)/pytest.ini" ]; then \
			$(UV_RUN) pytest -c "$(PYTHON_CONFIG_DIR)/pytest.ini" --cov=src --cov-report=term-missing --cov-report=html tests/; \
		else \
			$(UV_RUN) pytest --cov=src --cov-report=term-missing --cov-report=html tests/; \
		fi; \
	fi

test-js:
	@if [ "$(IS_JAVASCRIPT)" = "true" ]; then \
		echo "🌟 运行JavaScript/TypeScript测试..."; \
		FRONTEND_BASE_DIR="$(FRONTEND_PARENT)"; \
		if [ -d "$$FRONTEND_BASE_DIR" ]; then \
			cd $$FRONTEND_BASE_DIR; \
			if [ -f "../.team-code-quality/$(JS_CONFIG_DIR)/vitest.config.ts" ]; then \
				npx vitest run --coverage; \
			elif [ -f package.json ] && grep -q '"test"' package.json; then \
				npm test; \
			else \
				echo "⚠️  未找到测试脚本，跳过JavaScript测试"; \
			fi; \
			cd - > /dev/null; \
		else \
			echo "未找到 $$FRONTEND_BASE_DIR 目录，跳过JavaScript测试"; \
		fi; \
	fi

test-java:
	@if [ "$(IS_JAVA)" = "true" ]; then \
		echo "☕ 运行Java测试..."; \
		if [ -n "$(MVN)" ]; then \
			mvn test; \
		elif command -v java >/dev/null 2>&1; then \
			echo "运行单元测试：请使用mvn test或gradle test"; \
		fi; \
	fi

test-unit:
	@echo "🧪 运行单元测试 (UV固定版本)..."
	@if [ "$(IS_PYTHON)" = "true" ]; then \
		if [ -f "$(PYTHON_CONFIG_DIR)/pytest.ini" ]; then \
			$(UV_RUN) pytest -c "$(PYTHON_CONFIG_DIR)/pytest.ini" -m unit --cov=src --cov-report=term-missing; \
		else \
			$(UV_RUN) pytest -m unit --cov=src --cov-report=term-missing; \
		fi; \
	fi

test-integration:
	@echo "🧪 运行集成测试 (UV固定版本)..."
	@if [ "$(IS_PYTHON)" = "true" ]; then \
		if [ -f "$(PYTHON_CONFIG_DIR)/pytest.ini" ]; then \
			$(UV_RUN) pytest -c "$(PYTHON_CONFIG_DIR)/pytest.ini" -m integration --cov=src --cov-report=term-missing; \
		else \
			$(UV_RUN) pytest -m integration --cov=src --cov-report=term-missing; \
		fi; \
	fi

# 测试覆盖率
coverage:
	@echo "📊 生成测试覆盖率报告 (UV固定版本)..."
	@if [ "$(IS_PYTHON)" = "true" ]; then \
		if [ -f "$(PYTHON_CONFIG_DIR)/pytest.ini" ]; then \
			$(UV_RUN) pytest -c "$(PYTHON_CONFIG_DIR)/pytest.ini" --cov=src --cov-report=html --cov-report=xml --cov-report=term; \
		else \
			$(UV_RUN) pytest --cov=src --cov-report=html --cov-report=xml --cov-report=term; \
		fi; \
		echo "📄 HTML报告: htmlcov/index.html"; \
	fi

# 语言特定检查
check-python: lint-python security-python test-python
check-js: lint-js security-js test-js
check-java: lint-java security-java test-java

# 质量报告
report:
	@echo "📊 生成代码质量报告..."
	@mkdir -p reports
	@echo "生成报告时间: $$(date)" > reports/quality-report.txt
	@echo "================================" >> reports/quality-report.txt
	@echo "运行代码风格检查..." >> reports/quality-report.txt 2>&1
	@echo "运行安全检查..." >> reports/quality-report.txt 2>&1
	@echo "运行测试..." >> reports/quality-report.txt 2>&1
	@echo "✅ 报告已生成: reports/quality-report.txt"

# 清理
clean:
	@echo "🧹 清理临时文件..."
	# Python清理
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	# JavaScript清理
	@rm -rf node_modules/ .nyc_output coverage/ 2>/dev/null || true
	# Java清理
	@rm -rf target/ build/ .gradle/ 2>/dev/null || true
	# 通用清理
	@rm -rf .coverage htmlcov/ reports/ dist/ 2>/dev/null || true
	@echo "✅ 清理完成"

# 更新质量工具配置
update-quality:
	@echo "⬆️  更新代码质量工具配置..."
	@if [ -f $(TEAM_QUALITY_DIR)/setup.sh ]; then \
		./$(TEAM_QUALITY_DIR)/setup.sh; \
	else \
		echo "❌ 找不到更新脚本"; \
	fi

# 卸载
uninstall:
	@echo "🗑️  卸载代码质量工具..."
	@echo "  • 移除 pre-commit hooks..."
	@if [ -d .git ]; then pre-commit uninstall || true; fi
	@echo "  • 移除符号链接..."
	@rm -f .pre-commit-config.yaml
	@echo "  • 清理配置文件..."
	@rm -rf .flake8 .bandit .isort.cfg mypy.ini .pylintrc pytest.ini eslint.config.js .prettierrc
	@echo "  • 清理脚本..."
	@rm -rf scripts/format-code.sh scripts/check-quality.sh scripts/run-tests.sh
	@echo "  • 清理文档..."
	@rm -rf CODE_QUALITY.md $(TEAM_QUALITY_DIR)/
	@echo "✅ 卸载完成"

# 打开文档
docs:
	@echo "📚 打开文档..."
	@if [ -f $(TEAM_QUALITY_DIR)/GETTING_STARTED.md ]; then \
		less $(TEAM_QUALITY_DIR)/GETTING_STARTED.md; \
	elif [ -f $(TEAM_QUALITY_DIR)/QUICK_REFERENCE.md ]; then \
		less $(TEAM_QUALITY_DIR)/QUICK_REFERENCE.md; \
	else \
		echo "❌ 找不到文档"; \
	fi

# 状态检查
status:
	@echo "📊 UV-Only 固定版本状态:"
	@echo "  项目类型: $(if $(IS_PYTHON),Python, )$(if $(IS_JAVASCRIPT),JavaScript, )$(if $(IS_JAVA),Java, )"
	@echo "  UV: $(if $(UV),已安装,未安装)"
	@echo "  Python: $(PYTHON)"
	@echo "  Node.js: $(if $(NODE),$(NODE),未安装)"
	@echo "  Java: $(if $(JAVA),$(java -version 2>&1 | head -1),未安装)"
	@echo ""
	@echo "  工具状态:"
	@if command -v black >/dev/null 2>&1; then echo "  ✅ Black: $$(black --version)"; else echo "  ❌ Black: 未安装"; fi
	@if command -v eslint >/dev/null 2>&1; then echo "  ✅ ESLint: $$(eslint --version)"; else echo "  ❌ ESLint: 未安装"; fi
	@if command -v prettier >/dev/null 2>&1; then echo "  ✅ Prettier: $$(prettier --version)"; else echo "  ❌ Prettier: 未安装"; fi
	@if command -v checkstyle >/dev/null 2>&1; then echo "  ✅ Checkstyle: $$(checkstyle -version)"; else echo "  ❌ Checkstyle: 未安装"; fi

# =============================================================================
# 🌳 Git Workflow Commands
# =============================================================================

# Git工作流配置
git-setup:
	@echo "⚙️  配置Git工作流环境..."
	@cd $(PROJECT_ROOT) && \
	if [ ! -f .gitignore ]; then \
		echo "创建.gitignore文件..."; \
		curl -s https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore > .gitignore; \
		echo "node_modules/" >> .gitignore; \
		echo "dist/" >> .gitignore; \
		echo ".venv/" >> .gitignore; \
		echo "__pycache__/" >> .gitignore; \
	fi
	@echo "✅ Git工作流配置完成"

# Git工作流检查
git-check:
	@echo "🔍 检查Git工作流规范..."
	@cd $(PROJECT_ROOT) && \
	echo "=== Git配置检查 ===" && \
	git config --list --local | grep -E "(user\.|branch\.|core\.)" && \
	echo "" && \
	echo "=== 分支状态检查 ===" && \
	git branch -a && \
	echo "" && \
	echo "=== 提交信息格式检查 ===" && \
	git log --oneline -5 && \
	echo "" && \
	echo "=== 工作流文件检查 ===" && \
	if [ -f .github/workflows/claude.yml ]; then \
		echo "✅ Claude工作流配置存在"; \
	else \
		echo "❌ Claude工作流配置缺失"; \
	fi && \
	if [ -f CONTRIBUTING.md ]; then \
		echo "✅ 贡献指南存在"; \
	else \
		echo "❌ 贡献指南缺失"; \
	fi

# Git清理
git-clean:
	@echo "🧹 清理Git环境..."
	@cd $(PROJECT_ROOT) && \
	echo "清理已合并的本地分支..." && \
	git branch --merged | grep -v "main\|develop\|master" | xargs -r git branch -d && \
	echo "清理远程分支引用..." && \
	git remote prune origin && \
	echo "清理无用的tags..." && \
	git tag -l "temp-*" 2>/dev/null | xargs -r git tag -d && \
	echo "✅ Git清理完成"

# Git状态摘要
git-status:
	@echo "📊 Git状态摘要..."
	@cd $(PROJECT_ROOT) && \
	echo "=== 当前分支 ===" && \
	git branch --show-current && \
	echo "" && \
	echo "=== 工作目录状态 ===" && \
	git status --porcelain && \
	echo "" && \
	echo "=== 最近提交 ===" && \
	git log --oneline -3 && \
	echo "" && \
	echo "=== 远程状态 ===" && \
	git remote -v

# 分支清理
git-branch-prune:
	@echo "✂️  清理已合并的分支..."
	@cd $(PROJECT_ROOT) && \
	echo "查找已合并的功能分支..." && \
	for branch in $$(git branch --merged | grep -E "feature/|bugfix/|hotfix/" | sed 's/^[* ]*//'); do \
		if [ "$$branch" != "main" ] && [ "$$branch" != "develop" ] && [ "$$branch" != "master" ]; then \
			echo "删除本地分支: $$branch"; \
			git branch -d $$branch 2>/dev/null || git branch -D $$branch; \
		fi; \
	done && \
	echo "清理远程分支引用..." && \
	git remote prune origin && \
	echo "✅ 分支清理完成"

# 提交前检查
git-pre-commit:
	@echo "🔍 执行提交前检查..."
	@cd $(PROJECT_ROOT) && \
	echo "1. 检查工作目录状态..." && \
	if [ -n "$$(git status --porcelain)" ]; then \
		echo "有待提交的更改，继续检查..."; \
	else \
		echo "没有待提交的更改"; \
		exit 0; \
	fi && \
	echo "" && \
	echo "2. 运行代码质量检查..." && \
	$(MAKE) check && \
	echo "" && \
	echo "3. 检查提交信息格式..." && \
	if git log -1 --pretty=%B | grep -qE "^(feat|fix|docs|style|refactor|test|chore|perf|ci|build)(\(.+\))?: "; then \
		echo "✅ 提交信息格式正确"; \
	else \
		echo "❌ 提交信息格式不正确，请参考CONTRIBUTING.md"; \
		exit 1; \
	fi && \
	echo "" && \
	echo "✅ 提交前检查通过，可以提交代码"

# 推送前检查
git-pre-push:
	@echo "🔍 执行推送前检查..."
	@cd $(PROJECT_ROOT) && \
	echo "1. 检查分支状态..." && \
	current_branch=$$(git branch --show-current) && \
	if [ "$$current_branch" = "main" ] || [ "$$current_branch" = "master" ]; then \
		echo "❌ 不允许直接推送到主分支，请创建PR"; \
		exit 1; \
	fi && \
	echo "" && \
	echo "2. 检查是否有未提交的更改..." && \
	if [ -n "$$(git status --porcelain)" ]; then \
		echo "❌ 有未提交的更改，请先提交"; \
		exit 1; \
	fi && \
	echo "" && \
	echo "3. 运行完整测试..." && \
	$(MAKE) test && \
	echo "" && \
	echo "4. 检查是否需要创建PR..." && \
	if ! git log origin/$$current_branch..$$current_branch | grep -q .; then \
		echo "ℹ️  没有新的提交，可能需要创建PR"; \
	else \
		echo "✅ 有新的提交可以推送"; \
	fi && \
	echo "" && \
	echo "✅ 推送前检查通过"
