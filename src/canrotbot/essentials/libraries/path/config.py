from pydantic import BaseModel, Field


class FileConfig(BaseModel):
    asset_path: str = Field(default="./assets", alias="canrot_asset_path")
    user_data_path: str = Field(default="./canrot_data", alias="canrot_user_data_path")
