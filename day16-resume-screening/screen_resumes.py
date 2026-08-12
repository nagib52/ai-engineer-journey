from dotenv import load_dotenv
from groq import Groq
import os
import re
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_resume_text(pdf_path):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    return "\n".join([doc.page_content for doc in documents])

def score_resume(resume_text, job_description):
    prompt = f"""You are an expert HR recruiter. Compare this resume against the job description.

Job Description:
{job_description}

Resume:
{resume_text}

Give your response in this exact format:
SCORE: [a number from 0-100]
STRENGTHS: [2-3 bullet points on why this candidate fits]
GAPS: [2-3 bullet points on what's missing or weak]
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def extract_score(evaluation_text):
    match = re.search(r"SCORE:\s*(\d+)", evaluation_text)
    return int(match.group(1)) if match else 0

# ===== Use =====
job_description = """
We are looking for a Junior AI Engineer with experience in Python, 
LLM APIs, RAG systems, and basic machine learning. Experience with 
FastAPI and Docker is a plus. CSE degree preferred.
"""

resume_files = ["resume1.pdf", "resume2.pdf"]

results = []
for resume_file in resume_files:
    if os.path.exists(resume_file):
        resume_text = extract_resume_text(resume_file)
        evaluation = score_resume(resume_text, job_description)
        results.append({"file": resume_file, "evaluation": evaluation})

for r in results:
    r["score"] = extract_score(r["evaluation"])

results.sort(key=lambda x: x["score"], reverse=True)

for r in results:
    print(f"\n{'='*50}")
    print(f"Resume: {r['file']}")
    print(r['evaluation'])

print("\n" + "="*50)
print("RANKED CANDIDATES")
print("="*50)
for rank, r in enumerate(results, 1):
    print(f"\n#{rank} — {r['file']} (Score: {r['score']}/100)")