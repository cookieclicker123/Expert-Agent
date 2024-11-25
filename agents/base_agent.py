from abc import ABC, abstractmethod
from langchain_ollama import OllamaLLM
from langchain_groq import ChatGroq
from langchain.schema.messages import HumanMessage
from utils.config import Config
import sys

class BaseAgent(ABC):
    def __init__(self, name: str, callbacks=None):
        self.name = name
        self.callbacks = callbacks or []
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self):
        if Config.model_config.provider == "groq":
            return ChatGroq(
                api_key=Config.model_config.groq_api_key,
                model_name=Config.model_config.groq_model_name,
                callbacks=self.callbacks,
                streaming=True
            )
        elif Config.model_config.provider == "ollama":
            return OllamaLLM(
                model=Config.model_config.model_name,
                callbacks=self.callbacks
            )
        else:
            raise ValueError(f"Unknown provider: {Config.model_config.provider}")
        
    def _invoke_llm(self, prompt: str) -> str:
        """Invoke LLM with consistent callbacks"""
        try:
            if Config.model_config.provider == "groq":
                response = self.llm.invoke(
                    [HumanMessage(content=prompt)]
                )
                return response.content
            else:
                return self.llm.invoke(prompt)
            
        except Exception as e:
            print(f"\nError invoking LLM: {str(e)}")
            return f"Error: {str(e)}"
    
    @abstractmethod
    def process(self, query: str) -> str:
        pass