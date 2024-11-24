from abc import ABC, abstractmethod
from langchain_ollama import OllamaLLM
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler as StreamingHandler
from utils.config import Config
import sys

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.llm = OllamaLLM(
            model=Config.model_config.model_name,
            callbacks=[StreamingHandler()]
        )
        
    def _invoke_llm(self, prompt: str) -> str:
        """Invoke LLM with prompt"""
        return self.llm.invoke(prompt)
        
    def _stream_output(self, text: str):
        sys.stdout.write(text)
        sys.stdout.flush()
    
    @abstractmethod
    def process(self, query: str) -> str:
        pass