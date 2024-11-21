from dataclasses import dataclass

@dataclass
class ModelConfig:
    model_name: str = "llama3.2"
    temperature: float = 0.7
    max_tokens: int = 3000

@dataclass
class APIConfig:
    serper_api_key: str = "your-serper-key"
    yahoo_finance_api_key: str = "your-yahoo-key"

@dataclass
class PathConfig:
    documents_dir: str = "./data/documents"
    processed_dir: str = "./data/processed"
    index_dir: str = "./data/indexes"

class Config:
    model_config = ModelConfig()
    api_config = APIConfig()
    path_config = PathConfig() 