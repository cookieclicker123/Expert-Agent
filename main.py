from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_ollama import OllamaLLM
from langchain.callbacks.base import BaseCallbackHandler
import sys

# Custom streaming callback handler
class CustomStreamingHandler(BaseCallbackHandler):
    def __init__(self):
        self.text = ""
        
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Run on new LLM token. Only available when streaming is enabled."""
        sys.stdout.write(token)
        sys.stdout.flush()
        self.text += token


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

    # Initialize Ollama without a streaming handler
    llm = OllamaLLM(model=model_name)

    # Create a more detailed prompt template
    prompt_template = """
    You are an expert financial analyst and advisor with exceptional ability to synthesize information from multiple sources and draw sophisticated conclusions. Your strength lies in combining factual evidence with expert analysis.

    If context is provided, you have access to excerpts from multiple financial documents and sources:
    {context}

    Question: {question}

    Follow these analytical principles:

    1. INFORMATION SYNTHESIS
    - Identify key data points across all provided documents
    - Look for patterns, correlations, or contradictions between different sources
    - Understand the temporal relationship between different pieces of information
    - Recognize when different sources are describing the same phenomenon from different angles

    2. ANALYTICAL FOUNDATION
    - Ground your initial analysis in concrete facts from the sources
    - Note where different sources reinforce or challenge each other
    - Identify gaps or limitations in the available information
    - Consider the context and timeframe of each piece of information

    3. REASONED EXPANSION
    - Build logical bridges between different pieces of information
    - Draw conclusions that extend beyond but remain anchored to the evidence
    - Use your expertise to interpret implications
    - Develop insights that wouldn't be apparent from any single source alone

    4. HOLISTIC INTEGRATION
    - Combine document-based evidence with your market expertise
    - Consider how different pieces of information interact with each other
    - Identify broader patterns or trends suggested by the combined information
    - Develop a comprehensive view that's greater than the sum of its parts

    Remember:
    - Not every question requires external context - use your judgment
    - When using sources, cite them specifically but don't be constrained by them
    - Your role is to provide insight, not just information
    - Be explicit about your reasoning process and any assumptions
    - Distinguish between direct evidence and reasoned extrapolation

    Structure your response to best serve the analysis, but always make clear:
    - What information you're drawing from
    - How different sources connect
    - Your reasoning process
    - The confidence level of your conclusions
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
    streaming_handler = CustomStreamingHandler()
    
    try:
        response = qa_chain.invoke(
            {"query": question},
            {"callbacks": [streaming_handler]}
        )
        print()  # Add newline after response
        return streaming_handler.text
        
    except Exception as e:
        print(f"\nError during streaming: {e}")
        return ""


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
        print(f"\n[FINAL]{answer}")
