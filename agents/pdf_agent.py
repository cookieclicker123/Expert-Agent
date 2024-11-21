from agents.base_agent import BaseAgent
from tools.pdf_tools import PDFTool
from utils.prompts import PDF_AGENT_PROMPT
from langchain.chains import RetrievalQA
import json

class PDFAgent(BaseAgent):
    def __init__(self):
        super().__init__("pdf")
        self.pdf_tool = PDFTool()
        self.prompt = PDF_AGENT_PROMPT
        self.qa_chain = self._initialize_qa_chain()
        
    def _initialize_qa_chain(self):
        """Initialize the QA chain using the existing RAG setup"""
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.pdf_tool.rag_system.vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": 12,
                    "fetch_k": 20,
                    "lambda_mult": 0.5
                }
            ),
            chain_type_kwargs={"prompt": self.prompt}
        )
        
    def process(self, query: str) -> str:
        """Process document-based queries"""
        try:
            # Use the QA chain directly
            response = self.qa_chain.invoke({"query": query})
            return response['result']  # Return plain text response
        except Exception as e:
            return self._format_error_response(str(e))
            
    def _format_error_response(self, error_msg: str) -> str:
        return json.dumps({
            "error": {
                "message": error_msg,
                "agent": self.name
            }
        }, indent=2) 