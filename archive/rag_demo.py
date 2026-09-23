import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# 1. 加载文档
loader = TextLoader("../knowledge.txt", encoding="utf-8")
docs = loader.load()

# 2. 切分
text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
splits = text_splitter.split_documents(docs)
print(f"文档被分成了 {len(splits)} 块")

# 3. 向量化
print("准备加载本地嵌入模型...")
embeddings = HuggingFaceEmbeddings(
    model_name="D:/Tools/CodeOnPython/models/all-MiniLM-L6-v2"
)
print("嵌入模型加载成功！")

# 4. 存入 Chroma
vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
print("向量存储创建成功！")

# 5. 检索器
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# 6. LLM
llm = ChatOpenAI(
    model="deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 7. Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的认知健康助手。请严格根据以下资料回答问题，如果资料中没有相关信息，请直接说“根据现有资料无法回答”。\n\n资料：\n{context}"),
    ("user", "{question}")
])

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 8. RAG 链
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 9. 提问测试
print("--- 开始提问 ---")
question = "什么是RAG？"
answer = rag_chain.invoke(question)
print(f"问题：{question}")
print(f"回答：{answer}")

print("\n--- 再问一个 ---")
question2 = "轻度认知障碍是什么？"
answer2 = rag_chain.invoke(question2)
print(f"问题：{question2}")
print(f"回答：{answer2}")