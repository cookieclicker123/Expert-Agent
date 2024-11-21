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