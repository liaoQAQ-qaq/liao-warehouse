#!/bin/bash

# Team Code Quality Template - UV Global + Local Virtual Environment Setup
# 团队代码质量模板 - UV全局+局部虚拟环境安装脚本

# 错误处理：只在关键步骤失败时退出
# 注意：某些非关键命令（如版本检查）可能返回非零退出码，但不影响功能
# 不使用 set -e，允许部分命令失败
set +e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# 图标定义
ICON_SUCCESS="✅"
ICON_ERROR="❌"
ICON_WARNING="⚠️"
ICON_INFO="ℹ️"
ICON_ROCKET="🚀"
ICON_PACKAGE="📦"
ICON_GEAR="⚙️"

# 日志函数
log_info() {
    echo -e "${CYAN}${ICON_INFO} $1${NC}"
}

log_success() {
    echo -e "${GREEN}${ICON_SUCCESS} $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}${ICON_WARNING} $1${NC}"
}

log_error() {
    echo -e "${RED}${ICON_ERROR} $1${NC}"
}

log_step() {
    echo -e "${BLUE}$1${NC}"
}

# 进度条函数
show_progress() {
    local current=$1
    local total=$2
    local desc=$3
    local width=50
    local percentage=$((current * 100 / total))
    local filled=$((current * width / total))
    local empty=$((width - filled))

    printf "\r${PURPLE}$desc${NC} ["
    printf "%*s" $filled | tr ' ' '█'
    printf "%*s" $empty | tr ' ' '░'
    printf "] %d%% (%d/%d)" $percentage $current $total
}

# 获取相对路径 - 独立运行模式，不依赖业务项目
SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR_REL="$(dirname "$SCRIPT_PATH")"
if [ -z "$SCRIPT_DIR_REL" ]; then
    SCRIPT_DIR_REL="."
fi
cd "$SCRIPT_DIR_REL"
TEAM_QUALITY_DIR="."

# 团队工具配置 - 始终在.team-code-quality目录中
TEAM_VENV="$TEAM_QUALITY_DIR/.venv"
TEAM_PYTHON="$TEAM_VENV/bin/python"
TEAM_VENV_ACTIVATE="$TEAM_VENV/bin/activate"

# 前端和后端源码路径配置环境变量
# 可通过环境变量自定义源码路径，默认为标准结构
export BACKEND_SRC_PATH="${BACKEND_SRC_PATH:-backend/src}"
export FRONTEND_SRC_PATH="${FRONTEND_SRC_PATH:-frontend/src}"
PROJECT_ROOT_REL=".."
BACKEND_BASE_DIR="$(dirname "$BACKEND_SRC_PATH")"
FRONTEND_BASE_DIR="$(dirname "$FRONTEND_SRC_PATH")"
if [ "$BACKEND_BASE_DIR" = "." ]; then
    BACKEND_BASE_DIR=""
fi
if [ "$FRONTEND_BASE_DIR" = "." ]; then
    FRONTEND_BASE_DIR=""
fi
BACKEND_BASE_PATH="$PROJECT_ROOT_REL"
FRONTEND_BASE_PATH="$PROJECT_ROOT_REL"
if [ -n "$BACKEND_BASE_DIR" ]; then
    BACKEND_BASE_PATH="$PROJECT_ROOT_REL/$BACKEND_BASE_DIR"
fi
if [ -n "$FRONTEND_BASE_DIR" ]; then
    FRONTEND_BASE_PATH="$PROJECT_ROOT_REL/$FRONTEND_BASE_DIR"
fi

log_info "源码路径配置:"
log_info "  后端路径: $BACKEND_SRC_PATH"
log_info "  前端路径: $FRONTEND_SRC_PATH"

# 检测项目类型 - 检查父目录中的项目文件
log_step "🔍 检测项目类型..."
IS_PYTHON=false
IS_JAVASCRIPT=false
IS_JAVA=false

# 使用配置的后端路径检测Python项目
if [ -f "$PROJECT_ROOT_REL/pyproject.toml" ] || [ -f "$PROJECT_ROOT_REL/requirements.txt" ] || [ -f "$BACKEND_BASE_PATH/pyproject.toml" ] || [ -f "$BACKEND_BASE_PATH/requirements.txt" ]; then
    IS_PYTHON=true
    log_success "检测到 Python 项目"
fi

# 使用配置的前端路径检测JavaScript/TypeScript项目
if [ -f "$PROJECT_ROOT_REL/package.json" ] || [ -f "$FRONTEND_BASE_PATH/package.json" ]; then
    IS_JAVASCRIPT=true
    log_success "检测到 JavaScript/TypeScript 项目"
fi

if [ -f "$PROJECT_ROOT_REL/pom.xml" ] || [ -f "$PROJECT_ROOT_REL/build.gradle" ] || [ -f "$BACKEND_BASE_PATH/pom.xml" ] || [ -f "$BACKEND_BASE_PATH/build.gradle" ]; then
    IS_JAVA=true
    log_success "检测到 Java 项目"
fi

# 显示安装计划
echo -e "\n${BLUE}🏗️ UV全局+局部虚拟环境方案:${NC}"
echo "============================================"
echo ""
if [ "$IS_PYTHON" = true ]; then
    echo "  🐍 Python 项目 (团队虚拟环境):"
    echo "    • 工具位置: $TEAM_VENV"
    echo "    • Python 工具: Black 24.10.0, isort 5.13.2, flake8 7.1.1"
    echo "    • 质量工具: MyPy 1.13.0, bandit 1.7.10, pylint 3.3.2"
    echo "    • 测试框架: pytest 8.3.3, pytest-cov 6.0.0"
fi
if [ "$IS_JAVASCRIPT" = true ]; then
    echo "  🌟 JavaScript/TypeScript (本地 node_modules):"
    echo "    • ESLint 8.57.1、Prettier 3.6.2"
    echo "    • @typescript-eslint、eslint-plugin-vue、@vue/eslint-config-typescript"
fi
if [ "$IS_JAVA" = true ]; then
    echo "  ☕ Java 项目 (系统包管理):"
    echo "    • Checkstyle, PMD (系统包管理器)"
fi
echo ""
echo "📝 方案特点:"
echo "  • Python 工具：安装在 .team-code-quality/.venv/ (团队共享)"
echo "  • JavaScript 工具：安装在 .team-code-quality/node_modules/ (团队共享)"
echo "  • 业务项目：环境干净，只有业务依赖"
echo "  • 配置文件：集中管理，符号链接到项目根目录"
echo ""

# 确认继续 - 支持非交互式模式
if [ -n "$AUTO_INSTALL" ] && [ "$AUTO_INSTALL" = "true" ]; then
    log_info "自动安装模式，跳过确认步骤"
else
    read -p "是否继续采用UV全局+局部虚拟环境方案？(y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "安装已取消"
        exit 0
    fi
fi

# 开始安装
log_step "🚀 开始UV全局+局部虚拟环境安装..."

# 计算总步骤数（根据检测到的项目类型）
total_steps=2  # UV检查、虚拟环境
if [ "$IS_PYTHON" = true ]; then
    total_steps=$((total_steps + 1))  # Python工具安装
fi
if [ "$IS_JAVASCRIPT" = true ]; then
    total_steps=$((total_steps + 1))  # JavaScript工具安装
fi

current_step=0

# 步骤1: 检查和安装 UV
((current_step++))
show_progress $current_step $total_steps "检查UV环境"
echo
if ! command -v uv >/dev/null 2>&1; then
    log_error "UV 未安装，请先安装 UV："
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
else
    log_success "UV 已安装: $(uv --version 2>/dev/null || echo "版本检查失败")"
fi

# 步骤2: 创建或更新团队虚拟环境
((current_step++))
show_progress $current_step $total_steps "设置团队工具虚拟环境"
echo
if [ ! -d "$TEAM_VENV" ]; then
    log_info "创建团队工具虚拟环境..."
    uv venv --python 3.11 "$TEAM_VENV"
    log_success "虚拟环境创建成功: $TEAM_VENV"
else
    log_info "团队虚拟环境已存在: $TEAM_VENV"
fi

# 步骤3: 安装Python团队工具
((current_step++))
show_progress $current_step $total_steps "安装Python团队工具"
echo
if [ "$IS_PYTHON" = true ]; then
    log_info "在团队虚拟环境中安装Python工具..."

    # 安装固定版本的Python工具 - 使用UV管理
    if [ -f "$TEAM_VENV_ACTIVATE" ]; then
        source "$TEAM_VENV_ACTIVATE"

        # 使用 pip 安装到虚拟环境中（关键步骤，失败时退出）
        set -e  # 临时启用严格错误检查
        python -m pip install --upgrade pip setuptools wheel || {
            log_error "pip 升级失败"
            exit 1
        }
        python -m pip install \
            black==24.10.0 \
            isort==5.13.2 \
            flake8==7.1.1 \
            mypy==1.13.0 \
            bandit==1.7.10 \
            pylint==3.3.2 \
            pytest==8.3.3 \
            pytest-cov==6.0.0 \
            pip-audit==2.7.3 || {
            log_error "Python工具安装失败"
            exit 1
        }
        set +e  # 恢复允许部分命令失败

        log_success "Python工具安装完成"
    else
        log_error "虚拟环境不存在，请先创建虚拟环境"
        exit 1
    fi

    # 验证安装（这些命令的失败不影响整体安装，所以不触发错误）
    log_info "验证工具版本..."
    if [ -f "$TEAM_PYTHON" ]; then
        "$TEAM_PYTHON" -m black --version 2>/dev/null | head -1 || echo "Black: 检查失败" || true
        "$TEAM_PYTHON" -m isort --version 2>/dev/null | head -1 || echo "isort: 检查失败" || true
        "$TEAM_PYTHON" -m flake8 --version 2>/dev/null | head -1 || echo "flake8: 检查失败" || true
        "$TEAM_PYTHON" -m mypy --version 2>/dev/null | head -1 || echo "MyPy: 检查失败" || true
    else
        log_warning "无法找到Python解释器"
    fi
else
    log_info "跳过Python工具安装"
fi

# 步骤4: 安装JavaScript团队工具
((current_step++))
show_progress $current_step $total_steps "安装JavaScript团队工具"
echo
if [ "$IS_JAVASCRIPT" = true ]; then
    log_info "安装本地JavaScript工具..."

    if command -v npm >/dev/null 2>&1; then
        log_success "npm 已安装: $(npm --version)"

        if [ -f package.json ]; then
            npm install --no-audit --no-fund || {
                log_warning "JavaScript工具安装失败，请手动运行 npm install"
            }
            if [ -d node_modules ]; then
                log_success "本地 JavaScript 工具安装完成: node_modules/"
            else
                log_warning "未检测到 node_modules/ 目录，请检查 npm install 输出"
            fi
        else
            log_warning "未找到 package.json，跳过 JavaScript 工具安装"
        fi
    else
        log_warning "npm 未安装，请先安装 Node.js 和 npm"
        log_info "建议使用 Node.js 18+ 和 npm 最新版本"
    fi
else
    log_info "跳过JavaScript工具安装"
fi

# 创建环境变量文件供Makefile使用
log_info "配置文件保持在 .team-code-quality 目录内，不污染业务项目"
cat > .env.paths << EOF
# 源码路径配置 - 由setup.sh生成
# 可通过修改这些变量来自定义项目结构
BACKEND_SRC_PATH=$BACKEND_SRC_PATH
FRONTEND_SRC_PATH=$FRONTEND_SRC_PATH
EOF

echo ""
echo "============================================"

# 完成
echo -e "\n${GREEN}${ICON_SUCCESS} UV全局+局部虚拟环境安装完成！${NC}"
echo -e "${CYAN}${ICON_INFO} 架构特点:${NC}"
echo "  • Python 工具: 团队共享虚拟环境 $TEAM_VENV"
echo "  • JavaScript 工具: 本地 node_modules (npm install)"
echo "  • 业务项目: 环境干净，只有业务依赖"
echo "  • 配置文件: 集中管理，符号链接到根目录"
echo ""
echo -e "${CYAN}${ICON_INFO} 使用方法:${NC}"
echo "  make help     - 查看所有可用命令"
echo "  make setup    - 重新安装工具"
echo "  make check    - 运行代码质量检查"
echo "  make format   - 格式化代码"
echo "  make test     - 运行测试"
echo ""
echo -e "${CYAN}${ICON_INFO} 测试目录:${NC}"
echo "  后端测试: $(dirname "$BACKEND_SRC_PATH")/tests"
echo "  前端测试: $(dirname "$FRONTEND_SRC_PATH")/tests"
echo ""
echo -e "${CYAN}${ICON_INFO} 直接使用工具:${NC}"
echo ""
if [ "$IS_PYTHON" = true ]; then
    echo "🐍 Python 团队工具:"
    echo "  $TEAM_PYTHON -m black $BACKEND_SRC_PATH/     # 格式化Python代码"
    echo "  $TEAM_PYTHON -m flake8 $BACKEND_SRC_PATH/    # Python代码检查"
    echo "  $TEAM_PYTHON -m mypy $BACKEND_SRC_PATH/      # 类型检查"
    echo "  $TEAM_PYTHON -m pytest $(dirname "$BACKEND_SRC_PATH")/tests/   # 运行后端测试"
    echo ""
fi
if [ "$IS_JAVASCRIPT" = true ]; then
    echo "🌟 JavaScript 本地工具:"
    echo "  npm exec -- eslint $FRONTEND_SRC_PATH/ --fix              # 检查和修复"
    echo "  npm exec -- prettier --write $FRONTEND_SRC_PATH/          # 格式化代码"
    echo "  cd $(dirname "$FRONTEND_SRC_PATH") && npm test                   # 运行前端测试"
    echo "  cd $(dirname "$FRONTEND_SRC_PATH") && npm run test:unit          # 运行前端单元测试"
    echo ""
fi

echo -e "${PURPLE}${ICON_GEAR} 团队工具位置:${NC}"
echo "  虚拟环境: $TEAM_VENV"
echo "  配置文件: $TEAM_QUALITY_DIR/configs/"
echo "  链接文件: 项目根目录的 .flake8, .eslintrc.json 等"
echo ""
echo -e "${CYAN}${ICON_INFO} 环境变量配置:${NC}"
echo "  当前配置已保存到: $TEAM_QUALITY_DIR/.env.paths"
echo "  自定义路径示例:"
echo "    export BACKEND_SRC_PATH=\"api/src\"      # 自定义后端源码路径"
echo "    export FRONTEND_SRC_PATH=\"web/src\"      # 自定义前端源码路径"
echo "    make setup                               # 重新安装以应用新路径"
echo ""

log_info "✅ UV全局+局部虚拟环境方案安装完成！"
log_info "✅ 现在团队拥有统一的代码质量工具环境！"
