from typing import TypedDict, Annotated
from dotenv import load_dotenv
load_dotenv()
import os
from langchain_groq import ChatGroq
from langgraph.graph import START, END, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import tool
from langgraph.graph.message import BaseMessage, add_messages

os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")
os.environ["TAVILY_API_KEY"]=os.getenv("TAVILY_API_KEY")
os.environ["LANGSMITH_API_KEY"]=os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGSMITH_TRACING"]="true"
os.environ["LANGSMITH_PROJECT"]="TestProject"

# from langchain.chat_models import init_chat_model
# llm=init_chat_model("llama-3.1-8b-instant")

# initializing llm model
llm = ChatGroq(model="llama-3.1-8b-instant", max_tokens=500)

class State(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
    
def graphwithtools():
    #tool 1
    @tool
    def customfun(a: str) -> str:
        """A custom tool that tells about kuttyma when kuttyma is prompted."""
        return "Kuttyma is a cute little lovely woman."

    # tool 2 tavily
    from langchain_tavily import TavilySearch
    tavily_tool = TavilySearch()

    # tool 3 wikipedia

    from langchain_community.tools import WikipediaQueryRun
    from langchain_community.utilities import WikipediaAPIWrapper

    wikiapi = WikipediaAPIWrapper(top_k_results=2)
    wiki_tool = WikipediaQueryRun(api_wrapper=wikiapi)

    tools = [customfun, tavily_tool, wiki_tool]
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
    return graph_builder

tool_agent=graphwithtools()