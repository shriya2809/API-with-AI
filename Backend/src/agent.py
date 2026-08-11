from decouple import config
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.db.sqlite import SqliteDb

from src.qdrant import knowledge_base

ollama_url = config("OLLAMA_BASE_URL", default="http://localhost:11434")

db = SqliteDb(db_file="tmp/rag_sessions.db")


def build_agent(session_id: str | None = None) -> Agent:
    return Agent(
        model=Ollama(id="llama3.1", host=ollama_url),
        knowledge=knowledge_base,
        search_knowledge=True,
        db=db,
        session_id=session_id,
        add_history_to_context=True,   
        num_history_runs=5,
        instructions=[
            "Answer using only information from your knowledge base.",
            "Be concise, using bullet points where useful.",
            "If you don't have enough information, say so instead of guessing.",
        ],
        markdown=False,
    )


def _extract_sources(run_output) -> list[str]:
    """Best-effort: pulls source_url metadata out of the knowledge-search tool call, if one happened."""
    sources = set()
    try:
        for tool in (run_output.tools or []):
            if tool.result:
                for item in tool.result:
                    if isinstance(item, dict):
                        meta = item.get("meta_data") or item.get("metadata") or {}
                        src = meta.get("source_url")
                        if src:
                            sources.add(src)
    except Exception:
        pass
    return list(sources)


def get_answer_and_docs(question: str, session_id: str | None = None) -> dict:
    agent = build_agent(session_id=session_id)
    response = agent.run(question, session_id=session_id)
    return {
        "answer": response.content,
        "sources": _extract_sources(response),
    }


def stream_answer(question: str, session_id: str | None = None):
    agent = build_agent(session_id=session_id)
    for chunk in agent.run(question, session_id=session_id, stream=True):
        if getattr(chunk, "content", None):
            yield chunk.content