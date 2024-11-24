from abc import ABC, abstractmethod
from langchain_ollama import OllamaLLM
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler as StreamingHandler
from utils.config import Config
import sys

class BaseAgent(ABC):
    def __init__(self, name: str, silent: bool = False):
        self.name = name
        self.silent = silent
        self.stream_handler = StreamingHandler()
        self.llm = OllamaLLM(
            model=Config.model_config.model_name,
            callbacks=[]
        )
        
    def _invoke_llm(self, prompt: str, stream: bool = False) -> str:
        """Invoke LLM with optional streaming"""
        if stream:
            self.llm.callbacks = [self.stream_handler]
        else:
            self.llm.callbacks = []
        return self.llm.invoke(prompt)
        
    def _stream_output(self, text: str):
        if not self.silent:
            sys.stdout.write(text)
            sys.stdout.flush()
    
    @abstractmethod
    def process(self, query: str) -> str:
        pass