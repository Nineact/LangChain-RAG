# 认知健康 AI 智能体 - RAG 问答系统 Demo

## 📖 项目简介

本项目是一个基于 **LangChain + Chroma** 的本地知识库问答系统（RAG）Demo，并已用 **FastAPI** 封装成 HTTP 接口。用户可以通过 API 提问，系统会从本地知识库中检索相关信息，并调用大模型生成基于事实的回答。

## ✨ 核心功能

- 本地文档加载与智能切分
- 使用 HuggingFace 本地嵌入模型（all-MiniLM-L6-v2）进行向量化
- 基于 Chroma 的向量存储与相似度检索
- 结合 DeepSeek 大模型，实现检索增强生成（RAG）
- 提供 FastAPI 接口，支持 HTTP POST 请求调用
- 提供 Streamlit 可视化 Web 聊天界面，支持 PDF 上传和问答
- 具备对话历史记忆功能

## 🛠️ 技术栈

- Python 3.10+
- LangChain
- Chroma（向量数据库）
- HuggingFace（本地嵌入模型）
- DeepSeek API（大模型）
- FastAPI + Uvicorn（后端接口）

## 📁 项目结构

```text
LangChain+RAG/
├── .env                  # API Key（不上传）
├── .gitignore
├── README.md
├── knowledge.txt         # 本地知识库文档
├── main.py               # FastAPI 接口主程序
├── rag_demo.py           # 终端版 RAG 测试脚本
├── test_llm.py           # 大模型 API 基础调用测试
└── test_langchain.py     # LangChain 链式调用测试
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install langchain langchain-community langchain-openai langchain-chroma langchain-huggingface langchain-text-splitters fastapi uvicorn python-dotenv streamlit pypdf
```

或者

```bash
pip install -r requirements.txt
```
### 2. 配置环境变量

在项目根目录新建 `.env` 文件，填入你的 DeepSeek API Key：

```text
DEEPSEEK_API_KEY=YourAPIKey
```

### 3. 准备本地嵌入模型

本项目使用本地 `all-MiniLM-L6-v2` 模型。请提前下载到 `models/` 目录，或修改 `main.py` 中的路径为你自己的模型路径。

### 4. 运行 FastAPI 服务

```bash
uvicorn main:app --reload
```

然后在浏览器打开 `http://127.0.0.1:8000/docs`，可以在 Swagger UI 中测试 `/ask` 接口。

### 接口示例

**请求 POST /ask**

```json
{
  "question": "什么是RAG？"
}
```

**响应**

```json
{
  "answer": "RAG是一种结合检索和生成的技术……"
}
```

### 5. 运行 Streamlit Web 界面（可选）
streamlit run app.py

## 📝 备注

本项目为个人学习与课题组申请准备，后续会持续迭代（支持 PDF 上传、多轮对话、Web UI 等）。
