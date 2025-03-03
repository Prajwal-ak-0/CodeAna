from openai import AsyncOpenAI
from typing import List, Dict
from dotenv import load_dotenv
import os
import time
import asyncio
from chunking import CustomChunking

load_dotenv()

class AsyncEmbeddingGenerator:
    def __init__(self, model: str = "text-embedding-3-small", batch_size: int = 15):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.batch_size = batch_size

    async def embed_batch(self, batch: List[Dict]) -> List[Dict]:
        texts = [chunk["text"] for chunk in batch]
        try:
            response = await self.client.embeddings.create(
                input=texts,
                model=self.model
            )
            return [
                {
                    "page_number": batch[i]["page_number"],
                    "chunk": batch[i]["text"],
                    "embedding": response.data[i].embedding
                }
                for i in range(len(batch))
            ]
        except Exception as e:
            print(f"Error embedding batch: {str(e)}")
            return []

    async def embed_chunks(self, chunked_document: List[Dict]) -> List[Dict]:
        embedded_document = []
        for i in range(0, len(chunked_document), self.batch_size):
            batch = chunked_document[i:i + self.batch_size]
            try:
                result = await self.embed_batch(batch)
                embedded_document.extend(result)
            except Exception as e:
                print(f"Error processing batch: {str(e)}")
        
        return embedded_document

    def print_embeddings(self, embedded_document: List[Dict], num_words: int = 10, num_embedding: int = 5) -> None:
        if not embedded_document:
            print("No embeddings to display.")
            return

        for item in embedded_document:
            page_number = item.get("page_number", "Unknown")
            chunk = item.get("chunk", "")
            embedding = item.get("embedding", [])
            chunk_preview = ' '.join(chunk.split()[:num_words]) + ("..." if len(chunk.split()) > num_words else "")
            embedding_preview = embedding[:num_embedding]
            print(f"--- Page {page_number} ---")
            print(f"Chunk Preview: {chunk_preview}")
            print(f"Embedding Preview: {embedding_preview}")
            print("\n" + "-" * 50 + "\n")

async def main():
    start_time = time.time()

    chunker = CustomChunking(overlap_words=100)
    file_path = "Stream.pdf"
    complete_file_path = os.path.join("contract_file", file_path)
    chunked_document = chunker.process_file(complete_file_path)

    intermediate_time = time.time()
    print(f"Time taken in chunking: {intermediate_time - start_time:.2f} seconds")

    if chunked_document:
        print(f"Total chunks to process: {len(chunked_document)}")
        embedding_generator = AsyncEmbeddingGenerator(batch_size=10)
        embedded_document = await embedding_generator.embed_chunks(chunked_document)
        print(f"Total embeddings generated: {len(embedded_document)}")

    end_time = time.time()
    print(f"Time taken in embedding: {end_time - intermediate_time:.2f} seconds")
    print(f"Total time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
