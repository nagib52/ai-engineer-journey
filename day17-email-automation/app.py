import streamlit as st
import os
import re
import pickle
from dotenv import load_dotenv
from groq import Groq
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from email.mime.text import MIMEText

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

st.set_page_config(page_title="AI Email Management Agent", layout="wide")
st.title(" AI Email Management & Response Automation")
st.write("Fetches your recent Gmail messages, categorizes them, scores urgency/sentiment, and drafts replies.")

# ===== Gmail Authentication =====
def get_gmail_service():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as f:
            pickle.dump(creds, f)

    return build("gmail", "v1", credentials=creds)

# ===== Fetch Emails =====
def fetch_recent_emails(service, max_results=10):
    results = service.users().messages().list(
        userId="me", maxResults=max_results, q="in:inbox"
    ).execute()
    messages = results.get("messages", [])

    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()

        headers = msg_data["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(No Subject)")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "(Unknown Sender)")
        snippet = msg_data.get("snippet", "")

        emails.append({
            "id": msg["id"],
            "subject": subject,
            "sender": sender,
            "snippet": snippet
        })
    return emails

# ===== AI Analysis =====
def analyze_email(subject, sender, snippet):
    prompt = f"""You are an AI email assistant. Analyze this email and respond in this EXACT format:

CATEGORY: [one of: Urgent Action, Meeting/Schedule, Sales/Marketing, Support/Complaint, Newsletter/Spam, Personal, Other]
URGENCY: [a number from 1-10]
SENTIMENT: [Positive, Neutral, or Negative]
REPLY_DRAFT: [a short, professional 2-3 sentence reply draft]

Email details:
From: {sender}
Subject: {subject}
Content: {snippet}
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def parse_analysis(text):
    category = re.search(r"CATEGORY:\s*(.+)", text)
    urgency = re.search(r"URGENCY:\s*(\d+)", text)
    sentiment = re.search(r"SENTIMENT:\s*(\w+)", text)
    reply = re.search(r"REPLY_DRAFT:\s*(.+)", text, re.DOTALL)

    return {
        "category": category.group(1).strip() if category else "Other",
        "urgency": int(urgency.group(1)) if urgency else 5,
        "sentiment": sentiment.group(1).strip() if sentiment else "Neutral",
        "reply": reply.group(1).strip() if reply else "Could not generate reply."
    }

# ===== UI =====
max_emails = st.slider("How many recent emails to analyze?", 3, 20, 5)

if st.button("🔍 Fetch & Analyze Emails"):
    with st.spinner("Connecting to Gmail..."):
        service = get_gmail_service()

    with st.spinner(f"Fetching {max_emails} recent emails..."):
        emails = fetch_recent_emails(service, max_results=max_emails)

    if not emails:
        st.warning("No emails found.")
    else:
        st.success(f"Fetched {len(emails)} emails. Analyzing with AI...")

        results = []
        progress = st.progress(0)
        for i, email in enumerate(emails):
            analysis_text = analyze_email(email["subject"], email["sender"], email["snippet"])
            parsed = parse_analysis(analysis_text)
            results.append({**email, **parsed})
            progress.progress((i + 1) / len(emails))

        # Sort by urgency, highest first
        results.sort(key=lambda x: x["urgency"], reverse=True)

        st.subheader(" Analyzed Emails (sorted by urgency)")
        for r in results:
            urgency_color = "🔴" if r["urgency"] >= 7 else "🟡" if r["urgency"] >= 4 else "🟢"
            with st.expander(f"{urgency_color} [{r['category']}] {r['subject']} — from {r['sender']} (Urgency: {r['urgency']}/10)"):
                st.write(f"**Sentiment:** {r['sentiment']}")
                st.write(f"**Snippet:** {r['snippet']}")
                st.write("**Suggested Reply:**")
                st.info(r["reply"])