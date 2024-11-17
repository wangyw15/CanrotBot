from pydantic import BaseModel, Field


class RssConfig(BaseModel):
    interval: int = Field(default=60 * 30, alias="canrot_rss_update_interval")
