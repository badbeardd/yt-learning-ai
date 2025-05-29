from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Initialize model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def create_vector_store(text: str):
    """Create FAISS vector store from transcript text."""
    chunks = [text[i:i+500] for i in range(0, len(text), 400)]
    embeddings = embedding_model.encode(chunks)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))

    return {'index': index, 'chunks': chunks, 'model': embedding_model}

def get_context_chunks(query: str, store) -> list:
    """Retrieve top relevant chunks from FAISS."""
    query_vec = store['model'].encode([query])
    D, I = store['index'].search(np.array(query_vec), k=4)
    return [store['chunks'][i] for i in I[0]]
