from pydantic import BaseModel, Field


class CalculatorConfig(BaseModel):
    qalculate_bin: str = Field(default="qalc", alias="qalculate_bin")
