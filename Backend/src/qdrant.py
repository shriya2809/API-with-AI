from decouple import config
from langchain_community.document_loaders import WebBaseLoader
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient, models

qdrant_api_key = config("QDRANT_API_KEY", default=None)
qdrant_url = config("QDRANT_URL")
ollama_url = config("OLLAMA_BASE_URL", default="http://localhost:11434")
collection_name = "Websites"

client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key
)

# Create collection automatically if it does not exist
if not client.collection_exists(collection_name=collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE)
    )
    print(f"Collection '{collection_name}' created successfully.")

embeddings = OllamaEmbeddings(
    model="nomic-embed-text", 
    base_url=ollama_url
)

vector_store = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=embeddings
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    length_function=len,
    separators=["\n\n", "\n", ". ", " ", ""],  # tries paragraph -> sentence -> word
)

def upload_website_to_collection(url: str):
    loader = WebBaseLoader(url)
    docs = loader.load_and_split(text_splitter)
    for doc in docs:
        doc.metadata = {"source_url": url}

    vector_store.add_documents(docs)
    return f"Successfully uploaded {len(docs)} documents to collection {collection_name}"