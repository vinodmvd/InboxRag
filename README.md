# InboxRag

## Overview

InboxRag is an automated Retrieval-Augmented Generation (RAG) pipeline that connects to a Gmail account, retrieves PDF attachments (such as bank or credit card statements), extracts and chunks document content, generates semantic vector embeddings, stores them in a vector database, and enables natural-language querying through an LLM interface.

---

## Features

- Gmail API integration for automatic PDF attachment retrieval  
- PDF document text extraction and token-level chunking  
- Semantic embedding generation for similarity-based document search  
- Vector database support (Pinecone, Chroma, FAISS, or other providers)  
- LLM-driven contextual query answering  
- Fully automated ingestion, retrieval, and reasoning workflow  

---

## Use Cases

- Querying financial statements: “How much did I spend on dining last month?”  
- Merchant-level search across documents: “Show all transactions from Amazon in 2024.”  
- Monthly summaries: “Summarize expenses for May 2025.”  
- Identifying high-value transactions: “What is the highest transaction across all statements?”  

---

## RAG Pipeline Architecture

1. Fetch email messages with PDF attachments using the Gmail API  
2. Download PDF attachments to local storage  
3. Extract readable text from each PDF document  
4. segment extracted text into smaller token-based chunks  
5. generate vector embeddings from each chunk using a semantic embedding model  
6. store embeddings and metadata in a vector database index  
7. run similarity search on user query, retrieve the most relevant chunks, provide them as LLM context, and generate results  

---

##Missing files from GIT, that are required to be added. 

1. query_retriever/prompt.txt -> Required for the Final LLM's Instructions as a system prompt. 
2. query_retriever/agent/system_prompt.py -> Required for the controller agent instruction as a system prompt.

---

## Project Structure

```
InboxRag
├─ data_ingestion # Gmail fetch, PDF parsing, chunking, and embedding storage pipeline
├─ query_retriever # Query handling, vector retrieval, and LLM answer generation pipeline
├─ .gitignore
└─ README.md
```
