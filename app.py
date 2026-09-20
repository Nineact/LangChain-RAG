import streamlit as st
import tempfile
from dotenv import load_dotenv

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from rag_engine import load_embeddings, load_llm, get_prompt, process_pdf, format_docs

load_dotenv()

# UI
st.set_page_config(page_title="认知健康AI助手", layout="centered")
st.title("🧠 认知健康 AI 智能体 - RAG 问答系统")
st.caption("上传 PDF 文档，基于文档内容进行问答")

# init history
if "messages" not in st.session_state:
    st.session_state.messages = []

# load model
@st.cache_resource
def load_components():
    embeddings = load_embeddings()
    llm = load_llm()
    prompt = get_prompt()
    return embeddings, llm, prompt

embeddings, llm, prompt = load_components()

# get history
def get_history(_):
    history_str = ""
    if "messages" not in st.session_state:
        return history_str
    for msg in st.session_state.messages[:-1]:  # exclude new input
        role = "用户" if msg["role"] == "user" else "助手"
        history_str += f"{role}: {msg['message']}\n"
    return history_str

# sidebar
with st.sidebar:
    st.header("📄 上传知识库文档")
    uploaded_file = st.file_uploader("选择一个pdf文件", type=["pdf"])

    if uploaded_file is not None:
        if "process_file" not in st.session_state or st.session_state.process_file != uploaded_file.name:
            with st.spinner("正在处理文档，请稍候..."):
                # save temp file
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                # process pdf
                retriever, split_cnt = process_pdf(tmp_path, embeddings)

                # RAG
                st.session_state.rag_chain = (
                    {
                        "context": retriever | format_docs,
                        "question": RunnablePassthrough(),
                        "history": get_history
                    }
                    | prompt
                    | llm
                    | StrOutputParser()
                )
                st.session_state.process_file = uploaded_file.name
                st.success(f"文档处理完成！共切分为 {split_cnt} 块。")
        else:
            st.info("当前文档已处理完成，可以直接在下方提问。")

# display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["context"])

# conversation
if prompt_input := st.chat_input("请输入你的问题..."):
    if "rag_chain" not in st.session_state:
        st.warning("请先在左侧上传 PDF 文档，构建知识库。")
    else:
        # display user's question
        st.session_state.messages.append({"role": "user", "message": prompt_input})
        with st.chat_message("user"):
            st.markdown(prompt_input)

        # AI response
        with st.chat_message("assistant"):
            with st.spinner("不深度思考中..."):
                answer = st.session_state.rag_chain.invoke(prompt_input)
                st.markdown(answer)

        # save answer
        st.session_state.messages.append({"role": "assistant", "message": answer})