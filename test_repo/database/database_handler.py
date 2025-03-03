import sqlite3
import numpy as np
from typing import List, Dict

class DatabaseHandler:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database with necessary tables."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Drop the table if it exists, Every time we start with a fresh database
        c.execute('DROP TABLE IF EXISTS document_chunks')
        
        # Create a new empty table for document chunks
        c.execute('''
            CREATE TABLE document_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk TEXT NOT NULL,
                page_number INTEGER NOT NULL,
                embedding BLOB
            )''')
        
        conn.commit()
        conn.close()
    
    def store_chunked_docs(self, chunked_docs: List[Dict]) -> None:
        """Store document chunks and their embeddings in SQLite."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        for doc in chunked_docs:
            embedding_bytes = np.array(doc["embedding"], dtype=np.float32).tobytes()
            c.execute(
                'INSERT INTO document_chunks (chunk, page_number, embedding) VALUES (?, ?, ?)',
                (doc["chunk"], doc["page_number"], embedding_bytes)
            )
        
        conn.commit()
        conn.close()
        print(f"Stored {len(chunked_docs)} chunks in SQLite database.")

    def _cosine_similarity(self, query_embedding: List[float], doc_embedding: np.ndarray) -> float:
        """Calculate cosine similarity between query and document embeddings."""
        a = np.array(query_embedding)
        b = doc_embedding
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def get_chunks_count(self) -> int:
        """Get the number of chunks in the database."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM document_chunks')
        count = c.fetchone()[0]
        conn.close()
        return count

    async def get_relevant_chunks(self, query: str, k: int = 3, async_client=None) -> List[Dict]:
        """Get top-k relevant chunks for a query using cosine similarity."""
        # Get query embedding
        try:
            query_embedding = await async_client.embeddings.create(
                input=query,
                model="text-embedding-3-small"
            )
            query_embedding = query_embedding.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding for query '{query}': {str(e)}")
            return []

        # Retrieve all chunks and their embeddings
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('SELECT chunk, page_number, embedding FROM document_chunks')
            chunks = c.fetchall()
            conn.close()
        except Exception as e:
            print(f"Error retrieving chunks from database: {str(e)}")
            return []

        # Calculate similarities
        try:
            similarities = []
            for chunk, page_number, embedding_bytes in chunks:
                doc_embedding = np.frombuffer(embedding_bytes, dtype=np.float32)
                similarity = self._cosine_similarity(query_embedding, doc_embedding)
                similarities.append((similarity, chunk, page_number))

            # Sort by similarity and get top-k
            similarities.sort(reverse=True)
            top_k = similarities[:k]

            return [
                {
                    "chunk": chunk,
                    "page_number": page_number,
                    "score": float(score)
                }
                for score, chunk, page_number in top_k
            ]
        except Exception as e:
            print(f"Error calculating similarities: {str(e)}")
            return []
