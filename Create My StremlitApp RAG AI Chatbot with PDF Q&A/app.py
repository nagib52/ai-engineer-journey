import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# ===== SETUP =====
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.title("My AI Chatbot with PDF Q&A")

# Session state initialize
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None

# ===== SIDEBAR: PDF UPLOAD =====
with st.sidebar:
    st.header("Upload a PDF (optional)")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")

    if uploaded_file is not None:
        # সাময়িকভাবে ফাইল save করা (PyPDFLoader ফাইল path চায়)
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.spinner("Processing PDF..."):
            loader = PyPDFLoader("temp.pdf")
            documents = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
            chunks = text_splitter.split_documents(documents)

            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            st.session_state.vectorstore = FAISS.from_documents(chunks, embeddings)

        st.success("PDF processed! Now ask questions about it.")

# ===== RAG QUERY FUNCTION =====
def rag_query(question):
    relevant_chunks = st.session_state.vectorstore.similarity_search(question, k=2)
    context = "\n".join([chunk.page_content for chunk in relevant_chunks])

    prompt = f"""Answer the question based only on the following context. If the answer is not in the context, say "I don't know based on the document."

Context:
{context}

Question: {question}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ===== DISPLAY CHAT HISTORY =====
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ===== CHAT INPUT =====
user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # যদি PDF আপলোড করা থাকে, RAG দিয়ে উত্তর দাও
            if st.session_state.vectorstore is not None:
                reply = rag_query(user_input)
            else:
                # নাহলে normal chat
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=st.session_state.messages
                )
                reply = response.choices[0].message.content

            st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
