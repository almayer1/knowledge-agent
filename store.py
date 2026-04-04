import chromadb

from models import Chunk, QueryResult
from config import Settings

settings = Settings()
client = chromadb.PersistentClient(path=str(settings.data_dir / "chroma"))

def get_collection():
    collection = client.get_or_create_collection(
        name="knowledge",
        metadata={"hnsw:space": "cosine"}
    )
    return collection

def add_chunks(chunks: list[Chunk]):
    collection = get_collection()
    ids = []
    documents = []
    metadatas = []

    #extract data from chunks
    for chunk in chunks:
        ids.append(chunk.id)
        documents.append(chunk.content)
        metadatas.append(chunk.metadata)

    #store data from chunks
    collection.upsert(
        ids=ids, 
        documents=documents, 
        metadatas=metadatas
    )

#Works for only one question FIXME add scalabiliry for more questions
def query(question: str) -> list[QueryResult]:
    collection = get_collection()
    query_results = []

    #query db
    results = collection.query(
        query_texts=[question],
        n_results=settings.top_k
    )

    #for each result in results convert result to Chunk and score and store as QueryResult
    for i in range(len(results["ids"][0])):
        id = results["ids"][0][i]
        content = results["documents"][0][i]
        metadata = results["metadatas"][0][i]
        distance = results["distances"][0][i]
        score = 1 - distance
        chunk = Chunk(
            id=id, 
            document_id=metadata["document_id"], 
            content=content, 
            metadata=metadata
        )
        query_results.append(
            QueryResult(
                chunk=chunk, 
                score=score
            )
        )
    return query_results

def count() -> int:
    collection = get_collection()
    return collection.count()

