import os
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL =os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# 优先读环境变量（Docker 里会设置成 /app/models/all-MiniLM-L6-v2）
# 如果没有，就用本地默认路径
EMBEDDING_MODEL_PATH = os.getenv(
    "EMBEDDING_MODEL_PATH",
    "D:/Tools/CodeOnPython/LangChain+RAG/models/all-MiniLM-L6-v2"
)