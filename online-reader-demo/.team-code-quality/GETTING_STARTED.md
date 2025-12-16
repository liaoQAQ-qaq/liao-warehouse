# 👋 团队代码质量工具

> **让每个人的代码都保持高质量**

## 🚀 新员工必读 - 3分钟上手

### 第1步：安装工具！
进入.team-code-quality目录
```bash
make setup
```
> 💡 这会自动安装所有需要的代码检查工具

### 第2步：检查代码
```bash
make check
```
> 💡 提交代码前必须运行这个命令

### 第3步：修复问题
```bash
make format  # 自动格式化代码
```
> 💡 大部分格式问题可以自动修复

## ⚡ 日常开发 - 你只需要记住这些命令

| 场景 | 命令 | 说明 |
|------|------|------|
| **🔍 提交前检查** | `make check` | 必须运行！检查代码质量 |
| **🎨 自动格式化** | `make format` | 自动修复格式问题 |
| **🧪 运行测试** | `make test` | 运行所有测试 |
| **🆘 遇到问题** | `make help` | 查看所有可用命令 |

## 🎯 Git 提交时会发生什么？

当你运行 `git commit` 时，会自动检查：
- ✅ **Python代码**: 格式、导入、类型、安全检查
- ✅ **JavaScript代码**: 格式、风格检查
- ✅ **通用检查**: 文件格式、大文件警告

## ❓ 常见问题

### Q: 提示 "UV 未安装"
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Q: 提示 "make: command not found"
```bash
# Ubuntu/Debian:
sudo apt install make

# macOS:
brew install make
```

### Q: 代码检查失败
```bash
# 1. 先尝试自动修复
make format

# 2. 再检查一次
make check

# 3. 如果还有问题，查看具体错误信息并手动修复
```

### Q: 前端项目需要额外步骤
```bash
cd frontend
npm install
```

## 🔧 项目结构简介

```
.team-code-quality/
├── Makefile          # 命令接口（你主要使用这个）
├── setup.sh          # 安装脚本
├── configs/          # 配置文件（无需修改）
└── docs/             # 详细文档
```

## 📚 更多信息

- **📖 详细问题排查**: [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - 遇到问题时查阅
- **⚙️ 详细配置**: 查看 `configs/` 目录
- **🤝 遇到问题**: 联系团队维护者

---

**🎉 恭喜！现在你已经可以开始使用团队的代码质量工具了！**

**记住：每次提交前运行 `make check`**
