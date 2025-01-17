from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import os
import logging
from typing import List, Dict
import numpy as np

class EmbeddingHandler:
    def __init__(self, supabase_client=None):
        self.batch_size = 10
        self.collection_name = "crawled_data"
        self.supabase_client = supabase_client
        
        # Initialize embedding model
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
        except Exception as e:
            logging.error(f"Error loading model: {e}")
            raise
            
        # Initialize ChromaDB with new client configuration
        try:
            persist_dir = os.path.join(os.getcwd(), ".chromadb")
            self.client = chromadb.PersistentClient(path=persist_dir)
            
            # Get or create collection
            try:
                self.collection = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
                )
            except Exception as e:
                logging.error(f"Error getting/creating collection: {e}")
                raise
                
        except Exception as e:
            logging.error(f"Error initializing ChromaDB: {e}")
            raise
    
    def clean_text(self, text: str) -> str:
        """Clean and prepare text for embedding."""
        if not isinstance(text, str):
            return ""
        # Remove excessive whitespace and normalize
        return " ".join(text.split())
    
    def generate_document_id(self, url: str, index: int) -> str:
        """Generate a unique document ID."""
        return f"{url}_{index}"
    
    def process_and_store(self, crawled_data: List[Dict]) -> bool:
        """Process crawled data and store embeddings."""
        try:
            # Clear existing data for the same URLs
            urls = set(item['url'] for item in crawled_data)
            for url in urls:
                try:
                    self.collection.delete(where={"url": {"$eq": url}})
                except Exception as e:
                    logging.warning(f"Error clearing existing data: {e}")
                    continue
            
            for i in range(0, len(crawled_data), self.batch_size):
                batch = crawled_data[i:i + self.batch_size]
                
                texts = [self.clean_text(item.get('content', '')) for item in batch]
                # Filter out empty texts
                valid_indices = [idx for idx, text in enumerate(texts) if text and len(text) > 10]
                if not valid_indices:
                    continue
                    
                texts = [texts[idx] for idx in valid_indices]
                batch = [batch[idx] for idx in valid_indices]
                
                try:
                    # Generate embeddings
                    embeddings = self.model.encode(texts, convert_to_tensor=False)
                    
                    # Prepare data for storage
                    ids = [self.generate_document_id(item['url'], idx) for idx, item in enumerate(batch)]
                    metadatas = [{
                        'url': item['url'],
                        'title': item.get('title', ''),
                        'content': item.get('content', '')[:1000]  # Store first 1000 chars
                    } for item in batch]
                    
                    # Store in ChromaDB
                    self.collection.add(
                        embeddings=embeddings.tolist(),
                        documents=texts,
                        metadatas=metadatas,
                        ids=ids
                    )
                    
                    # Store in Supabase if client is available
                    if self.supabase_client:
                        logging.info(f"Starting Supabase operations for batch with {len(batch)} items")
                        for idx, item in enumerate(batch):
                            try:
                                logging.info(f"Processing item {idx + 1}/{len(batch)} - URL: {item['url']}")
                                
                                # First delete existing record
                                delete_result = self.supabase_client.table("crawled_data").delete().eq("url", item['url']).execute()
                                logging.info(f"Delete result: {delete_result}")
                                
                                # Convert embedding to list and ensure it's the correct length (384)
                                embedding_vector = embeddings[idx].tolist()
                                if len(embedding_vector) != 384:
                                    logging.error(f"Embedding vector length mismatch. Expected 384, got {len(embedding_vector)}")
                                    continue
                                
                                # Prepare the data to insert
                                insert_data = {
                                    "url": item['url'],
                                    "content": item.get('content', '')[:1000],
                                    "embedding": embedding_vector
                                }
                                logging.info(f"Preparing to insert data: {insert_data['url']}")
                                
                                # Then insert new record
                                insert_result = self.supabase_client.table("crawled_data").insert(insert_data).execute()
                                logging.info(f"Insert result: {insert_result}")
                                
                            except Exception as e:
                                logging.error(f"Supabase storage error for {item['url']}: {str(e)}")
                                logging.error(f"Full error details: {repr(e)}")
                                continue
                    else:
                        logging.warning("Supabase client is not available - skipping database storage")
                    
                except Exception as e:
                    logging.error(f"Error processing batch: {e}")
                    continue
            
            return True
            
        except Exception as e:
            logging.error(f"Error in process_and_store: {e}")
            return False
    
    def query_similar(self, query: str, url_filter: str = None, top_k: int = 3) -> List[Dict]:
        """Query similar documents."""
        try:
            # Generate query embedding
            query_embedding = self.model.encode(query, convert_to_tensor=False)
            
            # Prepare where clause if URL filter is provided
            where = {"url": {"$eq": url_filter}} if url_filter else None
            
            # Query the collection
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                where=where
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and results['ids'][0]:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else 0
                    })
            
            return formatted_results
            
        except Exception as e:
            logging.error(f"Error in query_similar: {e}")
            return [] 