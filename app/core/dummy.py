import random
from datetime import datetime, timedelta
from typing import List

from pydantic import BaseModel
from app.models import FieldStats, FieldWaterLevel


class WeatherData(BaseModel):
    date: datetime
    temperature_min: float
    temperature_max: float
    humidity: int
    wind_speed: float
    condition: str


def generate_weather_mock_data(start_date: datetime, days: int) -> List[WeatherData]:
    weather_conditions = ["Sunny", "Cloudy", "Rainy", "Stormy", "Windy", "Snowy"]

    return [
        WeatherData(
            date=start_date + timedelta(days=i),
            temperature_min=round(random.uniform(5.0, 15.0), 1),
            temperature_max=round(random.uniform(16.0, 30.0), 1),
            humidity=random.randint(40, 90),
            wind_speed=round(random.uniform(5.0, 20.0), 1),
            condition=random.choice(weather_conditions),
        )
        for i in range(days)
    ]


def generate_dummy_field_water_levels(num_records: int) -> List[FieldWaterLevel]:
    return [
        FieldWaterLevel(
            id=i + 1,
            device_id=f"Device_{random.randint(1, 10)}",
            water_level=random.randint(0, 15),
            create_time=datetime.now() - timedelta(minutes=random.randint(0, 1440)),
        )
        for i in range(num_records)
    ]


def generate_dummy_field_stats(num_records: int) -> List[FieldStats]:
    soil_status_options = ["Dry", "Moist", "Wet"]
    return [
        FieldStats(
            id=i + 1,
            device_id=f"Device_{random.randint(1, 10)}",
            soil_moisture=random.randint(0, 100),
            soil_status=random.choice(soil_status_options),
            temperature=round(random.uniform(15.0, 35.0), 2),
            create_time=datetime.now() - timedelta(minutes=random.randint(0, 1440)),
        )
        for i in range(num_records)
    ]


if __name__ == "__main__":
    water_levels = generate_dummy_field_water_levels(5)
    field_stats = generate_dummy_field_stats(5)

    print("Field Water Levels:")
    for record in water_levels:
        print(record.water_level)

    print("\nField Stats:")
    for record in field_stats:
        print(record.soil_moisture)

    start_date = datetime.now()
    weather_data = generate_weather_mock_data(start_date, 7)

    print("7-Day Weather Mock Data:")
    for day in weather_data:
        print(day.date, day.temperature_min, day.temperature_max, day.humidity, day.wind_speed, day.condition)
