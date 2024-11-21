from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.callbacks.base import BaseCallbackHandler
from typing import List, Any
import sys
from utils.config import Config

class StreamingHandler(BaseCallbackHandler):
    def __init__(self):
        self.text = ""
        
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        sys.stdout.write(token)
        sys.stdout.flush()
        self.text += token

class RAGSystem:
    def __init__(self, 
                 index_path: str = "./data/indexes",
                 embedding_model: str = 'sentence-transformers/all-MiniLM-L6-v2',
                 device: str = 'mps'):
        # Disable logging for the transformers and FAISS
        import logging
        logging.getLogger('sentence_transformers').setLevel(logging.WARNING)
        logging.getLogger('faiss').setLevel(logging.WARNING)
        
        self.index_path = index_path
        self.embedding_model = embedding_model
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embedding_model,
            model_kwargs={'device': device}
        )
        self.vector_store = FAISS.load_local(
            self.index_path, 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
    def get_context(self, query: str, k: int = 12) -> str:
        """Retrieve relevant context for a query"""
        try:
            retriever = self.vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": k,
                    "fetch_k": 20,
                    "lambda_mult": 0.5
                }
            )
            docs = retriever.invoke(query)
            return self._format_context(docs)
        except Exception as e:
            raise Exception(f"Error retrieving context: {str(e)}")

    def _format_context(self, docs: List[Any]) -> str:
        """Format retrieved documents into a string"""
        context_parts = []
        for i, doc in enumerate(docs, 1):
            metadata = doc.metadata
            context_parts.append(
                f"Document {i}:\n"
                f"Source: {metadata.get('source', 'Unknown')}\n"
                f"Content: {doc.page_content}\n"
            )
        return "\n".join(context_parts)

class PDFTool:
    """Main interface for PDF processing and RAG capabilities"""
    def __init__(self):
        self.config = Config.path_config
        self.rag_system = RAGSystem(
            index_path=self.config.index_dir
        )
        
    def query_documents(self, query: str) -> str:
        """Query the processed documents"""
        return self.rag_system.get_context(query)