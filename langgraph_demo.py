from typing import TypedDict
from langgraph.graph import StateGraph, END

# 1.定义State（状态）
class MyState(TypedDict):
    count: int
    message: str

# 2.定义Node(节点函数，子智能体)
def node_one(state: MyState):
    print(f"执行节点1， 当前count: {state['count']}")
    return {"count": state["count"] + 1, "message": "节点1已处理"}

def node_two(state: MyState):
    print(f"执行节点2， 当前count: {state['count']}")
    return {"count": state["count"] + 1, "message": "节点2已处理"}

# 定义路由函数
def ift2(state: MyState):
    if (state["count"] > 5):
        return "node2"
    else:
        return "node1"

# 3.构建图
workflow = StateGraph(MyState)

# 添加节点
workflow.add_node("node1", node_one)
workflow.add_node("node2", node_two)

# 添加边
workflow.set_entry_point("node1")
workflow.add_conditional_edges(
    "node1",
    ift2,
    {
        "node2": "node2",
        "node1": "node1"
    }
)
workflow.add_edge("node2", END)

# 4.编译并运行
app = workflow.compile()
result = app.invoke({"count": 0, "message": ""})
print(f"最终结果：{result}")