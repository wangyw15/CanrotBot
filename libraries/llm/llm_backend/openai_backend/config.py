from pydantic import BaseModel, Field


class OpenAIConfig(BaseModel):
    base_url: str = Field(default="https://api.openai.com/v1", alias="openai_base_url")
    api_key: str = Field(default="", alias="openai_api_key")
    model: str = Field(default="gpt-3.5-turbo", alias="canrot_openai_model")
