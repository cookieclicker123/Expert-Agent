import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import json

# Function to read all text files and prepare them for vector embedding
def load_and_split_texts(text_folder):
    # Use different splitters based on content type
    dense_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=400,
        separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""]
    )
    
    regular_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", "!", "?", ";", ":", " ", ""]
    )
    
    texts = []
    metadatas = []
    
    for file_name in os.listdir(text_folder):
        if file_name.endswith('.json'):
            with open(os.path.join(text_folder, file_name), "r") as file:
                data = json.load(file)
                text = data["text"]
                doc_metadata = data["metadata"]
                
                # Choose splitter based on document type or content
                is_dense_content = any(term in text.lower() 
                    for term in ['financial statement', 'balance sheet', 'income statement'])
                
                splitter = dense_splitter if is_dense_content else regular_splitter
                chunks = splitter.split_text(text)
                
                # Add chunks and metadata
                texts.extend(chunks)
                for i, chunk in enumerate(chunks):
                    chunk_metadata = {
                        **doc_metadata,
                        "chunk_id": i,
                        "total_chunks": len(chunks),
                        "chunk_size": len(chunk),
                        "chunking_strategy": "dense" if is_dense_content else "regular"
                    }
                    metadatas.append(chunk_metadata)
    
    return texts, metadatas

# Create FAISS index from text files
def create_faiss_index(text_folder, index_path, embedding_model='sentence-transformers/all-MiniLM-L6-v2'):
    texts, metadatas = load_and_split_texts(text_folder)
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    vector_store = FAISS.from_texts(texts, embeddings, metadatas=metadatas)

    # Save the FAISS index to disk
    vector_store.save_local(index_path)
    print(f"FAISS index saved to {index_path}")

if __name__ == "__main__":
    # The folder where text files are saved
    text_folder = "./data/processed"
    # The path where you want to save the FAISS index
    index_path = "./data/indexes"
    create_faiss_index(text_folder, index_path)
