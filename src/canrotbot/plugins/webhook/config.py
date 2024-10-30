from pydantic import BaseModel, Field


class WebhookConfig(BaseModel):
    domain: str = Field(default="", alias="canrot_domain")
