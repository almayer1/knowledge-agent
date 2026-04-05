from pydantic_settings import BaseSettings
from pydantic import ValidationInfo, field_validator
from pathlib import Path


class Settings(BaseSettings):
    # LLM
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "ollama"
    llm_model: str = "llama3.2"

    # API
    api_url: str = "http://localhost:8000"

    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5

    @field_validator("chunk_overlap")
    def overlap_must_be_less_than_size(cls, overlap, info: ValidationInfo):
        chunk_size = info.data.get("chunk_size")
        if chunk_size and overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        return overlap

    # OCR
    ocr_dpi: int = 300
    ocr_min_confidence: float = 0.65

    # Paths
    data_dir: Path = Path(__file__).parent / "data" 

    model_config = {"env_file": ".env"}

