# RAG App

A simple full-stack Retrieval-Augmented Generation (RAG) system for indexing websites and asking questions about their content. Built with FastAPI and React.

## Features

- Index any website by URL into a vector database
- Ask natural-language questions and get answers grounded in indexed content
- Automatic text chunking and embedding of website content
- Local LLM inference via Ollama (no external API keys required)
- Simple chat-style interface with loading indicator

## Tech Stack

- **Backend:** FastAPI, LangChain, Qdrant, Ollama
- **Frontend:** React, Axios, react-spinners

## Project Structure

```
Backend/
├── src/
│   ├── app.py
│   ├── qdrant.py
│   └── rag.py
├── .env
├── poetry.lock
└── pyproject.toml

fronten/
├── public/
└── src/
    ├── App.js
    ├── App.css
    └──  index.js
```

## Setup

### Backend

Install dependencies with Poetry:

```bash
poetry install
```

Create a `.env` file in the `Backend` folder:

```
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
OLLAMA_BASE_URL=http://localhost:11434
```

Make sure Ollama is running locally with the required models pulled:

```bash
ollama pull nomic-embed-text
ollama pull llama3
```

Run the server:

```bash
uvicorn app:app --reload
```

The API runs at `http://localhost:8000`. Interactive docs are at `http://localhost:8000/docs`.

### Frontend

```bash
npm install
npm start
```

The app runs at `http://localhost:3000`.

## API Endpoints

| Method | Endpoint    | Description                                          |
|--------|-------------|-------------------------------------------------------|
| POST   | `/chat`     | Ask a question and get an answer with supporting docs |
| POST   | `/indexing` | Index a website by URL into the vector store          |
