from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
import os
import json
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
app = FastAPI()

# ===== Document Loading (server startup) =====
pdf_path = "BangladeshsCurrentPS.pdf"  # Your PDF file name
loader = PyPDFLoader(pdf_path)
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(chunks, embeddings)

def search_document(query):
    results = vectorstore.similarity_search(query, k=2)
    return "\n".join([r.page_content for r in results])

def calculator(operation, a, b):
    ops = {"add": a+b, "subtract": a-b, "multiply": a*b, "divide": a/b if b != 0 else "Error"}
    return str(ops.get(operation, "Unknown operation"))

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_document",
            "description": "Search the document for relevant information",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform math calculations",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {"type": "string"},
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["operation", "a", "b"]
            }
        }
    }
]

class Question(BaseModel):
    question: str

@app.post("/ask")
def ask(q: Question):
    conversation = [
        {"role": "system", "content": "You are a study assistant. Use tools when needed."},
        {"role": "user", "content": q.question}
    ]

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=conversation,
        tools=tools,
        tool_choice="auto"
    )
    message = response.choices[0].message

    if message.tool_calls:
        conversation.append(message)
        for tool_call in message.tool_calls:
            fname = tool_call.function.name
            fargs = json.loads(tool_call.function.arguments)
            if fname == "search_document":
                result = search_document(fargs["query"])
            elif fname == "calculator":
                result = calculator(fargs["operation"], fargs["a"], fargs["b"])
            else:
                result = "Unknown tool"
            conversation.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})

        final = client.chat.completions.create(model="llama-3.1-8b-instant", messages=conversation)
        return {"answer": final.choices[0].message.content}
    else:
        return {"answer": message.content}