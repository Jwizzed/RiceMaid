from datetime import datetime
from pydantic import BaseModel


class FieldWaterLevel(BaseModel):
    id: int
    device_id: str
    water_level: int
    create_time: datetime


class FieldStats(BaseModel):
    id: int
    device_id: str
    soil_moisture: int
    soil_status: str
    temperature: float
    create_time: datetime
