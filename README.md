# 🧠 认知健康 AI 智能体 - RAG 问答系统 Demo

本项目是一个面向认知健康场景的智能问答系统 Demo。采用 **LangGraph** 构建状态图工作流，结合 **RAG（检索增强生成）** 技术，实现了基于本地知识库的精准问答，并支持人工评估重试的闭环机制。项目已通过 **Docker** 完成容器化，支持一键部署。

## ✨ 核心功能

- **RAG 检索增强生成**：基于本地 PDF/TXT 知识库，使用 Chroma 向量数据库检索最相关文本，交由 DeepSeek 大模型生成有据可依的回答，有效减少幻觉。
- **LangGraph 状态图工作流**：将 RAG 从传统的单链（LCEL）重构为图结构，支持条件路由、循环重试和状态合并。
- **人工评估与重试闭环（Human-in-the-Loop）**：引入了评估节点，如果对回答不满意，图会带着历史回答回退到生成节点，重新调整回答策略，直到满意为止。
- **Streamlit 可视化界面**：提供友好的 Web 聊天界面，支持上传 PDF、多轮对话和实时问答。
- **Docker 一键部署**：包含 `Dockerfile` 和 `docker-compose.yml`，无需配置本地 Python 环境，一条命令即可在任何电脑上运行。

## 🛠️ 技术栈

- **核心框架**：Python 3.10+, LangChain, LangGraph
- **大模型**：DeepSeek API (`deepseek-chat`)
- **向量模型**：HuggingFace 本地模型 (`all-MiniLM-L6-v2`)
- **向量数据库**：Chroma
- **前端界面**：Streamlit
- **部署工具**：Docker, Docker Compose
- **其他**：python-dotenv (环境变量管理)

## 📁 项目结构

```text
LangChain-RAG/
├── .env                  # API Key 配置（不上传）
├── .gitignore            # Git 忽略规则
├── Dockerfile            # Docker 构建文件
├── docker-compose.yml    # Docker 容器编排文件
├── requirements.txt      # Python 依赖清单
├── README.md             # 项目说明文档
├── app.py                # Streamlit 主入口（界面与交互）
├── rag_engine.py         # RAG 核心逻辑（加载模型、切分文档、构建检索器）
├── rag_graph.py          # LangGraph 状态图实现（评估-重试闭环）
├── config.py             # 全局配置（路径、API Key等）
├── knowledge.txt         # 本地知识库测试文件
└── models/               # 本地 HuggingFace 模型文件（不上传）
```

## 🚀 快速开始（app.py）

### 方式一：使用 Docker 一键启动（推荐）

无需安装 Python 环境，只需确保电脑上已安装 Docker Desktop。

1. 在项目根目录下，创建 `.env` 文件，填入你的 DeepSeek API Key：
   ```text
   DEEPSEEK_API_KEY=你的APIKey
   ```
2. 运行以下命令启动容器（后台运行）：
   ```bash
   docker-compose up -d
   ```
3. 浏览器访问 `http://localhost:8501` 即可使用。
4. 如需关闭服务，运行：
   ```bash
   docker-compose down
   ```

### 方式二：本地 Python 环境运行

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 配置 `.env` 文件（同上）。
3. 启动 Streamlit 应用：
   ```bash
   streamlit run app.py
   ```

## 🧠 核心架构解析（LangGraph, rag_graph.py）

本项目采用了 LangGraph 将传统的“检索 -> 生成”单链升级为**状态图（State Graph）**。

*   **State（状态）**：全局共享的数据包，包含 `question`（问题）、`context`（检索内容）、`answer`（回答）、`pre_answer`（历史回答列表）、`count`（重试次数）等。
*   **Node（节点）**：
    *   `retrieve_node`：负责根据问题检索文档。
    *   `generate_node`：负责调用大模型生成回答。
    *   `evaluate_node`：负责接收用户满意度反馈，并更新状态。
*   **Edge（边）**：定义了图的流转路径。
    *   `START` -> `retriever` -> `generator` -> `evaluator`
    *   条件边（Conditional Edge）：`evaluator` 后根据满意度决定是结束（`END`）还是回退到 `generator` 重新生成。

这种设计实现了 **Evaluator-Optimizer（评估-优化）** 模式，为后续接入多智能体协同（Multi-Agent）和 MCP 工具调用打下了架构基础。

## 📝 未来规划

- [ ] 引入 LangGraph Checkpointer，实现跨会话的长期记忆持久化。
- [ ] 接入 MCP（模型上下文协议），支持 Tool Calling（外部工具调用）。
- [ ] 构建多智能体协同架构（如 Supervisor Agent 路由多个子 Agent）。
- [ ] 优化 RAG 检索策略（如 Parent-Child Retriever, Hybrid Search）。