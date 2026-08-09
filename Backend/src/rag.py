from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_ollama import ChatOllama

from decouple import config

from src.qdrant import vector_store

model = ChatOllama(
    model="llama3",
    base_url=config("OLLAMA_BASE_URL", default="http://localhost:11434"),
    temperature=0,
)

condense_prompt = ChatPromptTemplate.from_template("""Given the conversation history and a follow-up question, rewrite the follow-up as a standalone question that includes all necessary context. If there is no history, return the question unchanged.

Chat History:
{chat_history}

Follow-up Question: {question}
Standalone Question:""")

prompt_template = """
Answer the question based only on the context below.
{context}

Question: {question}
Answer:
"""

prompt = ChatPromptTemplate.from_template(prompt_template)

retriever = vector_store.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 4,
        "fetch_k": 20,
        "lambda_mult": 0.5
    }
)


def format_docs_with_sources(docs):
    formatted = []
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source_url", "unknown source")
        formatted.append(f"[{i}] Source: {source}\n{doc.page_content}")
    return "\n\n".join(formatted)


def format_chat_history(chat_history):
    if not chat_history:
        return "None"
    lines = [f"Human: {turn['question']}\nAI: {turn['answer']}" for turn in chat_history]
    return "\n".join(lines)


def condense_question(question: str, chat_history: list) -> str:
    if not chat_history:
        return question
    result = model.invoke(condense_prompt.format(
        chat_history=format_chat_history(chat_history),
        question=question,
    ))
    return result.content


def _prepare(question: str, chat_history: list | None):
    """Runs the non-streaming prep work: condense the question, retrieve docs, build the prompt input."""
    chat_history = chat_history or []
    standalone_question = condense_question(question, chat_history)
    docs = retriever.invoke(standalone_question)
    context_str = format_docs_with_sources(docs)
    prompt_input = {"context": context_str, "question": question}
    return docs, prompt_input


def get_answer_and_docs(question: str, chat_history: list | None = None):
    docs, prompt_input = _prepare(question, chat_history)
    chain = prompt | model
    response = chain.invoke(prompt_input)
    sources = list({
        doc.metadata.get("source_url")
        for doc in docs
        if doc.metadata.get("source_url")
    })
    return {
        "answer": response.content,
        "context": docs,
        "sources": sources,
    }


def stream_answer(question: str, chat_history: list | None = None):
    """Yields answer tokens as they're generated, for a streaming endpoint."""
    docs, prompt_input = _prepare(question, chat_history)
    chain = prompt | model
    for chunk in chain.stream(prompt_input):
        if chunk.content:
            yield chunk.content