from pydantic import BaseModel, Field


class OllamaConfig(BaseModel):
    ollama_host: str = Field(
        default="http://localhost:11434", alias="canrot_ollama_host"
    )
    ollama_model: str = Field(default="llama3.1:latest", alias="canrot_ollama_model")
