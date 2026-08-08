from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_ollama import ChatOllama
from operator import itemgetter

from decouple import config

from src.qdrant import vector_store

model = ChatOllama(
    model="llama3",
    base_url=config("OLLAMA_BASE_URL", default="http://localhost:11434"),
    temperature=0,
)

prompt_template = """
Answer the question based only on the context below, in a concise manner and using bullet points where applicable.
Cite sources inline using [1], [2], etc. matching the numbered context blocks below.
If the context doesn't contain enough information to answer, say "I don't have enough information to answer that" instead of guessing.

Context:
{context}

Question: {question}
Answer:
"""

prompt = ChatPromptTemplate.from_template(prompt_template)

retriever = vector_store.as_retriever(search_kwargs={"k": 4})


def format_docs_with_sources(docs):
    """Turns retrieved chunks into a numbered, source-tagged block so the LLM can cite them as [1], [2]..."""
    formatted = []
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source_url", "unknown source")
        formatted.append(f"[{i}] Source: {source}\n{doc.page_content}")
    return "\n\n".join(formatted)


def create_chain():
    chain = (
        {
            "docs": retriever,
            "question": RunnablePassthrough(),
        }
        | RunnableParallel({
            "response": (
                {
                    "context": itemgetter("docs") | RunnableLambda(format_docs_with_sources),
                    "question": itemgetter("question"),
                }
                | prompt
                | model
            ),
            "context": itemgetter("docs"),
        })
    )
    return chain


def get_answer_and_docs(question: str):
    chain = create_chain()
    response = chain.invoke(question)
    answer = response["response"].content
    context = response["context"]
    sources = list({
        doc.metadata.get("source_url")
        for doc in context
        if doc.metadata.get("source_url")
    })
    return {
        "answer": answer,
        "context": context,
        "sources": sources,
    }