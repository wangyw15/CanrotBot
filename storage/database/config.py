from pydantic import BaseModel, Field
from ..config import global_config


class DatabaseConfig(BaseModel):
    connection_string: str = Field(
        default=f"sqlite:///{global_config.data_path}/data.db?check_same_thread=False",
        alias="canrot_database",
    )
