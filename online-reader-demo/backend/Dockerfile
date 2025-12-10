# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 1. 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. 拷贝应用代码
COPY . .

# 3. 环境变量（可以按你项目实际再改）
ENV SQLALCHEMY_DATABASE_URL="mysql+pymysql://root:password@db:3306/reader_db"

# 4. 启动命令
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
