# 🔧 团队代码质量工具 - 详细参考手册

> **问题排查与命令详解 - 遇到问题时查阅此文档**

## 📑 目录

- [🚀 核心命令详解](#-核心命令详解)
- [🐍 Python 工具详解](#-python-工具详解)
- [🌟 JavaScript 工具详解](#-javascript-工具详解)
- [☕ Java 工具详解](#-java-工具详解)
- [🔧 维护与管理命令](#-维护与管理命令)
- [🎯 Git 集成详解](#-git-集成详解)
- [🚀 CI/CD 环境配置](#-cicd-环境配置)
- [🚨 完整故障排除指南](#-完整故障排除指南)
- [📊 配置文件详解](#-配置文件详解)
- [💡 开发最佳实践](#-开发最佳实践)

---

## 🚀 核心命令详解

### make setup - 一键安装
```bash
make setup
```
**功能**：安装所有代码质量工具和配置
**适合场景**：
- 新员工首次配置环境
- 重新安装工具
- 更新工具版本

**执行流程**：
1. 检测项目类型（Python/JavaScript/Java）
2. 检查UV环境
3. 安装Python工具（固定版本）
4. 检查JavaScript环境
5. 设置配置文件符号链接
6. 安装Git pre-commit hooks

### make check - 完整代码质量检查 ⭐
```bash
make check
```
**功能**：运行所有语言的代码质量检查
**适合场景**：
- 每次提交代码前（必须）
- CI/CD流水线检查
- 代码审查前

**检查内容**：
- Python: Black + isort + flake8 + MyPy + bandit + pylint
- JavaScript: ESLint + Prettier
- Java: Checkstyle + PMD + SpotBugs

### make format - 自动格式化
```bash
make format
```
**功能**：自动修复代码格式问题
**适合场景**：
- 代码检查失败后的第一步修复
- 定期代码整理

**格式化范围**：
- Python: Black + isort
- JavaScript: Prettier
- Java: 需要IDE插件或手动格式化

---

## 🐍 Python 工具详解

### Python 命令参考
```bash
# 完整检查流程
make check-python        # 运行所有Python检查
make format-python       # 格式化Python代码
make test-python         # 运行Python测试
make security-python     # Python安全检查

# 单独工具使用（通过Makefile）
cd .team-code-quality && make format-python    # Black代码格式化
cd .team-code-quality && make check-python     # Flake8代码检查
cd .team-code-quality && make type-check       # MyPy类型检查
cd .team-code-quality && make test-python      # Pytest测试运行
cd .team-code-quality && make security-python  # Bandit安全扫描
cd .team-code-quality && make lint-python      # Pylint高级检查
cd .team-code-quality && make audit-python     # 依赖漏洞审计
```

### Python 工具版本说明
```toml
# pyproject.toml 中的固定版本
black==24.10.0      # 代码格式化 - 遵循PEP8
isort==5.13.2       # 导入排序 - 兼容Black
flake8==7.1.1       # 代码检查 - 语法和风格
mypy==1.13.0        # 类型检查 - 静态类型分析
pytest==8.3.3       # 测试框架 - 单元测试和集成测试
bandit==1.7.10      # 安全检查 - 常见安全问题扫描
pip-audit==2.7.3    # 依赖审计 - 已知漏洞检查
pylint==3.3.2       # 高级检查 - 代码质量分析
```

### Python 常见错误及解决方案

#### Black 格式化错误
```bash
# 错误：cannot format
# 解决：检查语法错误
cd ../backend && uv run python -m py_compile your_file.py

# 强制格式化（不推荐）
cd .team-code-quality && make format-python --force
```

#### MyPy 类型检查失败
```bash
# 查看详细错误信息
cd .team-code-quality && make type-check --verbose

# 忽略特定错误（临时方案）
cd .team-code-quality && make type-check --ignore-missing-imports

# 生成类型存根
cd .team-code-quality && make type-check --install-types
```

#### Pytest 测试失败
```bash
# 运行特定测试
cd .team-code-quality && make test-python tests/test_specific.py

# 详细输出
cd .team-code-quality && make test-python --verbose

# 运行失败的测试
cd .team-code-quality && make test-python --last-failed

# 覆盖率报告
cd .team-code-quality && make coverage
```

---

## 🌟 JavaScript 工具详解

### JavaScript 命令参考
```bash
# 完整检查流程
make check-js           # 运行JavaScript检查
make format-js          # 格式化JavaScript代码
make test-js            # 运行JavaScript测试

# 在frontend目录下直接使用
cd frontend
npm run lint            # ESLint检查和修复
npm run format          # Prettier格式化
npm test                # Vitest测试
npm run test:coverage   # 测试覆盖率
npm run test:ui         # 测试UI界面
```

### JavaScript 配置文件
```json
// package.json 中的脚本
{
  "scripts": {
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix",
    "format": "prettier --write src/",
    "test": "vitest",
    "test:coverage": "vitest --coverage",
    "test:ui": "vitest --ui"
  }
}
```

### JavaScript 常见错误及解决方案

#### ESLint 规则冲突
```bash
# 查看具体规则错误
npm run lint -- --no-fix

# 查看规则说明
npm run lint -- --ext .vue src/ --max-warnings 0

# 临时禁用特定规则（不推荐）
/* eslint-disable no-console */
console.log('debug');
/* eslint-enable no-console */
```

#### Prettier 格式化冲突
```bash
# 检查配置文件位置
ls .team-code-quality/configs/lang/javascript/.prettierrc

# 验证格式但不修改
npx prettier --check .

# 强制格式化特定文件
npx prettier --write src/components/*.vue
```

#### Vue3 特定问题
```bash
# 检查Vue组件
npm run lint -- src/App.vue

# 格式化Vue单文件组件
npx prettier --write src/**/*.vue

# TypeScript 类型检查
npx vue-tsc --noEmit
```

---

## ☕ Java 工具详解

### Java 命令参考
```bash
# 完整检查流程
make check-java         # 运行Java代码检查
make test-java          # 运行Java测试

# 直接使用构建工具
mvn test                # Maven测试
./gradlew test          # Gradle测试

# 代码质量工具
checkstyle -c .team-code-quality/configs/lang/java/checkstyle.xml src/
pmd -R .team-code-quality/configs/lang/java/pmd.xml -d src/
spotbugs -textui -exclude .team-code-quality/configs/lang/java/spotbugs-exclude.xml target/classes/
```

### Java 系统依赖安装
```bash
# Ubuntu/Debian
sudo apt install checkstyle pmd spotbugs

# 验证安装
checkstyle -version
pmd --version
```

### Java 常见错误及解决方案

#### Checkstyle 配置问题
```bash
# 检查配置文件语法
checkstyle -c .team-code-quality/configs/lang/java/checkstyle.xml src/MyClass.java

# 自定义配置
checkstyle -c custom-checkstyle.xml src/

# 生成报告
checkstyle -c checkstyle.xml -f xml src/ > checkstyle-report.xml
```

#### PMD 规则集问题
```bash
# 使用内置规则集
pmd -R java-quickstart -d src/

# 自定义规则
pmd -R custom-rules.xml -d src/

# 排除测试文件
pmd -R pmd.xml -d src/ --exclude-dirs test/
```

---

## 🔧 维护与管理命令

### 环境状态检查
```bash
make status             # 检查所有工具状态
make validate           # 验证配置文件正确性
make clean              # 清理临时文件和缓存
```

### 工具更新与管理
```bash
make update-quality     # 更新质量工具配置
make install-tools      # 仅安装工具（不配置）
make uninstall          # 卸载所有工具
```

### 报告生成
```bash
make report             # 生成完整质量报告
make coverage           # 生成测试覆盖率报告
```

---

## 🎯 Git 集成详解

### Pre-commit Hooks 管理
```bash
# 安装hooks（首次使用）
make setup              # 自动安装
# 或
cd .team-code-quality && make install-hooks

# 手动运行所有检查
cd .team-code-quality && make pre-commit

# 运行特定hook
cd .team-code-quality && make run-hook black

# 跳过hooks（不推荐）
git commit --no-verify

# 更新hooks版本
cd .team-code-quality && make update-hooks
```

### Pre-commit 配置详解
```yaml
# .team-code-quality/configs/.pre-commit-config.yaml
repos:
  # Python hooks（使用本地UV版本）
  - repo: local
    hooks:
      - id: black-local
        entry: uv run black
        files: ^backend/.*\.py$

  # JavaScript hooks（使用项目npm）
  - repo: local
    hooks:
      - id: eslint-local
        entry: npm run lint
        files: ^frontend/.*\.(js|ts|vue)$
```

### Git 工作流最佳实践
```bash
# 1. 开始开发
git checkout -b feature/new-feature

# 2. 开发过程中定期检查
make format          # 定期格式化
make check          # 确保代码质量

# 3. 提交前
make test           # 运行测试
make security       # 安全检查
make check          # 最终检查
git add .
git commit -m "feat: new feature"  # 自动触发hooks

# 4. 推送前
make check          # 再次确认
git push origin feature/new-feature
```

---

## 🚀 CI/CD 环境配置

> **确保本地开发与CI/CD环境完全一致的配置方案**

### 🎯 配置读取机制

#### 当前`make format`配置读取优先级

```bash
# Python格式化配置优先级：
1. .team-code-quality/configs/lang/python/.flake8  (最高优先级)
2. .flake8  (根目录备用配置)
3. 默认配置 (最低优先级)

# JavaScript格式化配置优先级：
1. .team-code-quality/configs/lang/javascript/.prettierrc
2. .prettierrc (根目录备用配置)
3. 默认配置
```

#### CI/CD环境风险场景

| 场景 | 本地环境 | CI/CD环境 | 影响 |
|------|----------|-----------|------|
| **格式化不一致** | 使用团队配置 | 使用默认配置 | ❌ 格式差异导致检查失败 |
| **版本不匹配** | Black 24.10.0 | Black 23.0.0 | ❌ 代码风格不一致 |
| **配置缺失** | 配置文件完整 | 配置文件缺失 | ❌ 回退到默认行为 |

### 🔧 解决方案

#### 方案1：配置文件版本控制（推荐）

**步骤1：确保配置文件被Git跟踪**
```bash
# 确认配置文件在Git中
git add .team-code-quality/configs/
git commit -m "Add code quality configuration files"

# 验证文件被跟踪
git ls-files | grep -E "\.flake8|\.prettierrc|\.eslintrc"
```

**步骤2：项目根目录创建配置链接**
```bash
# 在项目根目录创建符号链接
ln -sf .team-code-quality/configs/lang/python/.flake8 .flake8
ln -sf .team-code-quality/configs/lang/python/.isort.cfg .isort.cfg
ln -sf .team-code-quality/configs/lang/javascript/.prettierrc .prettierrc
ln -sf .team-code-quality/configs/lang/javascript/.eslintrc.json .eslintrc.json

# 添加到Git
git add .flake8 .isort.cfg .prettierrc .eslintrc.json
git commit -m "Add config symlinks to project root"
```

**步骤3：验证Makefile配置支持**
```bash
# 当前Makefile已支持备用配置路径
make format
# 输出示例：
# 🐍 格式化Python代码 (UV固定版本)...
# 使用配置文件: .team-code-quality/configs/lang/python/.flake8
# 或
# 使用根目录配置: .flake8
```

#### 方案2：Docker容器化环境

**预配置的Docker镜像**
```dockerfile
# .team-code-quality/Dockerfile
FROM python:3.11-slim

# 安装UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# 安装Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
RUN apt-get install -y nodejs

# 复制项目
WORKDIR /app
COPY . .

# 安装依赖
RUN uv sync --group dev
RUN cd frontend && npm install

# 设置格式化入口点
ENTRYPOINT ["make", "format"]
```

### 📦 CI/CD配置示例

#### GitHub Actions完整配置

```yaml
# .github/workflows/code-quality.yml
name: Code Quality

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11']
        node-version: ['18']

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Set up Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}

      - name: Install UV
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          echo "$HOME/.cargo/bin" >> $GITHUB_PATH

      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: |
            ~/.cache/uv/
            frontend/node_modules
          key: ${{ runner.os }}-deps-${{ hashFiles('**/uv.lock', '**/package-lock.json') }}

      - name: Setup environment
        run: |
          echo "验证配置文件..."
          python -c "
          import os
          configs = [
              '.team-code-quality/configs/lang/python/.flake8',
              '.team-code-quality/configs/lang/python/.isort.cfg',
              '.team-code-quality/configs/lang/javascript/.prettierrc',
              '.team-code-quality/configs/lang/javascript/.eslintrc.json'
          ]
          for config in configs:
              if os.path.exists(config):
                  print(f'✅ {config}')
              else:
                  print(f'❌ {config} 不存在')
                  exit(1)
          "

      - name: Create config symlinks (fallback)
        run: |
          if [ ! -f .flake8 ] && [ -f .team-code-quality/configs/lang/python/.flake8 ]; then
            ln -sf .team-code-quality/configs/lang/python/.flake8 .flake8
            echo "创建 .flake8 符号链接"
          fi

          if [ ! -f .prettierrc ] && [ -f .team-code-quality/configs/lang/javascript/.prettierrc ]; then
            ln -sf .team-code-quality/configs/lang/javascript/.prettierrc .prettierrc
            echo "创建 .prettierrc 符号链接"
          fi

      - name: Install tools
        run: |
          make setup

      - name: Validate configuration
        run: |
          echo "验证配置一致性..."
          make validate

      - name: Run formatting
        run: |
          echo "运行代码格式化..."
          make format

      - name: Check for formatting changes
        run: |
          if [[ -n $(git status --porcelain) ]]; then
            echo "❌ 代码格式不统一"
            echo "以下文件需要格式化："
            git diff --name-only
            echo ""
            echo "格式化差异："
            git diff
            echo ""
            echo "解决方案：在本地运行 'make format' 并提交更改"
            exit 1
          else
            echo "✅ 代码格式检查通过"
          fi

      - name: Run full quality check
        run: |
          make check
```

#### GitLab CI配置

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - format
  - check

variables:
  PYTHON_VERSION: "3.11"
  NODE_VERSION: "18"

cache:
  paths:
    - .cache/uv/
    - frontend/node_modules/

before_script:
  - echo "Setting up environment..."
  - apt-get update -qq
  - apt-get install -y make curl
  - curl -LsSf https://astral.sh/uv/install.sh | sh
  - export PATH="/root/.cargo/bin:$PATH"
  - curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
  - apt-get install -y nodejs

validate_config:
  stage: validate
  script:
    - echo "Validating configuration files..."
    - |
      python -c "
      import os
      required_configs = [
          '.team-code-quality/configs/lang/python/.flake8',
          '.team-code-quality/configs/lang/python/.isort.cfg',
          '.team-code-quality/configs/lang/javascript/.prettierrc',
          '.team-code-quality/configs/lang/javascript/.eslintrc.json'
      ]
      missing = [cfg for cfg in required_configs if not os.path.exists(cfg)]
      if missing:
          print(f'❌ 缺少配置文件: {missing}')
          exit(1)
      print('✅ 所有配置文件存在')
      "
  only:
    - merge_requests
    - main

format_code:
  stage: format
  script:
    - echo "Installing tools..."
    - make setup
    - echo "Running format..."
    - make format
    - |
      if [[ -n $(git status --porcelain) ]]; then
        echo "❌ 代码格式不统一"
        git diff
        echo "请在本地运行 'make format' 并提交更改"
        exit 1
      else
        echo "✅ 代码格式检查通过"
      fi
  only:
    - merge_requests
    - main
```

### 🔍 验证配置一致性

#### 本地验证脚本

```bash
#!/bin/bash
# scripts/validate-format-consistency.sh

echo "🔍 验证格式化配置一致性..."

# 1. 检查配置文件存在
echo "检查配置文件..."
configs=(
    ".team-code-quality/configs/lang/python/.flake8"
    ".team-code-quality/configs/lang/python/.isort.cfg"
    ".team-code-quality/configs/lang/javascript/.prettierrc"
    ".team-code-quality/configs/lang/javascript/.eslintrc.json"
)

for config in "${configs[@]}"; do
    if [ -f "$config" ]; then
        echo "✅ $config"
    else
        echo "❌ $config 不存在"
        exit 1
    fi
done

# 2. 检查工具版本
echo ""
echo "检查工具版本..."
cd .team-code-quality && make format-python --version
cd .team-code-quality && make check-python --version
npm list prettier eslint 2>/dev/null || echo "JavaScript工具未安装"

# 3. 测试格式化
echo ""
echo "测试格式化..."
test_file=$(mktemp --suffix=.py)
echo 'import os,sys' > "$test_file"
cd .team-code-quality && make format-python --check "$test_file" && echo "✅ Black配置正确" || echo "❌ Black配置问题"
rm "$test_file"

echo "✅ 配置验证完成"
```

#### CI/CD环境验证脚本

```bash
#!/bin/bash
# 在CI/CD中运行此脚本验证环境一致性

echo "🏥 CI/CD环境健康检查..."

# 1. 环境信息
echo "环境信息："
echo "Python: $(python --version)"
echo "UV: $(uv --version)"
echo "Node.js: $(node --version)"
echo "Make: $(make --version)"

# 2. 配置文件检查
echo ""
echo "配置文件检查："
if [ -d ".team-code-quality" ]; then
    echo "✅ .team-code-quality 目录存在"
    find .team-code-quality/configs -name "*.toml" -o -name "*.json" -o -name "*.xml" -o -name ".*cfg" -o -name ".*ini" | while read file; do
        echo "✅ $file"
    done
else
    echo "❌ .team-code-quality 目录不存在"
    exit 1
fi

echo "✅ CI/CD环境检查完成"
```

### ❓ CI/CD常见问题

#### Q1: CI/CD中配置文件路径错误

```bash
# 症状：找不到配置文件
# 解决：创建符号链接
ln -sf .team-code-quality/configs/lang/python/.flake8 .flake8
ln -sf .team-code-quality/configs/lang/javascript/.prettierrc .prettierrc
```

#### Q2: 工具版本不一致

```bash
# 症状：格式化结果不同
# 解决：固定版本号
# pyproject.toml
[dependency-groups]
dev = [
    "black==24.10.0",    # 固定版本
    "isort==5.13.2",     # 固定版本
]
```

#### Q3: 权限问题

```bash
# 症状：权限拒绝
# 解决：检查文件权限
ls -la .team-code-quality/configs/
chmod 644 .team-code-quality/configs/lang/python/.flake8
```

#### Q4: 符号链接在Windows中不工作

```bash
# Windows解决方案：复制配置文件
cp .team-code-quality/configs/lang/python/.flake8 .flake8
cp .team-code-quality/configs/lang/javascript/.prettierrc .prettierrc
```

---

## 🚨 完整故障排除指南

### 🔧 环境问题

#### UV 未安装或版本错误
```bash
# 症状：make setup 时提示 "UV 未安装"
curl -LsSf https://astral.sh/uv/install.sh | sh

# 重新加载环境
source ~/.bashrc

# 验证安装
uv --version
```

#### Make 工具未安装
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install make

# macOS
brew install make

# 验证安装
make --version
```

#### Node.js/npm 问题
```bash
# 检查版本（需要18+）
node --version
npm --version

# 安装正确版本（Ubuntu）
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# 使用nvm管理版本
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

### 🐍 Python 特定问题

#### 依赖版本冲突
```bash
# 症状：工具版本不匹配错误
# 解决：重新安装固定版本
rm uv.lock
uv sync --group dev

# 清理缓存
uv cache clean
```

#### 路径问题
```bash
# 症状：找不到配置文件
# 检查符号链接
ls -la .pre-commit-config.yaml

# 手动创建链接
ln -sf .team-code-quality/configs/.pre-commit-config.yaml .pre-commit-config.yaml
```

#### 权限问题
```bash
# 症状：权限拒绝错误
chmod +x .team-code-quality/setup.sh

# 检查文件权限
ls -la .team-code-quality/
```

### 🌟 JavaScript 特定问题

#### npm 依赖问题
```bash
# 症状：找不到ESLint或Prettier
cd frontend
rm -rf node_modules package-lock.json
npm install

# 清理npm缓存
npm cache clean --force
```

#### Node.js 版本不匹配
```bash
# 症状：依赖需要不同Node版本
nvm list
nvm use 18  # 或项目要求的版本

# 在package.json中指定引擎
# "engines": { "node": ">=18.0.0" }
```

### ☕ Java 特定问题

#### 工具路径问题
```bash
# 症状：checkstyle命令未找到
# 查找安装位置
whereis checkstyle
which checkstyle

# 添加到PATH（临时）
export PATH=$PATH:/usr/share/java/checkstyle

# 永久添加
echo 'export PATH=$PATH:/usr/share/java/checkstyle' >> ~/.bashrc
```

#### 编译问题
```bash
# 症状：SpotBugs找不到.class文件
# 确保先编译
mvn compile
# 或
./gradlew build

# 然后运行SpotBugs
spotbugs -textui target/classes/
```

### 🔍 调试技巧

#### 详细错误输出
```bash
# Python工具详细输出
cd .team-code-quality && make format-python --check --verbose
cd .team-code-quality && make check-python --verbose
cd .team-code-quality && make type-check --show-traceback

# Pre-commit详细输出
cd .team-code-quality && make pre-commit --verbose

# Make调试
make check --debug
```

#### 逐步诊断
```bash
# 1. 检查环境
make status

# 2. 验证配置
make validate

# 3. 单独测试每个工具
cd .team-code-quality && make format-python --version
cd .team-code-quality && make check-python --version
npm --version

# 4. 检查文件权限
ls -la .team-code-quality/

# 5. 测试简单文件
echo "print('test')" > test.py
cd .team-code-quality && make format-python test.py
rm test.py
```

---

## 📊 配置文件详解

### 配置文件位置与用途
```
.team-code-quality/
├── configs/
│   ├── .pre-commit-config.yaml    # Git hooks主配置
│   └── lang/
│       ├── python/
│       │   ├── .flake8           # Flake8代码检查规则
│       │   ├── .pylintrc         # Pylint高级检查规则
│       │   ├── .bandit           # Bandit安全检查规则
│       │   ├── mypy.ini          # MyPy类型检查规则
│       │   └── pytest.ini        # Pytest测试配置
│       ├── javascript/
│       │   ├── .eslintrc.json    # ESLint代码检查规则
│       │   └── .prettierrc       # Prettier格式化规则
│       └── java/
│           ├── checkstyle.xml    # Checkstyle代码风格规则
│           ├── pmd.xml           # PMD代码质量规则
│           └── spotbugs-exclude.xml  # SpotBugs排除规则
├── pyproject.toml                # Python工具依赖和版本
└── Makefile                      # 命令接口定义
```

### 修改配置文件
```bash
# 自定义Black配置
echo -e "[tool.black]\nline-length = 88" >> pyproject.toml

# 自定义ESLint规则
cp .team-code-quality/configs/lang/javascript/.eslintrc.json custom-eslint.json
vim custom-eslint.json

# 测试自定义配置
cd .team-code-quality && make format-python --config custom-black.toml src/
```

---

## 💡 开发最佳实践

### 每日开发流程
```bash
# 1. 开始工作
git pull origin main
make check              # 确保代码库状态良好

# 2. 开发新功能
# ... 编写代码 ...
make format             # 定期格式化
make check              # 定期检查

# 3. 完成功能
make test               # 运行测试
make security           # 安全检查
make check              # 最终检查

# 4. 提交代码
git add .
git commit -m "feat: implement new feature"
```

### 代码审查准备
```bash
# 1. 确保所有检查通过
make check
make test
make coverage

# 2. 生成质量报告
make report

# 3. 分支管理
git checkout -b pr/feature-name
git push origin pr/feature-name

# 4. 创建PR前最终检查
make check
```

### 性能优化建议
```bash
# 使用增量检查（大型项目）
cd .team-code-quality && make format-python src/new_module/    # 只检查修改的模块
cd .team-code-quality && make check-python src/new_module/

# 并行测试
cd .team-code-quality && make test-python --parallel           # 如果安装了pytest-xdist

# 缓存依赖
cd ../backend && uv sync --frozen                # 使用锁文件，不重新解析
```

---

## 📞 获取帮助

### 命令行帮助
```bash
make help                       # 查看所有可用命令
make docs                       # 打开文档（如果有less命令）
cd ../backend && uv run --help  # UV帮助
cd .team-code-quality && make format-python --help
```

### 常用信息查询
```bash
# 查看工具版本
make status                     # 所有工具状态

# 验证配置
make validate                   # 配置文件检查

# 查看配置文件位置
find .team-code-quality -name "*.toml" -o -name "*.json" -o -name "*.xml"
```

### 社区资源
- [Black官方文档](https://black.readthedocs.io/)
- [ESLint用户指南](https://eslint.org/docs/user-guide/)
- [Prettier文档](https://prettier.io/docs/)
- [Pre-commit官方文档](https://pre-commit.com/)
- [UV用户指南](https://docs.astral.sh/uv/)

---

**💡 提示**: 将此文档加入浏览器书签，遇到问题时可以快速找到解决方案！
