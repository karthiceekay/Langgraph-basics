from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from IPython.display import display, Image

class State(BaseModel):
    name: str
    age: int


def addname(state: State):
    return {"name" : state.name + " added", "age" : state.age + 1}

def addanother(state: State):
    return {"name" : state.name + " again", "age" : state.age + 50}

def filtered(state: State):
    return {}

def cond_filter(state: State):
    if state.age > 30:
        return "firstname"
    else:
        return "lastname"

graph = StateGraph(state_schema=State)
graph.add_node("firstname", addname)
graph.add_node("lastname", addanother)
graph.add_node("filter", filtered)

graph.add_edge(START, "filter")
graph.add_conditional_edges("filter", cond_filter)
graph.add_edge("firstname", END)
graph.add_edge("lastname", END)
final = graph.compile()
display(Image(final.get_graph().draw_mermaid_png(output_file_path="graph.png")))

if __name__ == "__main__":
    result = final.invoke({"name": "John", "age": 35})
    print(result)