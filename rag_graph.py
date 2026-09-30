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
    is_continue: bool
    pre_answer: list
    identity: str

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
    if state["identity"] == "assistant":
        return {"context": "不需要资料"}
    docs = retriever.invoke(state["question"])
    context_str = format_docs(docs)
    return {"context": context_str}

def generate_node(state: RAGState):
    history_str = "\n".join(state["pre_answer"]) if state["pre_answer"] else "无"

    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({
        "identity": "专业的认知健康助手。请严格根据以下资料回答问题，如果资料中没有相关信息，请直接说“根据现有资料无法回答”。" if state["identity"] == "professor"
                    else "专业护士，负责处理不需要医生的问题。",
        "question": state["question"],
        "context": state["context"],
        "history": history_str,
        "is_continue": "用户需要继续回答" if state["is_continue"] else "",
        "is_satisfied": "如果之前的回答不满意，请完全改变你的回答角度和表述方式，给出一个全新的、更详细的回答。" if not state["is_satisfied"] else ""
    })  # "is_satisfied"是作为prompt给llm的，而不是state类型的返回值
    return {"answer": answer}

def evaluate_node(state: RAGState):
    print(f"本次第{state['count']}次回答：\n", state["answer"])
    user_input = input("对这个回答是否满意？(满意：1， 否则：0) ")
    is_ok = (user_input == "1")

    new_pre_answer = state["pre_answer"].copy()
    if not is_ok:
        new_pre_answer.append(state["answer"])
        is_going = True
        new_question = state["question"].copy()
    else:
        user_input = input("还要继续询问吗？(是：1， 否则：0) ")
        is_going = (user_input == "1")
        if is_going:
            new_question = input("请输入你的下一个问题：")

    return {
        "is_satisfied": is_ok,
        "is_continue": is_going,
        "question": new_question,
        "pre_answer": new_pre_answer,
        "count": state["count"] + (1 - int(is_ok))
    }

def supervise_node(state: RAGState):
    question = state["question"]

    prompt = f"你是一个主管。请判断下面的问题是否需要查阅内部资料。如果需要，只输出英文单词 'retrieve'；如果只是日常打招呼或常识，只输出英文单词 'direct'。不要输出任何其他内容。\n问题：{question}"
    decision = llm.invoke(prompt).content.strip().lower()

    if "retrieve" in decision:
        return {"identity": "professor"}
    else:
        return {"identity": "assistant"}

# define route
def checker(state: RAGState):
    if not state["is_satisfied"]:
        return "retry"      # 不满意：重试
    elif state["is_continue"]:
        return "next"       # 满意且继续：开启新话题
    else:
        return "finish"     # 满意且结束：下班收工

# work graph
workflow = StateGraph(RAGState)

workflow.add_node("supervisor", supervise_node)
workflow.add_node("retriever", retrieve_node)
workflow.add_node("generator", generate_node)
workflow.add_node("evaluator", evaluate_node)

workflow.add_edge(START, "supervisor")
workflow.add_edge("supervisor", "retriever")
workflow.add_edge("retriever", "generator")
workflow.add_edge("generator", "evaluator")
workflow.add_conditional_edges(
    "evaluator",
    checker,
    {
        "finish": END,
        "retry": "generator",
        "next": "supervisor",
    }
)
# 可以修改retriever，重新选择文本进行回答

app = workflow.compile()

# run
if __name__ == "__main__":
    user_question = input("请输入你的问题：")
    result = app.invoke({
        "question": user_question,
        "pre_answer": [],
        "is_satisfied": False,
        "is_continue": True,
        "count": 1,
        "context": "不需要资料",
        "answer": ""
    })
    print(f"\n共尝试{result['count']}次。最终回答：")
    print(result["answer"])