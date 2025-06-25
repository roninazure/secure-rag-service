# Secure RAG Service

![Python CI](https://github.com/roninazure/privategpt-service/actions/workflows/python-ci.yml/badge.svg)

**Proof-of-Concept** of a private RAG pipeline using FastAPI, AWS Bedrock & Pinecone.

## Getting Started
1. Clone this repo  
2. `cd privategpt-service && python -m venv venv && source venv/bin/activate`  
3. `pip install -r requirements.txt`  
4. `uvicorn src.main:app --reload`  
