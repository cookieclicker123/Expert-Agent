import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Function to read all text files and prepare them for vector embedding
def load_and_split_texts(text_folder):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    texts = []
    for file_name in os.listdir(text_folder):
        if file_name.endswith(".txt"):
            with open(os.path.join(text_folder, file_name), "r") as file:
                text = file.read()
                chunks = text_splitter.split_text(text)
                texts.extend(chunks)
    return texts

# Create FAISS index from text files
def create_faiss_index(text_folder, index_path, embedding_model='sentence-transformers/all-MiniLM-L6-v2'):
    texts = load_and_split_texts(text_folder)
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    metadatas = [{"source": f"chunk_{i}"} for i in range(len(texts))]
    vector_store = FAISS.from_texts(texts, embeddings, metadatas=metadatas)

    # Save the FAISS index to disk
    vector_store.save_local(index_path)
    print(f"FAISS index saved to {index_path}")

if __name__ == "__main__":
    # The folder where text files are saved
    text_folder = "DataTxt"
    # The path where you want to save the FAISS index
    index_path = "DataIndex"
    create_faiss_index(text_folder, index_path)
