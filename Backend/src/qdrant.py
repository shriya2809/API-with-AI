from decouple import config
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.embedder.ollama import OllamaEmbedder
from agno.vectordb.qdrant import Qdrant
from agno.vectordb.distance import Distance

qdrant_api_key = config("QDRANT_API_KEY", default=None)
qdrant_url = config("QDRANT_URL")
ollama_url = config("OLLAMA_BASE_URL", default="http://localhost:11434")
collection_name = "Websites_v2"

embedder = OllamaEmbedder(
    id="nomic-embed-text",
    dimensions=768,
    host=ollama_url,
)

vector_db = Qdrant(
    collection=collection_name,
    url=qdrant_url,
    api_key=qdrant_api_key,
    embedder=embedder,
    distance=Distance.cosine,
)

knowledge_base = Knowledge(
    vector_db=vector_db,
)


def upload_website_to_collection(url: str):
    knowledge_base.add_content(url=url, metadata={"source_url": url})
    return f"Successfully indexed {url} into the '{collection_name}' knowledge base"