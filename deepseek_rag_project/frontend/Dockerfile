# --- 第一阶段：构建阶段 ---
FROM node:18-alpine as build-stage

WORKDIR /app

# 复制 package.json 并安装依赖
COPY package*.json ./
RUN npm install

# 复制源代码并进行打包 build
COPY . .
RUN npm run build

# --- 第二阶段：运行阶段 (Nginx) ---
FROM nginx:stable-alpine as production-stage

# 从第一阶段复制打包好的 dist 文件夹到 Nginx 目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 复制我们自定义的 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]