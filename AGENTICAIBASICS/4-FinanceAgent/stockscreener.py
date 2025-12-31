# import dependencies

from typing import Annotated
from dotenv import load_dotenv
load_dotenv()

from langchain_groq import ChatGroq
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langchain.messages import SystemMessage
from langgraph.checkpoint.memory import InMemorySaver

# adding tool nodes
from fintool import simple_screener

# create llm
llm = ChatGroq(model="llama-3.1-8b-instant", max_tokens=500)

tools = [simple_screener]
toolnode = ToolNode(tools)
llm_with_tools = llm.bind_tools(tools)

# build state schema
class State(dict):
    messages: Annotated[list, add_messages]

# llm function
def llm_with_tool(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# build the state graph
graph = StateGraph(state_schema=State)
graph.add_node("llm", llm_with_tool)
graph.add_node("tools", toolnode)

graph.add_edge(START, "llm")
graph.add_conditional_edges("llm", tools_condition)
graph.add_edge("tools", "llm")

memory = InMemorySaver()
memorygraph_builder = graph.compile(checkpointer=memory)
print(memorygraph_builder)

if __name__ == "__main__":
    while True:
        prompt = input(" Enter your prompt: ")
        messages = [SystemMessage(content="You are a financial assistant. You only have access to the simple_screener tool. Do not use any other tools."), prompt]
        response = memorygraph_builder.invoke({"messages": messages}, config={"configurable": {"thread_id" : 1234}})
        print(response['messages'][-1].content)
