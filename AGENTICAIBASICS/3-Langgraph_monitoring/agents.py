from typing import TypedDict, Annotated
from dotenv import load_dotenv
load_dotenv()
import os
from langchain_groq import ChatGroq
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import tool
from langgraph.graph.message import AnyMessage, add_messages

os.environ["LANGSMITH_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGSMITH_TRACING"]="true"
os.environ["LANGSMITH_PROJECT"]="TestProject"

class State(TypedDict):
    messages : Annotated[list[AnyMessage], add_messages]

# initializing llm model
llm = ChatGroq(model="llama-3.1-8b-instant")

#tool 1
@tool
def customfun(a: float) -> float:
    """A custom tool that multiplies the input number by 2.523."""
    return a * 2.523

# tool 2 tavily
from langchain_tavily import TavilySearch
tavily_tool = TavilySearch()



tools = [customfun, tavily_tool]
# binding tools to llm
llm_with_tools = llm.bind_tools(tools)

def llm_func(state: State):
    return {"messages" : llm_with_tools.invoke(state["messages"])}

# builing the state graph
graph = StateGraph(state_schema=State)

graph.add_node("llm", llm_func)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "llm")
graph.add_conditional_edges(
    "llm",
    tools_condition
)
graph.add_edge("tools", "llm")
graph.add_edge("llm", END)
graph_builder = graph.compile()

response = graph_builder.invoke({"messages" : ["Latest AI news and multiple my number 987"]})
print(response["messages"][-1].content)
# from IPython.display import display, Image
# display(Image(graph_builder.get_graph().draw_mermaid_png()))
