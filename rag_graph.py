# 1. 定义状态所需
from typing import TypedDict

from dotenv import load_dotenv
# 2. LangGraph 核心（构建图）
from langgraph.graph import StateGraph, START, END

# 3. 从你昨天写好的 rag_engine.py 中复用组件（强烈建议！）
from rag_engine import (
    load_embeddings, 
    load_llm, 
    get_prompt, 
    format_docs
)

# 4. LangChain 核心（用于构建提示词和解析输出）
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

load_dotenv()

class RAGState(TypedDict):
    question: str
    context: str
    answer: str
    count: int
    is_satisfied: bool
    pre_answer: list

# init
def get_retriever(embeddings):
    loader = TextLoader("knowledge.txt", encoding="utf-8")
    docs = loader.load()
    splits = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(docs)
    vector_store = Chroma.from_documents(documents=splits, embedding=embeddings)
    retriever = vector_store.as_retriever(search_kwargs = {"k": 3})
    return retriever

def load_components():
    embeddings = load_embeddings()
    llm = load_llm()
    prompt = get_prompt()
    retriever = get_retriever(embeddings)
    return embeddings, llm, prompt, retriever

embeddings, llm, prompt, retriever = load_components()

# define nodes
def retrieve_node(state: RAGState):
    docs = retriever.invoke(state["question"])
    context_str = format_docs(docs)
    return {"context": context_str}

def generate_node(state: RAGState):
    history_str = "\n".join(state["pre_answer"]) if state["pre_answer"] else "无"

    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({
        "question": state["question"],
        "context": state["context"],
        "history": history_str,
        "is_satisfied": "满意" if (state["is_satisfied"]) else "不满意"
    })
    return {"answer": answer}

def evaluate_node(state: RAGState):
    print(f"本次第{state['count']}次回答：\n", state["answer"])
    user_input = input("对这个回答是否满意？(满意：1， 否则：0) ")
    is_ok = (user_input == "1")

    new_pre_answer = state["pre_answer"].copy()
    if not is_ok:
        new_pre_answer.append(state["answer"])

    return {
        "is_satisfied": is_ok,
        "pre_answer": new_pre_answer,
        "count": state["count"] + (1 - int(is_ok))
    }

# define route
def checker(state: RAGState):
    if state["is_satisfied"]:
        return "pass"
    else:
        return "fail"

# work graph
workflow = StateGraph(RAGState)

workflow.add_node("retriever", retrieve_node)
workflow.add_node("generator", generate_node)
workflow.add_node("evaluator", evaluate_node)

workflow.add_edge(START, "retriever")
workflow.add_edge("retriever", "generator")
workflow.add_edge("generator", "evaluator")
workflow.add_conditional_edges(
    "evaluator",
    checker,
    {
        "pass": END,
        "fail": "generator"
    }
)

app = workflow.compile()

# run
if __name__ == "__main__":
    user_question = input("请输入你的问题：")
    result = app.invoke({"question": user_question, "pre_answer": [], "is_satisfied": False, "count": 1})
    print(f"\n共尝试{result['count']}次。最终回答：")
    print(result["answer"])