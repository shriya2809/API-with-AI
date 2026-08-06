from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
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
Answer the question based on the context, in a concise manner and using bullet points where applicable.

Context: {context}
Question: {question}
Answer:
"""

prompt = ChatPromptTemplate.from_template(prompt_template)

retriever = vector_store.as_retriever()

def create_chain():
    chain = (
        {
            "context": retriever,
            "question": RunnablePassthrough(),
        }
        | RunnableParallel({
            "response": prompt | model,
            "context": itemgetter("context"),
        })
    )
    return chain

def get_answer_and_docs(question: str):
    chain = create_chain()
    response = chain.invoke(question)
    answer = response["response"].content
    context = response["context"]
    return {
        "answer": answer,
        "context": context
    }