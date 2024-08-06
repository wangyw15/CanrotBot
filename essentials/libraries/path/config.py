from pydantic import BaseModel, Field


class FileConfig(BaseModel):
    user_data_path: str = Field(default="./canrot_data", alias="canrot_user_data_path")
