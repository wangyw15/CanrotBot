from pydantic import BaseModel, Field
from canrotbot.essentials.libraries.config import global_config


class DatabaseConfig(BaseModel):
    connection_string: str = Field(
        default=f"sqlite:///{global_config.user_data_path}/data.db?check_same_thread=False",
        alias="canrot_database",
    )
