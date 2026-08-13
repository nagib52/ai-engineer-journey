import streamlit as st
import pandas as pd
import os
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="AI Customer Support Automation Agent", layout="wide")
st.title("🎧 AI Customer Support Automation Agent")
st.write("Upload support tickets to get AI-powered categorization, priority, reply drafts, and escalation flags.")

# ===== File Upload =====
uploaded_file = st.file_uploader("Upload Support Tickets CSV/Excel", type=["csv", "xlsx"])

use_sample = st.checkbox("Use sample data instead (support_tickets.csv)", value=True if not uploaded_file else False)

df = None
if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
elif use_sample and os.path.exists("support_tickets.csv"):
    df = pd.read_csv("support_tickets.csv")

# ===== AI Analysis =====
def analyze_ticket(subject, message):
    prompt = f"""You are an expert customer support triage agent. Analyze this support ticket and respond in this EXACT format:

CATEGORY: [one of: Billing, Technical Issue, Account Access, Feature Request, General Inquiry, Refund/Cancellation]
PRIORITY: [Low, Medium, High, Critical]
ESCALATE: [Yes or No — Yes if this needs a human agent due to complexity, anger, financial impact, or urgency]
REPLY_DRAFT: [a short, empathetic, professional 2-3 sentence reply draft]

Ticket:
Subject: {subject}
Message: {message}
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def parse_analysis(text):
    category = re.search(r"CATEGORY:\s*(.+)", text)
    priority = re.search(r"PRIORITY:\s*(\w+)", text)
    escalate = re.search(r"ESCALATE:\s*(\w+)", text)
    reply = re.search(r"REPLY_DRAFT:\s*(.+)", text, re.DOTALL)

    return {
        "category": category.group(1).strip() if category else "General Inquiry",
        "priority": priority.group(1).strip() if priority else "Medium",
        "escalate": escalate.group(1).strip() if escalate else "No",
        "reply": reply.group(1).strip() if reply else "Could not generate reply."
    }

# ===== UI =====
if df is not None:
    st.subheader("📋 Raw Ticket Data")
    st.dataframe(df, use_container_width=True)

    if st.button("🤖 Analyze Tickets"):
        results = []
        progress = st.progress(0)
        for i, (_, row) in enumerate(df.iterrows()):
            analysis_text = analyze_ticket(row["subject"], row["message"])
            parsed = parse_analysis(analysis_text)
            results.append({**row.to_dict(), **parsed})
            progress.progress((i + 1) / len(df))

        results_df = pd.DataFrame(results)

        priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
        results_df["priority_rank"] = results_df["priority"].map(priority_order).fillna(2)
        results_df = results_df.sort_values("priority_rank")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Tickets", len(results_df))
        col2.metric("Needs Escalation", int((results_df["escalate"].str.lower() == "yes").sum()))
        col3.metric("Critical/High Priority", int(results_df["priority"].isin(["Critical", "High"]).sum()))

        st.subheader("🎫 Triaged Tickets (sorted by priority)")
        for _, r in results_df.iterrows():
            priority_icon = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(r["priority"], "🟡")
            escalate_tag = "🚨 ESCALATE" if str(r["escalate"]).lower() == "yes" else ""

            with st.expander(f"{priority_icon} [{r['category']}] {r['subject']} — {r['customer_name']} {escalate_tag}"):
                c1, c2 = st.columns(2)
                c1.write(f"**Priority:** {r['priority']}")
                c1.write(f"**Category:** {r['category']}")
                c2.write(f"**Escalate to Human:** {r['escalate']}")
                st.write(f"**Original Message:** {r['message']}")
                st.write("**AI Suggested Reply:**")
                st.info(r["reply"])
else:
    st.info("Upload a CSV/Excel file, or check 'Use sample data' to try it with demo tickets.")