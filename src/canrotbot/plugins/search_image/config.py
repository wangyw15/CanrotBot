from pydantic import BaseModel, Field


class SearchImageConfig(BaseModel):
    saucenao_api_key: str = Field(default="")
    search_result_count: int = Field(
        default=1, alias="canrot_image_search_result_count"
    )
