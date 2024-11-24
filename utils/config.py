from dataclasses import dataclass
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class ModelConfig:
    model_name: str = "llama3.2"
    temperature: float = 0.7
    max_tokens: int = 3000
    provider: str = "ollama"

    groq_api_key: str = os.getenv("GROQ_API_KEY")
    groq_model_name: str = "llama-3.2-90b-text-preview"

    local_display_name: str = "Local (Ollama LLaMA 3.2)"
    groq_display_name: str = "Groq (LLaMA 3.2 90B)"

@dataclass
class APIConfig:
    serper_api_key: str = os.getenv("SERPER_API_KEY")
    alpha_vantage_key: str = os.getenv("ALPHA_VANTAGE_API_KEY")

@dataclass
class PathConfig:
    documents_dir: str = "./data/documents"
    processed_dir: str = "./data/processed"
    index_dir: str = "./data/indexes"

class Config:
    model_config = ModelConfig()
    api_config = APIConfig()
    path_config = PathConfig() 