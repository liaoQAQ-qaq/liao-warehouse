# 代码质量工具配置文件参考文档

本文档详细列出了 `.team-code-quality/configs` 目录下所有代码质量工具的配置文件及其详细配置内容。

## 📁 目录结构

```
.team-code-quality/configs/
├── .pre-commit-config.yaml          # Pre-commit Git hooks 主配置
└── lang/                             # 按语言分类的配置文件
    ├── python/                       # Python 工具配置
    │   ├── .flake8                   # Flake8 代码检查规则
    │   ├── .isort.cfg                # isort 导入排序配置
    │   ├── .pylintrc                 # Pylint 高级检查规则
    │   ├── .bandit                   # Bandit 安全检查规则
    │   ├── mypy.ini                  # MyPy 类型检查规则
    │   ├── pytest.ini                # Pytest 测试配置
    │   └── pyproject.toml            # Black 格式化配置
    ├── javascript/                   # JavaScript/TypeScript 工具配置
    │   ├── .eslintrc.json           # ESLint 代码检查规则
    │   ├── .prettierrc              # Prettier 格式化规则
    │   ├── tsconfig.json            # TypeScript 编译配置
    │   └── vitest.config.ts         # Vitest 测试配置
    └── java/                         # Java 工具配置
        ├── checkstyle.xml           # Checkstyle 代码风格规则
        ├── pmd.xml                  # PMD 代码质量规则
        └── spotbugs-exclude.xml     # SpotBugs 排除规则
```

---

## 🔧 配置文件详情

### 1. Pre-commit 配置

**文件路径**: `configs/.pre-commit-config.yaml`

**用途**: Git pre-commit hooks 主配置文件，定义在提交代码前自动运行的检查工具

**详细配置**:

```yaml
# Multi-language Pre-commit hooks configuration
# Usage: cd .team-code-quality && make install-hooks
# Usage: cd .team-code-quality && make pre-commit

repos:
  # Pre-commit built-in hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
        description: Removes trailing whitespace
        exclude: '\.md$'
      - id: end-of-file-fixer
        description: Ensures that a file is either empty or ends with one newline
      - id: check-yaml
        description: Attempts to load all yaml files to verify syntax
      - id: check-added-large-files
        description: Prevent giant files from being committed
        args: ['--maxkb=1000']
      - id: check-json
        description: Attempts to load all json files to verify syntax
      - id: check-toml
        description: Attempts to load all toml files to verify syntax
      - id: check-xml
        description: Attempts to load all xml files to verify syntax
      - id: debug-statements
        description: Check for debugger imports and py37+ `breakpoint()` calls in python source
      - id: check-merge-conflict
        description: Check for files that contain merge conflict strings
      - id: check-case-conflict
        description: Check for files that would conflict in case-insensitive filesystems
      - id: mixed-line-ending
        description: Ensures that a file doesn't have mixed line endings
      - id: requirements-txt-fixer
        description: Sorts entries in requirements.txt

  # === PYTHON HOOKS (使用UV管理的本地版本) ===

  # Python code formatting with Black (使用本地版本)
  - repo: local
    hooks:
      - id: black-local
        name: black
        entry: uv run black
        language: system
        files: ^backend/.*\.py$
        args: [--config=.team-code-quality/configs/lang/python/.flake8]
        description: The uncompromising Python code formatter (UV managed)

  # Import sorting with isort (使用本地版本)
  - repo: local
    hooks:
      - id: isort-local
        name: isort
        entry: uv run isort
        language: system
        files: ^backend/.*\.py$
        args: ["--settings-file", ".team-code-quality/configs/lang/python/.isort.cfg"]
        description: Sorts imports according to Black profile (UV managed)

  # Linting with flake8 (使用本地版本)
  - repo: local
    hooks:
      - id: flake8-local
        name: flake8
        entry: uv run flake8
        language: system
        files: ^backend/.*\.py$
        args: [--config=.team-code-quality/configs/lang/python/.flake8]
        description: Linting for Python code (UV managed)

  # Type checking with MyPy (使用本地版本)
  - repo: local
    hooks:
      - id: mypy-local
        name: mypy
        entry: uv run mypy
        language: system
        files: ^backend/src/.*\.py$
        args: [--config-file=.team-code-quality/configs/lang/python/mypy.ini]
        description: Static type checking for Python (UV managed)

  # Security scanning with Bandit (使用本地版本)
  - repo: local
    hooks:
      - id: bandit-local
        name: bandit
        entry: uv run bandit
        language: system
        files: ^backend/src/.*\.py$
        args: [-c, .team-code-quality/configs/lang/python/.bandit, -q]
        exclude: ^tests/
        description: Security oriented static analyzer (UV managed)

  # Advanced linting with Pylint (使用本地版本)
  - repo: local
    hooks:
      - id: pylint-local
        name: pylint
        entry: uv run pylint
        language: system
        files: ^backend/src/.*\.py$
        args: [--rcfile=.team-code-quality/configs/lang/python/.pylintrc]
        description: Python code analysis tool (UV managed)

  # Security scanning with pip-audit (使用本地版本)
  - repo: local
    hooks:
      - id: pip-audit-local
        name: pip-audit
        entry: uv run pip-audit --requirement=backend/requirements.txt
        language: system
        files: ^(backend/requirements\.txt|backend/pyproject\.toml)$
        description: Audit Python dependencies for known vulnerabilities (UV managed)

  # === JAVASCRIPT/TYPESCRIPT HOOKS (使用项目本地版本) ===

  # ESLint for JavaScript/TypeScript (使用项目本地版本)
  - repo: local
    hooks:
      - id: eslint-local
        name: eslint
        entry: cd frontend && npm run lint
        language: system
        files: ^frontend/.*\.(js|jsx|ts|tsx|vue)$
        pass_filenames: false
        description: Linting for JavaScript/TypeScript/Vue files (project managed)

  # Prettier for code formatting (使用项目本地版本)
  - repo: local
    hooks:
      - id: prettier-local
        name: prettier
        entry: cd frontend && npm run format
        language: system
        files: ^frontend/.*\.(js|jsx|ts|tsx|vue|json|css|scss|md)$
        pass_filenames: false
        description: Code formatting for JavaScript/TypeScript/Vue (project managed)

  # === JAVA HOOKS ===

  # Checkstyle for Java
  - repo: local
    hooks:
      - id: checkstyle
        name: Checkstyle
        entry: checkstyle
        language: system
        files: \.java$
        args: [-c, .team-code-quality/configs/lang/java/checkstyle.xml]
        description: Check Java code style

  # PMD for Java code analysis
  - repo: local
    hooks:
      - id: pmd
        name: PMD
        entry: pmd
        language: system
        files: \.java$
        args: [-R, .team-code-quality/configs/lang/java/pmd.xml, -d, .]
        description: PMD Java code analysis

  # SpotBugs for bug detection
  - repo: local
    hooks:
      - id: spotbugs
        name: SpotBugs
        entry: spotbugs
        language: system
        files: \.class$
        pass_filenames: false
        args: [-textui, -exclude, .team-code-quality/configs/lang/java/spotbugs-exclude.xml, -auxclasspath, .]
        description: SpotBugs static analysis for Java

# Global configuration
default_language_version:
  python: python3.11
  node: "18"

# Don't automatically fix files
default_stages: [pre-commit]
fail_fast: false

# Files to exclude from all hooks
exclude: |
  (?x)^(
    \.git/.*|
    \.venv/.*|
    venv/.*|
    node_modules/.*|
    target/.*|
    build/.*|
    dist/.*|
    \*.class|
    \*.jar|
    \*.war|
    \*.ear|
    \.idea/.*|
    \.vscode/.*|
    \.DS_Store
  )$
```

---

## 🐍 Python 工具配置

### 2.1 Flake8 配置

**文件路径**: `configs/lang/python/.flake8`

**工具**: Flake8 - Python 代码风格检查工具

**详细配置**:

```ini
[flake8]
max-line-length = 88
# 忽略的规则说明：
# E203: whitespace before ':' (与 black 冲突)
# W503: line break before binary operator (与 black 冲突)
# E501: line too long (允许，black 会自动处理)
# F401: imported but unused (警告级别，不阻塞)
# F841: local variable assigned but never used (警告级别)
extend-ignore = E203,W503,E501
exclude =
    __pycache__,
    .git,
    .venv,
    venv,
    migrations,
    alembic
# 允许某些常见的非关键错误
per-file-ignores =
    __init__.py:F401,F403
    tests/*:E501,F401,F811
```

**配置说明**:
- **max-line-length**: 最大行长度为 88 字符（与 Black 保持一致）
- **extend-ignore**: 忽略与 Black 冲突的规则和行长度检查
- **exclude**: 排除的目录
- **per-file-ignores**: 针对特定文件的忽略规则

---

### 2.2 isort 配置

**文件路径**: `configs/lang/python/.isort.cfg`

**工具**: isort - Python 导入排序工具

**详细配置**:

```ini
[settings]
profile = black
line_length = 88
multi_line_output = 3
include_trailing_comma = true
known_first_party = src
```

**配置说明**:
- **profile**: 使用 Black 兼容的配置
- **line_length**: 行长度 88（与 Black 一致）
- **multi_line_output**: 多行导入格式
- **include_trailing_comma**: 包含尾随逗号
- **known_first_party**: 识别 `src` 为第一方包

---

### 2.3 Pylint 配置

**文件路径**: `configs/lang/python/.pylintrc`

**工具**: Pylint - Python 代码质量分析工具

**详细配置**:

```ini
[MASTER]
# 禁用过于严格的检查
# C0114: missing-module-docstring (模块文档字符串)
# C0115: missing-class-docstring (类文档字符串)
# C0116: missing-function-docstring (函数文档字符串)
# R0903: too-few-public-methods (公共方法太少)
# E1101: no-member (成员不存在，经常误报)
# E0401: import-error (导入错误，检查时可能没有安装依赖)
# R0801: duplicate-code (代码重复，允许一定程度的重复)
# W1203: logging-fstring-interpolation (f-string 日志，现代 Python 可以接受)
# W0611: unused-import (未使用的导入，由 flake8 检查)
# W0612: unused-variable (未使用的变量，警告级别)
# W0613: unused-argument (未使用的参数，某些情况下是必需的)
# W0718: broad-exception-caught (捕获通用异常，某些情况下需要)
# C0121: singleton-comparison (单例比较，== True 在某些情况下可接受)
disable = C0114,C0115,C0116,R0903,E1101,E0401,R0801,W1203,W0611,W0612,W0613,W0718,C0121

[FORMAT]
max-line-length = 88

[DESIGN]
max-args = 10
max-attributes = 15
max-locals = 20
max-branches = 20
max-statements = 60

[TYPECHECK]
generated-members = objects,DoesNotExist,MultipleObjectsReturned
# 忽略导入错误（检查时可能没有安装依赖）
ignored-modules = sqlalchemy,fastapi,pydantic,starlette,alembic,asyncpg,psycopg2,passlib,bcrypt,jwt,email_validator,bleach
```

**配置说明**:
- **disable**: 禁用的检查规则列表（放宽检查标准）
- **max-line-length**: 最大行长度 88
- **DESIGN**: 放宽设计限制（参数、属性、局部变量等）
- **ignored-modules**: 忽略第三方库的导入错误

---

### 2.4 Bandit 配置

**文件路径**: `configs/lang/python/.bandit`

**工具**: Bandit - Python 安全漏洞扫描工具

**详细配置**:

```yaml
exclude_dirs:
  - tests
  - venv
  - .venv
  - __pycache__
skips:
  - B101
  - B601
```

**配置说明**:
- **exclude_dirs**: 排除的目录（测试、虚拟环境等）
- **skips**: 跳过的检查规则
  - **B101**: assert_used（测试中允许使用 assert）
  - **B601**: shell_injection_subprocess（某些情况下需要）

---

### 2.5 MyPy 配置

**文件路径**: `configs/lang/python/mypy.ini`

**工具**: MyPy - Python 静态类型检查工具

**详细配置**:

```ini
[mypy]
# Python version
python_version = 3.11

# 放宽检查规则 - 允许渐进式类型检查
# Warn about various issues (改为警告而非错误)
warn_return_any = false
warn_unused_configs = true
warn_no_return = false
warn_redundant_casts = false
warn_unused_ignores = true
warn_unreachable = true
strict_equality = false

# 允许未类型化的定义（渐进式类型检查）
disallow_untyped_defs = false
disallow_incomplete_defs = false
disallow_untyped_decorators = false
check_untyped_defs = false

# Optional typing (允许隐式 Optional)
no_implicit_optional = false

# 允许未解析的导入（本地模块）
ignore_missing_imports = true

# Miscellaneous
show_error_codes = true
show_error_context = true
pretty = true
color_output = true
error_summary = true
incremental = true
follow_imports = normal

# 配置模块搜索路径
mypy_path = backend/src

# Files to check
files = backend/src,backend/tests

# 排除重复的模块和配置文件
exclude = backend/src/config/database.py

# 本地模块配置 - 允许未解析的导入
[mypy-src.*]
ignore_missing_imports = true
follow_imports = skip

# Ignore missing imports for third-party libraries
[mypy-alembic.*]
ignore_missing_imports = true

[mypy-sqlalchemy.*]
ignore_missing_imports = true

[mypy-psycopg2.*]
ignore_missing_imports = true

[mypy-asyncpg.*]
ignore_missing_imports = true

[mypy-passlib.*]
ignore_missing_imports = true

[mypy-bcrypt.*]
ignore_missing_imports = true

[mypy-jwt.*]
ignore_missing_imports = true

[mypy-fastapi.*]
ignore_missing_imports = true

[mypy-pydantic.*]
ignore_missing_imports = true

[mypy-pytest.*]
ignore_missing_imports = true

[mypy-httpx.*]
ignore_missing_imports = true

[mypy-starlette.*]
ignore_missing_imports = true

[mypy-email_validator.*]
ignore_missing_imports = true

[mypy-bleach.*]
ignore_missing_imports = true
```

**配置说明**:
- **python_version**: Python 版本 3.11
- **放宽检查**: 允许渐进式类型检查，不强制所有代码都有类型注解
- **ignore_missing_imports**: 忽略缺失的导入（本地模块和第三方库）
- **mypy_path**: 模块搜索路径
- **exclude**: 排除重复的模块文件

---

### 2.6 Pytest 配置

**文件路径**: `configs/lang/python/pytest.ini`

**工具**: Pytest - Python 测试框架

**详细配置**:

```ini
[tool:pytest]
# Test discovery
testpaths = ../tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Output and reporting
addopts =
    --strict-markers
    --strict-config
    --verbose
    --cov=../src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml:coverage.xml
    --cov-fail-under=80
    --tb=short

# Test markers
markers =
    unit: Unit tests for individual functions and classes
    integration: Integration tests for API endpoints and workflows
    security: Security tests for authentication and authorization
    slow: Tests that take longer to run (> 10 seconds)
    auth: Authentication related tests
    api: API endpoint tests
    database: Database operation tests

# Minimum version required
minversion = 6.0

# Async testing
asyncio_mode = auto

# Test execution timeout
timeout = 300

# Warnings
filterwarnings =
    error
    ignore::UserWarning
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

**配置说明**:
- **testpaths**: 测试文件路径
- **addopts**: 默认选项（覆盖率、报告格式等）
- **--cov-fail-under=80**: 覆盖率要求 80%
- **markers**: 测试标记定义
- **asyncio_mode**: 异步测试模式
- **timeout**: 测试超时时间 300 秒

---

### 2.7 Black 配置（pyproject.toml）

**文件路径**: `configs/lang/python/pyproject.toml`

**工具**: Black - Python 代码格式化工具

**详细配置**:

```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | venv
  | _build
  | buck-out
  | build
  | dist
  | __pycache__
)/
'''
```

**配置说明**:
- **line-length**: 行长度 88 字符
- **target-version**: 目标 Python 版本 3.11
- **include**: 包含的文件模式（.py 和 .pyi）
- **extend-exclude**: 排除的目录（缓存、构建目录等）

---

## 🌟 JavaScript/TypeScript 工具配置

### 3.1 ESLint 配置

**文件路径**: `configs/lang/javascript/.eslintrc.json`

**工具**: ESLint - JavaScript/TypeScript 代码检查工具

**详细配置**:

```json
{
  "extends": [
    "@typescript-eslint/recommended",
    "@vue/eslint-config-typescript"
  ],
  "parser": "vue-eslint-parser",
  "parserOptions": {
    "ecmaVersion": 2022,
    "sourceType": "module",
    "parser": "@typescript-eslint/parser"
  },
  "plugins": ["@typescript-eslint", "vue"],
  "env": {
    "browser": true,
    "node": true,
    "es2022": true
  },
  "rules": {
    "indent": ["error", 2],
    "quotes": ["error", "single"],
    "semi": ["error", "never"],
    "no-console": "warn",
    "no-unused-vars": "off",
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/explicit-function-return-type": "warn",
    "@typescript-eslint/no-explicit-any": "warn",
    "vue/multi-word-component-names": "off"
  },
  "ignorePatterns": ["dist/", "node_modules/", "*.d.ts"]
}
```

**配置说明**:
- **extends**: 继承的规则集（TypeScript 和 Vue）
- **parser**: Vue 文件解析器
- **parserOptions**: ECMAScript 2022，模块模式
- **rules**: 自定义规则
  - 缩进：2 空格
  - 引号：单引号
  - 分号：不使用分号
  - 未使用变量：TypeScript 规则检查
- **ignorePatterns**: 忽略的文件模式

---

### 3.2 Prettier 配置

**文件路径**: `configs/lang/javascript/.prettierrc`

**工具**: Prettier - JavaScript/TypeScript 代码格式化工具

**详细配置**:

```json
{
  "semi": false,
  "trailingComma": "none",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "arrowParens": "avoid",
  "endOfLine": "lf",
  "quoteProps": "as-needed",
  "jsxSingleQuote": true,
  "vueIndentScriptAndStyle": true
}
```

**配置说明**:
- **semi**: 不使用分号
- **singleQuote**: 使用单引号
- **printWidth**: 行宽度 100 字符
- **tabWidth**: 缩进 2 空格
- **arrowParens**: 箭头函数参数避免括号
- **endOfLine**: 行尾 LF
- **vueIndentScriptAndStyle**: Vue 文件中的 script 和 style 标签缩进

---

### 3.3 TypeScript 配置

**文件路径**: `configs/lang/javascript/tsconfig.json`

**工具**: TypeScript 编译器配置

**详细配置**:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "declaration": true,
    "declarationMap": true,
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "moduleResolution": "node",
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "baseUrl": "./",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": [
    "src/**/*",
    "types/**/*"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "**/*.test.ts",
    "**/*.spec.ts"
  ]
}
```

**配置说明**:
- **target**: 编译目标 ES2022
- **strict**: 启用严格模式
- **paths**: 路径别名 `@/*` 映射到 `src/*`
- **exclude**: 排除测试文件和构建产物

---

### 3.4 Vitest 配置

**文件路径**: `configs/lang/javascript/vitest.config.ts`

**工具**: Vitest - JavaScript/TypeScript 测试框架

**详细配置**:

```typescript
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        'dist/'
      ],
      threshold: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  }
})
```

**配置说明**:
- **environment**: jsdom（浏览器环境模拟）
- **coverage**: 覆盖率配置
  - **threshold**: 覆盖率阈值 80%
  - **reporter**: 报告格式（文本、JSON、HTML）
- **alias**: 路径别名配置

---

## ☕ Java 工具配置

### 4.1 Checkstyle 配置

**文件路径**: `configs/lang/java/checkstyle.xml`

**工具**: Checkstyle - Java 代码风格检查工具

**详细配置**:

```xml
<?xml version="1.0"?>
<!DOCTYPE module PUBLIC
    "-//Checkstyle//DTD Checkstyle Configuration 1.3//EN"
    "https://checkstyle.org/dtds/configuration_1_3.dtd">

<module name="Checker">
    <property name="charset" value="UTF-8"/>
    <property name="severity" value="warning"/>
    <property name="fileExtensions" value="java, properties, xml"/>

    <module name="TreeWalker">
        <!-- 命名规范 -->
        <module name="ConstantName"/>
        <module name="LocalVariableName"/>
        <module name="MemberName"/>
        <module name="MethodName"/>
        <module name="PackageName"/>
        <module name="ParameterName"/>
        <module name="StaticVariableName"/>
        <module name="TypeName"/>

        <!-- 代码风格 -->
        <module name="AvoidStarImport"/>
        <module name="OneTopLevelClass"/>
        <module name="NoLineWrap"/>
        <module name="EmptyBlock"/>
        <module name="NeedBraces"/>
        <module name="LeftCurly"/>
        <module name="RightCurly"/>

        <!-- 空白符 -->
        <module name="WhitespaceAfter"/>
        <module name="WhitespaceAround"/>
        <module name="NoWhitespaceBefore"/>

        <!-- 代码复杂度 -->
        <module name="CyclomaticComplexity">
            <property name="max" value="10"/>
        </module>
        <module name="JavaNCSS"/>
        <module name="NPathComplexity"/>

        <!-- 最佳实践 -->
        <module name="ArrayTrailingComma"/>
        <module name="CovariantEquals"/>
        <module name="EmptyStatement"/>
        <module name="EqualsHashCode"/>
        <module name="FinalLocalVariable"/>
        <module name="HiddenField"/>
        <module name="IllegalInstantiation"/>
        <module name="InnerAssignment"/>
        <module name="MagicNumber"/>
        <module name="MissingSwitchDefault"/>
        <module name="SimplifyBooleanExpression"/>
        <module name="SimplifyBooleanReturn"/>

        <!-- 注释 -->
        <module name="JavadocMethod"/>
        <module name="JavadocType"/>
        <module name="JavadocVariable"/>
        <module name="JavadocStyle"/>
    </module>
</module>
```

**配置说明**:
- **severity**: 严重级别为 warning
- **CyclomaticComplexity**: 圈复杂度最大值为 10
- 检查项包括：命名规范、代码风格、空白符、复杂度、最佳实践、注释

---

### 4.2 PMD 配置

**文件路径**: `configs/lang/java/pmd.xml`

**工具**: PMD - Java 代码质量分析工具

**详细配置**:

```xml
<?xml version="1.0"?>
<ruleset name="Team Rules"
    xmlns="http://pmd.sourceforge.net/ruleset/2.0.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://pmd.sourceforge.net/ruleset/2.0.0
    http://pmd.sourceforge.net/ruleset_2_0_0.xsd">

    <description>
        团队 Java 代码质量规则
    </description>

    <!-- 基础规则 -->
    <rule ref="category/java/bestpractices.xml">
        <exclude name="JUnitTestsShouldIncludeAssert"/>
        <exclude name="JUnitUseExpected"/>
    </rule>

    <!-- 代码风格 -->
    <rule ref="category/java/codestyle.xml">
        <exclude name="ShortVariable"/>
        <exclude name="LongVariable"/>
        <exclude name="OnlyOneReturn"/>
    </rule>

    <!-- 设计原则 -->
    <rule ref="category/java/design.xml">
        <exclude name="TooManyMethods"/>
        <exclude name="CyclomaticComplexity"/>
    </rule>

    <!-- 错误预防 -->
    <rule ref="category/java/errorprone.xml"/>

    <!-- 性能优化 -->
    <rule ref="category/java/performance.xml">
        <exclude name="AvoidInstantiatingObjectsInLoops"/>
    </rule>

    <!-- 多线程 -->
    <rule ref="category/java/multithreading.xml"/>

    <!-- 自定义规则配置 -->
    <rule name="MethodLength"
          language="java"
          message="Method {0} is too long. Consider refactoring."
          class="net.sourceforge.pmd.lang.rule.XPathRule">
        <description>
            Methods should not be too long. Long methods are hard to read and maintain.
        </description>
        <priority>3</priority>
        <properties>
            <property name="xpath">
                <value>
                    //MethodDeclaration[
                        @Image='private' and
                        count(Block/BlockStatement) > 20
                    ]
                </value>
            </property>
        </properties>
    </rule>

    <rule name="ClassDataAbstractionCoupling"
          language="java"
          message="High coupling in class {0}. {1} different types are imported."
          class="net.sourceforge.pmd.lang.rule.XPathRule">
        <description>
            Classes should have low coupling. Too many different imports indicate high coupling.
        </description>
        <priority>3</priority>
        <properties>
            <property name="xpath">
                <value>
                    //ClassOrInterfaceDeclaration[
                        count(ImportDeclaration) > 15
                    ]
                </value>
            </property>
        </properties>
    </rule>
</ruleset>
```

**配置说明**:
- 包含多个规则类别：最佳实践、代码风格、设计原则、错误预防、性能、多线程
- 排除了一些过于严格的规则
- 自定义规则：方法长度、类耦合度

---

### 4.3 SpotBugs 排除配置

**文件路径**: `configs/lang/java/spotbugs-exclude.xml`

**工具**: SpotBugs - Java 静态分析工具（排除规则）

**详细配置**:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<FindBugsFilter>
    <!-- 项目特定的排除规则 -->

    <!-- 排除测试类中的某些检查 -->
    <Match>
        <Class name="~.*Test.*" />
        <Bug pattern="DM_DEFAULT_ENCODING" />
    </Match>

    <!-- 排除自动生成的代码 -->
    <Match>
        <Class name="~.*Generated.*" />
    </Match>

    <!-- 排除特定的低优先级问题 -->
    <Match>
        <Bug pattern="EI_EXPOSE_REP,EI_EXPOSE_REP2" />
        <Priority value="3" />
    </Match>

    <!-- 排除序列化相关的警告 -->
    <Match>
        <Bug pattern="SE_BAD_FIELD,SE_TRANSIENT_FIELD_NOT_RESTORED" />
    </Match>
</FindBugsFilter>
```

**配置说明**:
- 排除测试类中的编码检查
- 排除自动生成的代码
- 排除低优先级的封装问题
- 排除序列化相关的警告

---

## 📊 配置文件使用说明

### 配置文件路径变量

在 Makefile 中，配置文件路径通过以下变量定义：

- `CONFIG_DIR := configs`
- `PYTHON_CONFIG_DIR := $(CONFIG_DIR)/lang/python`
- `JS_CONFIG_DIR := $(CONFIG_DIR)/lang/javascript`
- `JAVA_CONFIG_DIR := $(CONFIG_DIR)/lang/java`

### 工具版本

所有工具使用固定版本，确保团队环境一致：

**Python 工具**:
- Black: 24.10.0
- isort: 5.13.2
- flake8: 7.1.1
- MyPy: 1.13.0
- Bandit: 1.7.10
- Pylint: 3.3.2
- pytest: 8.3.3
- pytest-cov: 6.0.0

**JavaScript 工具**:
- ESLint: 8.57.1
- Prettier: 3.6.2

### 配置文件位置

所有配置文件位于 `.team-code-quality/configs/` 目录下，保持与业务项目的独立性。通过相对路径引用，不依赖绝对路径。

---

## 📝 注意事项

1. **配置文件路径**: 所有路径都是相对于 `.team-code-quality` 目录的相对路径
2. **工具版本**: 使用固定版本，确保团队环境一致
3. **检查严格度**: 配置已适当放宽，避免过于严格的检查阻塞开发
4. **渐进式类型检查**: MyPy 配置允许渐进式添加类型注解
5. **独立性**: 配置文件与业务项目完全独立，不污染业务代码库

---

**文档生成时间**: 2024年
**配置文件位置**: `.team-code-quality/configs/`
**维护说明**: 修改配置文件后，运行 `cd .team-code-quality && make setup` 重新应用配置
