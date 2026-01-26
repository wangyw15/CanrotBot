from typing import Any

from pydantic import BaseModel, Field, SecretStr


class OpenAIConfig(BaseModel):
    base_url: str = Field(default="https://api.openai.com/v1", alias="openai_base_url")
    api_key: SecretStr = Field(default=SecretStr(""), alias="openai_api_key")
    model: str = Field(default="gpt-3.5-turbo", alias="canrot_openai_model")
    extra_body: dict[str, Any] = Field(default={}, alias="canrot_openai_extra_body")
