from pydantic import BaseModel, Field


class OllamaConfig(BaseModel):
    host: str = Field(default="http://localhost:11434", alias="canrot_ollama_host")
    model: str = Field(default="llama3.1:latest", alias="canrot_ollama_model")
