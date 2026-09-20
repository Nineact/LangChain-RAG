from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from openai.types import vector_store

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, EMBEDDING_MODEL_PATH

def load_embeddings():  # load local model
    return HuggingFaceEmbeddings(model_name = EMBEDDING_MODEL_PATH)

def load_llm(): # load deepseek llm
    return ChatOpenAI(
        model = DEEPSEEK_MODEL,
        api_key = DEEPSEEK_API_KEY,
        base_url = DEEPSEEK_BASE_URL,
    )

def get_prompt():
    return ChatPromptTemplate.from_messages([
        ("system",
         "你是一个专业的认知健康助手。请严格根据以下资料回答问题，如果资料中没有相关信息，请直接说“根据现有资料无法回答”。\n\n以下是之前的对话历史：\n{history}\n\n资料：\n{context}"),
        ("user", "{question}")
    ])

def process_pdf(pdf_path, embeddings):  # load pdf, split, chroma, retriever
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = text_splitter.split_documents(docs)

    vector_store = Chroma.from_documents(documents=splits, embedding=embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    return retriever, len(splits)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)