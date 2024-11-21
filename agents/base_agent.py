from abc import ABC, abstractmethod
from langchain_ollama import OllamaLLM
from utils.config import Config

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self) -> OllamaLLM:
        """Initialize LLM with standard configuration"""
        return OllamaLLM(
            model=Config.model_config.model_name,
            temperature=Config.model_config.temperature
        )
    
    @abstractmethod
    def process(self, query: str) -> str:
        """Process a query and return response"""
        pass 