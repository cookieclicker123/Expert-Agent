from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_ollama import OllamaLLM


# Load FAISS index
def load_faiss_index(index_path, embedding_model):
    # Load the FAISS index using the same embedding model
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    return vector_store


# Create the RAG system using FAISS and Ollama (Llama 3.1)
def create_rag_system(index_path, embedding_model='sentence-transformers/all-MiniLM-L6-v2', model_name="llama3.2"):
    # Load the FAISS index
    vector_store = load_faiss_index(index_path, embedding_model)

    # Initialize the Ollama model (Llama3.1)
    llm = OllamaLLM(model=model_name)

    # Create a more detailed prompt template
    prompt_template = """
    You are an expert financial analyst with access to the following context from various financial documents. 
    Your job is to provide detailed, accurate analysis using only the information in the context below.

    Context: {context}

    Question: {question}

    Instructions:
    1. Base your analysis strictly on the provided context
    2. When citing information, specify the source document and timeframe
    3. If analyzing relationships or trends, explicitly state which documents support your analysis
    4. For any metrics or data points, clearly indicate their source and date
    5. If certain information appears outdated or if you need additional context, note this in your response

    Answer in this format:
    Sources Used: [List the specific documents and their dates]
    Analysis: [Your detailed answer based on available context]
    Additional Context Needed: [Optional - only if relevant information appears to be missing]
    """

    # Create a template for formatting the input for the model
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=prompt_template
    )

    # Create a RetrievalQA chain that combines the vector store with the model
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 12,
                "fetch_k": 20,
                "lambda_mult": 0.5
            }
        ),
        chain_type_kwargs={"prompt": prompt}
    )

    return qa_chain


# Function to run the RAG system with a user question
def get_answer(question, qa_chain):
    answer = qa_chain.invoke({"query": question})
    return answer["result"]


if __name__ == "__main__":
    # Path to the FAISS index directory
    index_path = "DataIndex"

    # Initialize the RAG system
    rag_system = create_rag_system(index_path)

    # Get user input and generate the answer
    while True:
        user_question = input("Ask your question (or type 'exit' to quit): ")
        if user_question.lower() == "exit":
            print("Exiting the RAG system.")
            break
        answer = get_answer(user_question, rag_system)
        print(f"Answer: {answer}")
