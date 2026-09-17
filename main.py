import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# ========== 初始化部分 ==========
load_dotenv()

# 1. 加载文档和切分
loader = TextLoader("knowledge.txt", encoding="utf-8")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
splits = text_splitter.split_documents(docs)
print(f"文档被分成了 {len(splits)} 块")

# 2. 向量化并存储
embeddings = HuggingFaceEmbeddings(
    model_name="D:/Tools/CodeOnPython/models/all-MiniLM-L6-v2"
)
vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# 3. 大模型
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 4. Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的认知健康助手。请严格根据以下资料回答问题，如果资料中没有相关信息，请直接说“根据现有资料无法回答”。\n\n资料：\n{context}"),
    ("user", "{question}")
])

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 5. RAG 链
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

## ========== FastAPI 接口部分 ==========
app = FastAPI()

# 定义请求体的数据格式
class Question(BaseModel):
    question: str

# 定义接口：POST /ask
@app.post("/ask")
def ask(q: Question):
    answer = rag_chain.invoke(q.question)
    return {"answer": answer}