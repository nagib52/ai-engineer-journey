from dotenv import load_dotenv
from groq import Groq
import os
import time
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

pdf_path = "BangladeshsCurrentSituation-PandS.pdf"  # pdf name
loader = PyPDFLoader(pdf_path)
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = text_splitter.split_documents(documents)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(chunks, embeddings)

def rag_query(question):
    relevant_chunks = vectorstore.similarity_search(question, k=2)
    context = "\n".join([c.page_content for c in relevant_chunks])
    prompt = f"""Answer based only on the context below. If the answer is not in the context, say "I don't know based on the document."

Context:
{context}

Question: {question}
Answer:"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ===== TEST SET =====
test_questions = [
    {"question": "What is this document about?", "expected_keywords": ["income", "inequality"]},
    {"question": "What causes income inequality according to the document?", "expected_keywords": ["land", "taxation", "power"]},
    {"question": "What is the capital of France?", "expected_keywords": ["don't know", "not"]},
]

# ===== EVALUATION LOOP =====
results = []
for test in test_questions:
    start_time = time.time()
    answer = rag_query(test["question"])
    elapsed = round(time.time() - start_time, 2)

    keyword_found = any(kw.lower() in answer.lower() for kw in test["expected_keywords"])

    results.append({
        "question": test["question"],
        "answer": answer,
        "passed": keyword_found,
        "response_time": elapsed
    })

# ===== REPORT =====
print("=" * 50)
print("EVALUATION REPORT")
print("=" * 50)
passed_count = 0
for r in results:
    status = "✅ PASS" if r["passed"] else "❌ FAIL"
    print(f"\n{status} | Time: {r['response_time']}s")
    print(f"Q: {r['question']}")
    print(f"A: {r['answer'][:150]}...")
    if r["passed"]:
        passed_count += 1

print("\n" + "=" * 50)
print(f"Score: {passed_count}/{len(results)} passed")
avg_time = round(sum(r["response_time"] for r in results) / len(results), 2)
print(f"Average response time: {avg_time}s")