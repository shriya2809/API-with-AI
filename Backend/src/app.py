from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from src.rag import get_answer_and_docs, stream_answer
from src.qdrant import upload_website_to_collection
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI(
    title="RAG API",
    description="A simple RAG API",
    version="0.1",
)

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
)

class ChatTurn(BaseModel):
    question: str
    answer: str

class Message(BaseModel):
    message: str
    chat_history: Optional[List[ChatTurn]] = []


@app.post("/chat", description="Chat with the RAG API through this endpoint")
def chat(message: Message):
    history = [turn.dict() for turn in message.chat_history]
    response = get_answer_and_docs(message.message, chat_history=history)

    response_content = {
        "question": message.message,
        "answer": response["answer"],
        "sources": response["sources"],
        "documents": [
            doc.dict() for doc in response["context"]
        ]
    }

    return JSONResponse(content=response_content, status_code=200)


@app.post("/chat/stream", description="Chat with the RAG API, streaming tokens as they're generated")
def chat_stream(message: Message):
    history = [turn.dict() for turn in message.chat_history]

    def event_generator():
        for token in stream_answer(message.message, chat_history=history):
            yield f"data: {json.dumps(token)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/indexing", description="Index a website through this endpoint")
def indexing(url: str):
    try:
        response = upload_website_to_collection(url)
        return JSONResponse(content={"response": response}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)