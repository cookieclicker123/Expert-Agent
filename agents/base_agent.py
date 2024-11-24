from abc import ABC, abstractmethod
from langchain_ollama import OllamaLLM
from langchain_groq import ChatGroq
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler as StreamingHandler
from utils.config import Config
import sys

class BaseAgent(ABC):
    def __init__(self, name: str, silent: bool = False):
        self.name = name
        self.silent = silent
        self.stream_handler = StreamingHandler()
        
        # Initialize LLM based on provider
        if Config.model_config.provider == "ollama":
            self.llm = OllamaLLM(
                model=Config.model_config.model_name,
                callbacks=[]
            )
        elif Config.model_config.provider == "groq":
            self.llm = ChatGroq(
                api_key=Config.model_config.groq_api_key,
                model_name=Config.model_config.groq_model_name,
                callbacks=[],
                temperature=Config.model_config.temperature,
                max_tokens=Config.model_config.max_tokens
            )
        else:
            raise ValueError(f"Unknown provider: {Config.model_config.provider}")
        
    def _invoke_llm(self, prompt: str, stream: bool = False) -> str:
        """Invoke LLM with optional streaming"""
        try:
            if stream:
                self.llm.callbacks = [self.stream_handler]
            else:
                self.llm.callbacks = []
            
            response = self.llm.invoke(prompt)
            
            if Config.model_config.provider == "groq":
                # Ensure consistent formatting for Groq responses
                if isinstance(response, str):
                    return response
                else:
                    return response.content  # Handle ChatGroq response format
                
            return response
            
        except Exception as e:
            print(f"\nError invoking LLM: {str(e)}")
            return f"Error: {str(e)}"
        
    def _stream_output(self, text: str):
        if not self.silent:
            sys.stdout.write(text)
            sys.stdout.flush()
    
    @abstractmethod
    def process(self, query: str) -> str:
        pass