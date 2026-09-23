from typing import TypedDict
from langgraph.graph import StateGraph, END

class MyState(TypedDict):
    count: int
    message: str
    is_ok: bool

def worker(state: MyState):
    print(f"[Worker] 当前count: {state['count']}")
    return {
        "count": state['count'] + 1,
        "message": f"已加工到 {state['count'] + 1}",
        "is_ok": state["count"] + 1 >= 5
    }

def checker(state: MyState):
    print(f"[Checker] 检查结果：count={state['count']}, 合格={state['is_ok']}")
    return state

def route_after_checker(state: MyState):
    if state["is_ok"]:
        return "pass"
    else:
        return "fail"

workflow = StateGraph(MyState)

workflow.add_node("worker", worker)
workflow.add_node("checker", checker)

workflow.set_entry_point("worker")
workflow.add_edge("worker", "checker")
workflow.add_conditional_edges(
    "checker",
    route_after_checker,
    {
        "pass": END,
        "fail": "worker"
    }
)

"""
# 1. 直接写个字典字面量（最常用）
state0 = {"count": 0, "message": "", "is_ok": False}
result = app.invoke(state0)

# 2. 或者带上类型提示（告诉 IDE 这个字典应该符合 MyState 的格式）
state0: MyState = {"count": 0, "message": "", "is_ok": False}
result = app.invoke(state0)

# 3. 或者先声明一个空字典，再逐个塞数据
state0: MyState = {}
state0["count"] = 0
state0["message"] = ""
state0["is_ok"] = False
result = app.invoke(state0)
"""

app = workflow.compile()
result = app.invoke({"count": 0, "message": "", "is_ok": False})
print(f"最终结果：{result}")