# AI Engineer Journey

Hi, I'm Nagib Mahfuj — a CSE graduate building hands-on experience in AI Engineering, with a focus on LLMs, RAG systems, and AI agents. This repo documents the projects I've built while working toward an AI Engineer role — from foundational ML to production-style RAG, multi-agent systems, and deployment.

## Projects

AI Resume Screening & Candidate Ranking System

Scores and ranks resumes against a job description using RAG-style LLM reasoning — returns a match score, strengths, and gaps for each candidate. Stack: Python, Groq API, LangChain, PyPDF View Project

AI Customer Support Automation Agent

Automatically categorizes incoming support tickets, assigns priority, drafts a reply, and flags cases for escalation. Stack: Python, Groq API, Agent/Tool-calling View Project

AI Email Management & Response Automation

Connects to a real Gmail inbox via OAuth, categorizes incoming emails, scores sentiment/urgency, and drafts replies. Stack: Python, Gmail API (OAuth), Groq API View Project

AI Inventory & Purchase Recommendation Assistant

Analyzes inventory data and recommends what to purchase based on stock levels and demand patterns. Stack: Python, Pandas, Groq API View Project

Multi-Agent System (LangGraph)

A researcher → writer agent pipeline where one agent's output feeds into the next, built as a proper LangGraph state graph. Stack: LangGraph, Groq API View Project

RAG + Tool-Calling Study Assistant

An agent that combines document search (RAG) and a calculator tool, deciding on its own which to use based on the question. Stack: LangChain, FAISS, Groq API View Project

FastAPI Backend + Docker

Wraps the RAG + tool-calling agent as a REST API and containerizes it with Docker for portable deployment. Stack: FastAPI, Docker, Groq API View Project

RAG PDF Q&A Web App

A Streamlit app where users upload a PDF and ask questions about it, answered using retrieval-augmented generation. Stack: Streamlit, LangChain, FAISS View Project

AI Agent with Tool Calling

An agent that dynamically decides when to use tools (calculator, weather, currency converter) to answer a question. Stack: Groq API, function calling View Project

LLM Evaluation Framework

A lightweight evaluation script for a RAG pipeline — keyword-based correctness checks, hallucination detection on out-of-scope questions, and response-time measurement. Stack: Python, Groq API View Project

LoRA Fine-Tuning

Hands-on parameter-efficient fine-tuning of a language model using LoRA, run on free Kaggle GPU. Stack: Transformers, PEFT View Project

SQL Fundamentals

Core SQL operations — table creation, inserts, filtering, aggregation, and joins — using SQLite from Python. Stack: Python, sqlite3 View Project

Titanic ML Analysis

Data cleaning, EDA, and classification models (Logistic Regression, Random Forest) on the classic Titanic dataset. Stack: Pandas, scikit-learn View Project

Skills

Languages & Core: Python, SQL AI/LLM: Groq API, LangChain, LangGraph, RAG, FAISS, Prompt Engineering, Fine-tuning (LoRA/PEFT) Agents: Tool/Function Calling, Multi-Agent Systems Backend & Infra: FastAPI, Docker, REST APIs Data & ML: Pandas, NumPy, scikit-learn Tools: Git, GitHub, Streamlit

About This Repo

Each folder is a self-contained project with its own code. This repo reflects a structured, project-based path into AI Engineering — built by shipping working systems rather than just following tutorials.


### 1. Titanic ML Analysis
Data cleaning, EDA, and classification models (Logistic Regression, Random Forest) on the Titanic dataset.
[View Project] (https://github.com/nagib52/ai-engineer-journey/blob/main/api-call-system-prompt-conversation-history.ipynb)

### 2. LLM Chatbot (Groq API)
CLI chatbot using Groq's LLM API with conversation memory and system prompts.
[View Project] (https://github.com/nagib52/ai-engineer-journey/blob/main/rag-retrieval-augmented-generation.ipynb)

### 3. RAG PDF Q&A Streamlit App
A web app that lets users upload a PDF and ask questions about it, powered by RAG (LangChain + FAISS + Groq).
[View Project] (https://github.com/nagib52/ai-engineer-journey/tree/main/stremlit-app-rag-ai-chatbot-with%3Dpdf-q-a)

### 4. AI Agent with Tool Calling
An agent that dynamically decides when to use tools (calculator, weather, currency converter) to answer questions.
[View Project] (https://github.com/nagib52/ai-engineer-journey/tree/main/day6-ai-agent)

### 5. RAG + Tool-Calling Study Assistant
Combines document search (RAG) and calculator tools in a single agent that decides which to use based on the question.
[View Project] (https://github.com/nagib52/ai-engineer-journey/tree/main/day8-study-assistant)

### 6. FastAPI Backend + Docker
Wraps the RAG + tool-calling agent as a REST API using FastAPI, containerized with Docker.
[View Project] (https://github.com/nagib52/ai-engineer-journey/tree/main/day9-fastapi-backend)

### 7. Multi-Agent System (LangGraph)
A researcher-writer agent pipeline built with LangGraph, where one agent's output feeds into the next.
[View Project] (https://github.com/nagib52/ai-engineer-journey/tree/main/day13-multi-agent)

## Skills
Python, Pandas, Numpy, Scikit-learn, LangChain, LangGraph, FAISS, Streamlit, FastAPI, Docker, SQL, Groq API, Git/GitHub

