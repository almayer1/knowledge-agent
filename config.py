from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # LLM settings
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "ollama"
    llm_model: str = "llama3.2"

    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5

    # OCR
    ocr_dpi: int = 300
    ocr_min_confidence: float = 0.65

    # Paths
    data_dir: Path = Path(__file__).parent / "data" 

    model_config = {"env_file": ".env"}

