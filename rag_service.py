"""
RAG (Retrieval-Augmented Generation) Service for AyuMithra
Provides medical knowledge retrieval for more humanized, informed responses
"""

import os
import pickle
import numpy as np
from typing import List, Optional
from pathlib import Path

class RAGService:
    def __init__(self, knowledge_dir='knowledge_base', index_path='knowledge_base/faiss_index'):
        self.knowledge_dir = Path(knowledge_dir)
        self.index_path = Path(index_path)
        self.model = None
        self.index = None
        self.documents = []
        self.metadata = []
        
        # Load or build index
        self.index_path.mkdir(parents=True, exist_ok=True)
        
    def load_embedding_model(self):
        """Load sentence transformer model for embeddings"""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                print("Loading embedding model (first time takes ~30 seconds)...")
                # Using a lightweight, fast model
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✓ Embedding model loaded successfully")
                return True
            except Exception as e:
                print(f"✗ Error loading embedding model: {e}")
                print("RAG system will use fallback keyword-based retrieval")
                self.model = None
                return False
        return True
    
    def load_documents(self) -> List[str]:
        """Load all markdown documents from knowledge base"""
        documents = []
        metadata = []
        
        if not self.knowledge_dir.exists():
            print(f"Knowledge directory not found: {self.knowledge_dir}")
            return [], []
        
        # Read all .md files
        for md_file in self.knowledge_dir.glob('*.md'):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Split into chunks (500 tokens each with overlap)
                chunks = self._split_into_chunks(content, chunk_size=500, overlap=50)
                
                for i, chunk in enumerate(chunks):
                    documents.append(chunk)
                    metadata.append({
                        'source': md_file.name,
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    })
                    
                print(f"✓ Loaded {md_file.name}: {len(chunks)} chunks")
                
            except Exception as e:
                print(f"Error loading {md_file.name}: {e}")
        
        self.documents = documents
        self.metadata = metadata
        return documents, metadata
    
    def _split_into_chunks(self, text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # Count words (rough token count)
            word_count = len(paragraph.split())
            
            # If adding this paragraph exceeds chunk size
            if current_length + word_count > chunk_size and current_chunk:
                # Save current chunk
                chunks.append('\n\n'.join(current_chunk))
                
                # Keep last few words for overlap
                overlap_text = ' '.join(current_chunk[-1].split()[-overlap:]) if current_chunk else ''
                current_chunk = [overlap_text, paragraph] if overlap_text else [paragraph]
                current_length = word_count + (overlap if overlap_text else 0)
            else:
                current_chunk.append(paragraph)
                current_length += word_count
        
        # Don't forget the last chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def build_index(self):
        """Build FAISS index from knowledge base documents"""
        print("\n=== Building RAG Knowledge Base ===")
        
        # Load model
        if not self.load_embedding_model():
            return False
        
        # Load documents
        documents, metadata = self.load_documents()
        
        if not documents:
            print("✗ No documents found in knowledge base")
            return False
        
        print(f"\nTotal documents: {len(documents)} chunks")
        print("Creating embeddings...")
        
        # Create embeddings
        embeddings = self.model.encode(documents, show_progress_bar=True)
        
        # Create FAISS index
        try:
            import faiss
            dimension = embeddings.shape[1]
            
            # Create index
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings.astype('float32'))
            
            # Save index and metadata
            faiss.write_index(self.index, str(self.index_path / 'index.faiss'))
            
            with open(self.index_path / 'index.pkl', 'wb') as f:
                pickle.dump({
                    'documents': documents,
                    'metadata': metadata
                }, f)
            
            print(f"\n✓ Knowledge base built successfully!")
            print(f"✓ Index saved to: {self.index_path}")
            print(f"✓ Total chunks indexed: {len(documents)}")
            return True
            
        except Exception as e:
            print(f"Error building FAISS index: {e}")
            return False
    
    def load_index(self) -> bool:
        """Load existing FAISS index"""
        try:
            import faiss
            
            index_file = self.index_path / 'index.faiss'
            metadata_file = self.index_path / 'index.pkl'
            
            if not index_file.exists() or not metadata_file.exists():
                print("No existing index found, building new one...")
                return self.build_index()
            
            # Load index
            self.index = faiss.read_index(str(index_file))
            
            # Load documents and metadata
            with open(metadata_file, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.metadata = data['metadata']
            
            # Load model
            self.load_embedding_model()
            
            print(f"✓ Knowledge base loaded: {len(self.documents)} chunks")
            return True
            
        except Exception as e:
            print(f"Error loading index: {e}")
            return self.build_index()
    
    def index_exists(self) -> bool:
        """Check if index already exists"""
        index_file = self.index_path / 'index.faiss'
        metadata_file = self.index_path / 'index.pkl'
        return index_file.exists() and metadata_file.exists()
    
    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """Retrieve top-k most relevant document chunks for a query"""
        try:
            # Load index if not loaded
            if self.index is None:
                if not self.load_index():
                    # Fallback: keyword-based retrieval
                    return self._keyword_retrieve(query, top_k)
            
            # If model failed to load, use keyword retrieval
            if self.model is None:
                return self._keyword_retrieve(query, top_k)
            
            # Create query embedding
            query_embedding = self.model.encode([query])
            
            # Search index
            distances, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            # Retrieve documents
            results = []
            for idx in indices[0]:
                if idx < len(self.documents):
                    results.append(self.documents[idx])
            
            return results
            
        except Exception as e:
            print(f"Error retrieving from knowledge base: {e}")
            return self._keyword_retrieve(query, top_k)
    
    def _keyword_retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """Fallback: Simple keyword-based retrieval"""
        if not self.documents:
            return []
        
        # Extract keywords from query
        query_words = set(query.lower().split())
        
        # Score each document by keyword matches
        scored_docs = []
        for doc in self.documents:
            doc_lower = doc.lower()
            score = sum(1 for word in query_words if word in doc_lower)
            if score > 0:
                scored_docs.append((score, doc))
        
        # Sort by score (highest first) and return top_k
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored_docs[:top_k]]
    
    def add_document(self, file_path: str) -> bool:
        """Add a new document to knowledge base and rebuild index"""
        try:
            # Copy file to knowledge directory
            import shutil
            dest_path = self.knowledge_dir / Path(file_path).name
            shutil.copy(file_path, dest_path)
            
            # Rebuild index
            return self.build_index()
            
        except Exception as e:
            print(f"Error adding document: {e}")
            return False


# Singleton instance
_rag_instance = None

def get_rag_service() -> RAGService:
    """Get or create RAG service singleton"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGService()
    return _rag_instance
