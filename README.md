# 🎯 ResumeInsight AI

> AI-Powered Resume Analyzer & ATS Optimizer with Retrieval-Augmented Generation (RAG)

A production-ready application that performs **deterministic ATS scoring**, **semantic keyword matching**, **resume quality analysis**, and **AI-powered chat** using RAG — not just a simple LLM wrapper.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://resumeinsig-2zgkeqwwiks9t2ti7z8sgk.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue)](#)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)](#)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-green)](#)
[![Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-Latest-purple)](#)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **ATS Scoring** | Deterministic scoring across 7 weighted dimensions |
| 🔍 **Keyword Analysis** | Exact + Fuzzy (RapidFuzz) + Semantic matching |
| 🧠 **RAG Chat** | Ask questions about your resume using retrieval-augmented generation |
| ✍️ **Bullet Rewriter** | AI-powered bullet point improvement |
| 📝 **Quality Analysis** | Grammar, passive voice, weak verbs, missing metrics detection |
| 🎤 **Interview Prep** | Auto-generated interview questions from resume content |
| 📈 **Visual Dashboard** | Interactive charts: gauge, radar, bar, pie |
| 🔐 **Secure** | API keys in .env, input sanitization, file validation |

---

## 🏗️ Architecture

```
User → Upload Resume (PDF/DOCX) + Job Description
         ↓
    Resume Parsing (PyMuPDF / python-docx)
         ↓
    Section Detection & Info Extraction
         ↓
    Chunking (RecursiveCharacterTextSplitter)
         ↓
    Embeddings (all-MiniLM-L6-v2)
         ↓
    FAISS Vector Index + BM25 Index
         ↓
    Hybrid Retrieval (RRF Fusion)
         ↓
    Gemini 2.5 Flash (LLM)
         ↓
    ATS Report + Chat Answers
```

---

## 🚀 Quick Start

### 1. Clone
```bash
git clone https://github.com/PrathamUdayG/ResumeInsight-AI.git
cd ResumeInsight-AI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Configure API Key
```bash
cp .env.example .env
# Edit .env and add your Gemini API key
```

### 4. Run
```bash
streamlit run app.py
```

---

## 📁 Project Structure

```
ResumeInsight-AI/
├── app.py                 # Main Streamlit application
├── core/
│   ├── parser.py          # PDF/DOCX parsing & info extraction
│   ├── chunking.py        # Text chunking with metadata
│   ├── embeddings.py      # Sentence Transformer embeddings
│   ├── retriever.py       # Hybrid search (FAISS + BM25 + RRF)
│   ├── ats.py             # ATS analysis orchestrator
│   ├── keyword_match.py   # Multi-strategy keyword matching
│   ├── scoring.py         # Deterministic ATS scoring
│   ├── grammar.py         # Quality & grammar analysis
│   ├── prompts.py         # All LLM prompt templates
│   ├── llm.py             # Gemini API integration
│   ├── rewrite.py         # Bullet point rewriter
│   └── interview.py       # Interview question generator
├── utils/
│   ├── constants.py       # All configuration & constants
│   └── helpers.py         # Shared utility functions
├── assets/
│   └── styles.py          # Premium CSS styles
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔧 Tech Stack

- **Frontend**: Streamlit with custom glassmorphism CSS
- **LLM**: Google Gemini 2.5 Flash
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector DB**: FAISS (Inner Product search)
- **Keyword Search**: BM25Okapi (rank-bm25)
- **Fusion**: Reciprocal Rank Fusion (k=60)
- **NLP**: spaCy, RapidFuzz
- **Visualization**: Plotly
- **Document Parsing**: PyMuPDF, python-docx

---

## 📊 ATS Score Weights

| Component | Weight |
|-----------|--------|
| Keyword Match | 30% |
| Skill Match | 20% |
| Experience Match | 15% |
| Education Match | 10% |
| Action Verbs | 10% |
| Quantified Achievements | 10% |
| Formatting | 5% |

---

## 📄 License

MIT License - See LICENSE file for details.

---

**Built by Pratham Uday G** 🚀
