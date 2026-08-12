from dotenv import load_dotenv
from groq import Groq
import os
from typing import TypedDict
from langgraph.graph import StateGraph, END

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class State(TypedDict):
    topic: str
    research: str
    final_answer: str

def researcher_agent(state: State) -> State:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a researcher. Give 3-4 key facts about the topic, concisely."},
            {"role": "user", "content": state["topic"]}
        ]
    )
    state["research"] = response.choices[0].message.content
    return state

def writer_agent(state: State) -> State:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a writer. Turn these research facts into a short, engaging paragraph."},
            {"role": "user", "content": state["research"]}
        ]
    )
    state["final_answer"] = response.choices[0].message.content
    return state

# ===== Graph creation =====
graph = StateGraph(State)

graph.add_node("researcher", researcher_agent)
graph.add_node("writer", writer_agent)

graph.set_entry_point("researcher")
graph.add_edge("researcher", "writer")
graph.add_edge("writer", END)

app = graph.compile()

# ===== Run =====
result = app.invoke({"topic": "Benefits of learning AI Engineering", "research": "", "final_answer": ""})

print("=== FINAL RESULT ===")
print(result["final_answer"])