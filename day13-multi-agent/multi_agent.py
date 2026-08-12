from dotenv import load_dotenv
from groq import Groq
import os
from typing import TypedDict

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ===== State: All agent are shared information =====
class State(TypedDict):
    topic: str
    research: str
    final_answer: str

# ===== Agent 1: Researcher =====
def researcher_agent(state: State) -> State:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a researcher. Give 3-4 key facts about the topic, concisely."},
            {"role": "user", "content": state["topic"]}
        ]
    )
    state["research"] = response.choices[0].message.content
    print("Researcher output:\n", state["research"])
    return state

# ===== Agent 2: Writer =====
def writer_agent(state: State) -> State:
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a writer. Turn these research facts into a short, engaging paragraph."},
            {"role": "user", "content": state["research"]}
        ]
    )
    state["final_answer"] = response.choices[0].message.content
    print("\nWriter output:\n", state["final_answer"])
    return state

# ===== Initial State =====
initial_state: State = {"topic": "Benefits of learning AI Engineering", "research": "", "final_answer": ""}

state = researcher_agent(initial_state)
state = writer_agent(state)

print("\n=== FINAL RESULT ===")
print(state["final_answer"])