from pydantic import BaseModel, Field


class YinglishConfig(BaseModel):
    yinglish_rate: float = Field(default=1.0)
