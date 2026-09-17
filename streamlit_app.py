import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

#init
load_dotenv()
if "messages" not in st.session_state:
    st.session_state.messages = []

#title
st.set_page_config(page_title="认知健康AI助手", layout="centered")
st.title("🧠 认知健康 AI 智能体 - RAG 问答系统")
st.caption("上传 PDF 文档，基于文档内容进行问答")

#load
@st.cache_resource
def load_component():
    embeddings = HuggingFaceEmbeddings(
        model_name = "D:/Tools/CodeOnPython/models/all-MiniLM-L6-v2"
    )
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com/",
    )
    # agent1
    prompt_extractor = ChatPromptTemplate.from_messages([
        ("system",
         "你是一个信息提取专家。请根据以下资料，提取出与用户问题相关的最核心的3个事实，用简短的句子列出。\n\n资料：\n{context}"),
        ("user", "用户问题：{question}")
    ])
    # agent2
    prompt_generator = ChatPromptTemplate.from_messages([
        ("system",
         "你是一个专业的认知健康助手。请根据以下提取出的事实，以及之前的对话历史，用温和、专业的语气回答用户。如果事实中没有相关信息，请直接说“根据现有资料无法回答”。\n\n历史对话：\n{history}\n\n提取的事实：\n{facts}"),
        ("user", "用户问题：{question}")
    ])
    return embeddings, llm, prompt_extractor, prompt_generator

embeddings, llm, prompt_extractor, prompt_generator = load_component()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_history(_):
    history_str = ""
    if "messages" not in st.session_state:
        return history_str
    for msg in st.session_state.messages[:-1]:   # the final one is the new question, uploaded
        role = "用户" if msg["role"] == "user" else "助手"
        history_str += f"{role}: {msg['context']}\n"
    return history_str

#upload
with st.sidebar:
    st.header("📄 上传知识库文档")
    uploaded_file = st.file_uploader("选择一个pdf文件", type=["pdf"])

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name

        with st.spinner("正在处理文档，请稍候..."):
            loader = PyPDFLoader(tmp_path)
            docs = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            splits = text_splitter.split_documents(docs)

            vector_store = Chroma.from_documents(documents=splits, embedding=embeddings)
            retriever = vector_store.as_retriever(search_kwargs = {"k": 3})

            extractor_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | prompt_extractor
                | llm
                | StrOutputParser()
            )

            st.session_state.rag_chain = (
                {"facts": extractor_chain,
                 "question": RunnablePassthrough(),
                 "history": get_history}
                | prompt_generator
                | llm
                | StrOutputParser()
            )
            st.success(f"文档处理完成！共切分为 {len(splits)} 块。")

#history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["context"])

#input
if prompt_input := st.chat_input("请输入你的问题..."):
    if "rag_chain" not in st.session_state:
        st.warning("请先在左侧上传 PDF 文档，构建知识库。")
    else:
        # user's message
        st.session_state.messages.append({"role": "user", "context": prompt_input})
        with st.chat_message("user"):
            st.markdown(prompt_input)
        # output
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                answer = st.session_state.rag_chain.invoke(prompt_input)
                st.markdown(answer)

        st.session_state.messages.append({"role": "assistant", "context": answer})