from abc import ABC, abstractmethod
from langchain_ollama import OllamaLLM
from utils.callbacks import StreamingHandler
from utils.config import Config
import sys

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.streaming_handler = StreamingHandler()
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self) -> OllamaLLM:
        """Initialize LLM with streaming callback"""
        return OllamaLLM(
            model=Config.model_config.model_name,
            temperature=Config.model_config.temperature,
            streaming=True,
            callbacks=[self.streaming_handler]
        )
    
    def _stream_output(self, text: str, end: str = ""):
        """Stream output to console"""
        sys.stdout.write(text)
        if end:
            sys.stdout.write(end)
        sys.stdout.flush()
    
    def _invoke_llm(self, prompt: str) -> str:
        """Invoke LLM with streaming"""
        self.streaming_handler.text = ""  # Reset stored text
        response = self.llm.invoke(prompt)
        return self.streaming_handler.text  # Return accumulated text
    
    @abstractmethod
    def process(self, query: str) -> str:
        """Process a query and return response"""
        pass 