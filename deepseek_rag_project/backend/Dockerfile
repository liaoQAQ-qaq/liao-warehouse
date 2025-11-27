# 使用轻量级的 Python 3.10 镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量 (防止 Python 生成 .pyc 文件，并让日志立即输出)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# 强制使用国内镜像源 (构建时也需要)
ENV HF_ENDPOINT=https://hf-mirror.com

# 安装系统依赖 (编译某些 Python 包需要)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
# 安装 Python 依赖 (使用清华源加速)
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制后端所有代码
COPY . .
# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "server.py"]