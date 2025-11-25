
# DeepSeek Enterprise RAG Knowledge Base

### 基于 LlamaIndex 与 Milvus 的企业级检索增强生成系统

## 1\. 系统概述 (System Overview)

本系统是一个现代化的企业级知识库问答助手。它采用 **RAG (Retrieval-Augmented Generation)** 架构，允许用户上传私有文档（PDF, DOCX, TXT），系统自动将文档向量化并存储至 **Milvus** 数据库。

当用户提问时，系统通过 **LlamaIndex** 进行语义检索，结合 **DeepSeek-V3** 大模型的推理能力，生成精准、专业的回答。前端采用 **React + Framer Motion** 构建，提供极具现代感的“毛玻璃”风格（Glassmorphism）交互体验。

### 1.1 核心特性

  * **🧠 智能 RAG 引擎**：基于 LlamaIndex v0.10+，集成 BAAI 中文 Embedding 模型，实现高精度语义检索。
  * **🌊 极速流式响应**：全链路异步架构（Async/Await），实现类似 ChatGPT 的打字机流式输出效果。
  * **🔄 数据闭环同步**：文件管理支持“硬删除”，前端删除文件的同时，自动清理 Milvus 数据库中的向量索引，杜绝幽灵数据。
  * **🎨 现代化 UI/UX**：
      * **Glassmorphism 设计**：磨砂玻璃背景、悬浮输入框。
      * **Framer Motion 动画**：平滑的侧边栏进出、消息气泡回弹、上传进度条动画。
  * **💾 混合持久化**：
      * **向量数据** -\> Milvus (Docker)
      * **会话历史** -\> SQLite (本地文件)
      * **原始文档** -\> 本地文件系统

-----

## 2\. 技术栈 (Tech Stack)

### 🖥️ 前端 (Frontend)

| 组件 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **核心框架** | React 18 | 构建用户界面的 JavaScript 库 |
| **构建工具** | Vite 5 | 极速开发服务器与打包工具 |
| **动画引擎** | **Framer Motion** | 处理复杂的进入/退出动画、布局转换 |
| **样式方案** | CSS Variables | 原生 CSS 变量管理主题色与毛玻璃特效 |
| **图标库** | Lucide React | 轻量级、风格统一的 SVG 图标 |
| **Markdown** | React-Markdown | 渲染 LLM 返回的格式化文本 |
| **网络请求** | Fetch / XHR | Fetch 用于流式对话，XHR 用于带进度的文件上传 |

### ⚙️ 后端 (Backend)

| 组件 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **Web 框架** | **FastAPI** | 高性能异步 Python Web 框架 |
| **RAG 框架** | **LlamaIndex** | (v0.10.x) 负责文档读取、切片、索引与检索 |
| **大模型** | DeepSeek-Chat | 通过 OpenAI 协议适配，提供推理能力 |
| **向量数据库** | **Milvus** | (v2.3.x) 存储高维向量数据 |
| **Embedding** | `BAAI/bge-small-zh-v1.5` | 智源中文嵌入模型，HuggingFace 下载 |
| **数据库** | SQLite3 | 轻量级存储会话（Session）与消息历史 |
| **任务队列** | BackgroundTasks | FastAPI 内置工具，用于异步处理文件向量化 |

-----

## 3\. 系统架构设计 (Architecture)

```mermaid
graph TD
    User[用户] --> Frontend[React 前端 (Vite)]
    
    subgraph Frontend_Logic
        UI[ChatArea / UploadManager]
        Stream[流式读取器]
    end
    
    Frontend -->|HTTP POST (Stream)| API[FastAPI Server]
    
    subgraph Backend_Services
        API -->|Session Management| SQLite[(SQLite DB)]
        API -->|Async Task| VectorService[Vector Store Service]
        API -->|Query| RAGService[RAG Service]
        
        VectorService -->|Load & Embed| LlamaIndex
        RAGService -->|Retrieve| LlamaIndex
        
        LlamaIndex -->|Store/Search Vectors| Milvus[(Milvus Vector DB)]
        LlamaIndex -->|Generate Answer| DeepSeek[DeepSeek LLM API]
    end
```

-----

## 4\. 核心代码模块详解

### 4.1 后端模块 (`backend/`)

#### `server.py` (服务入口)

  * **职责**：路由分发、跨域配置、后台任务调度。
  * **关键方法**：
      * `chat_endpoint`: 处理对话请求，调用 `rag.chat_stream` 并通过 `StreamingResponse` 返回生成器。
      * `upload_file`: 接收文件 -\> 保存硬盘 -\> 触发 `BackgroundTasks` (异步调用 `vector_service.process_file`)。
      * `delete_file`: 调用 `vector_service.delete_file_index` 实现数据库同步删除。

#### `vector_store.py` (数据核心)

  * **职责**：初始化 LlamaIndex、连接 Milvus、模型配置、索引管理。
  * **关键逻辑**：
      * **环境修复**：强制设置 `HF_ENDPOINT` 为国内镜像，防止模型下载卡死。
      * **模型注册**：通过 `openai_utils` 强制注册 `deepseek-chat` 到 LlamaIndex 白名单。
      * **`process_file(filepath)`**：
        1.  使用 `SimpleDirectoryReader` 加载文件（支持 PDF/DOCX/TXT）。
        2.  注入 `file_name` 到元数据（Metadata）。
        3.  调用 `self.index.insert(doc)` 将文档切片并存入 Milvus。
      * **`delete_file_index(filename)`**：
        1.  使用 `MilvusClient`。
        2.  执行删除表达式：`file_name == "{filename}"`，实现精准删除。

#### `rag_service.py` (业务大脑)

  * **职责**：定义提示词（Prompt）、执行检索与生成。
  * **关键逻辑**：
      * **Prompt Engineering**：定义了 `qa_prompt_tmpl_str`，明确区分“你是谁”（AI身份）和“我是谁”（基于文档检索）。
      * **`chat_stream(question)`**：
        1.  调用 `query_engine.aquery(question)` 执行异步检索。
        2.  使用 `async for` 遍历 `async_response_gen()`，实现非阻塞流式输出。

#### `session_manager.py` (记忆中枢)

  * **职责**：基于 SQLite 管理会话列表和聊天记录。
  * **表结构**：
      * `sessions`: `id`, `title`, `updated_at`
      * `messages`: `id`, `session_id`, `role`, `content`, `timestamp`

-----

### 4.2 前端模块 (`frontend/src/`)

#### `components/ChatArea.jsx` (对话区域)

  * **核心技术**：
      * **`useLayoutEffect`**：配合 `behavior: 'auto'`，在 DOM 绘制前瞬间滚动到底部，解决切换 Tab 时的页面抖动问题。
      * **流式解析**：使用 `response.body.getReader()` 和 `TextDecoder` 逐字节读取后端返回的数据流。
      * **Framer Motion**：实现消息气泡的 `scale` 和 `opacity` 进场动画。

#### `components/Sidebar.jsx` (侧边栏)

  * **视觉设计**：使用 `backdrop-filter: blur(20px)` 实现毛玻璃效果。
  * **交互逻辑**：
      * 历史记录项支持 `stopPropagation`，防止点击删除按钮时误触进入会话。
      * 使用 `AnimatePresence` 实现列表项删除时的平滑移除动画。

#### `components/UploadManager.jsx` (上传管理)

  * **核心技术**：
      * **`XMLHttpRequest`**：替代 `fetch`，通过监听 `xhr.upload.onprogress` 事件实现真实的上传进度百分比显示。
      * **状态同步**：上传完成后自动刷新文件列表。

-----

## 5\. API 接口文档

| 方法 | 路径 | 描述 | 参数示例 |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/chat` | 发送对话消息（流式） | `{"input": "你好", "session_id": "uuid..."}` |
| **POST** | `/api/upload` | 上传文件 | `FormData: { file: binary }` |
| **GET** | `/api/files` | 获取已上传文件列表 | 无 |
| **DELETE** | `/api/files/{filename}` | 删除文件及向量索引 | URL Path 参数 |
| **GET** | `/api/sessions` | 获取会话历史列表 | 无 |
| **GET** | `/api/sessions/{id}/messages` | 获取某会话的消息详情 | URL Path 参数 |
| **DELETE** | `/api/sessions/{id}` | 删除指定会话 | URL Path 参数 |

-----

## 6\. 部署与运行指南

### 6.1 环境要求

  * **Docker**: 用于运行 Milvus 向量数据库。
  * **Python**: 3.10 或更高版本。
  * **Node.js**: 18 或更高版本。

### 6.2 启动步骤

#### 第一步：启动数据库 (Milvus)

在项目根目录或包含 `docker-compose.yml` 的目录执行：

```bash
sudo docker run -d --name milvus-standalone -p 19530:19530 -p 9091:9091 milvusdb/milvus:v2.3.7-standalone
```

#### 第二步：启动后端 (Backend)

1.  进入后端目录：`cd backend`
2.  安装依赖：`pip install -r requirements.txt`
3.  配置环境变量：确保 `.env` 文件存在且包含 `DEEPSEEK_API_KEY`。
4.  启动服务：
    ```bash
    python server.py
    ```
    *成功标志：看到 `Uvicorn running on http://0.0.0.0:8000`*

#### 第三步：启动前端 (Frontend)

1.  进入前端目录：`cd frontend`
2.  安装依赖：`npm install`
3.  启动开发服务器：
    ```bash
    npm run dev
    ```
4.  浏览器访问：`http://localhost:5173`

-----

## 7\. 常见问题排查

1.  **后端报错 `Unknown model 'deepseek-chat'`**

      * *原因*：LlamaIndex 校验 OpenAI 模型白名单。
      * *解决*：确保 `vector_store.py` 中包含 `openai_utils.ALL_AVAILABLE_MODELS["deepseek-chat"] = 64000` 的注册代码。

2.  **前端文件上传成功，但问答找不到内容**

      * *原因*：后台向量化任务失败，通常是缺少读取器插件。
      * *解决*：在 `vector_store.py` 中显式导入 `from llama_index.readers.file import ...` 并在 `SimpleDirectoryReader` 中指定 `file_extractor`。

3.  **切换 Tab 时页面上下跳动**

      * *原因*：`useEffect` 异步滚动导致的视觉差。
      * *解决*：在 `ChatArea.jsx` 中使用 `useLayoutEffect` 配合 `behavior: 'auto'`。