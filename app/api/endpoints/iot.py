from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models import FieldWaterLevel as FieldWaterLevelModel, FieldStats as FieldStatsModel
from app.schemas.iot_data import FieldWaterLevel, FieldStats

router = APIRouter()


@router.post(
    "/water-level/",
    response_model=FieldWaterLevel,
    status_code=status.HTTP_201_CREATED,
    description="Create a new water level entry",
)
async def create_water_level(
    data: FieldWaterLevel, session: AsyncSession = Depends(deps.get_session)
) -> FieldWaterLevel:
    db_entry = FieldWaterLevelModel(
        id=data.id,
        device_id=data.device_id,
        water_level=data.water_level,
        create_time=data.create_time or datetime.utcnow(),
    )
    session.add(db_entry)
    await session.commit()
    await session.refresh(db_entry)
    return db_entry


@router.get(
    "/water-level/{device_id}", response_model=FieldWaterLevel, description="Get a water level entry by device ID"
)
async def get_water_level(device_id: str, session: AsyncSession = Depends(deps.get_session)) -> FieldWaterLevel:
    result = await session.execute(select(FieldWaterLevelModel).where(FieldWaterLevelModel.device_id == device_id))
    db_entry = result.scalar_one_or_none()
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Water level entry not found")
    return db_entry


@router.get(
    "/water-level/",
    response_model=List[FieldWaterLevel],
    description="Get all water level entries",
)
async def get_all_water_levels(session: AsyncSession = Depends(deps.get_session)) -> List[FieldWaterLevel]:
    result = await session.execute(select(FieldWaterLevelModel))
    db_entries = result.scalars().all()
    return db_entries


@router.get(
    "/water-level/recent/{days}",
    response_model=List[FieldWaterLevel],
    description="Get water level entries from the past 'days' number of days",
)
async def get_recent_water_levels(
    days: int, session: AsyncSession = Depends(deps.get_session)
) -> List[FieldWaterLevel]:
    if days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The number of days must be greater than 0.",
        )
    start_time = datetime.utcnow() - timedelta(days=days)
    result = await session.execute(select(FieldWaterLevelModel).where(FieldWaterLevelModel.create_time >= start_time))
    db_entries = result.scalars().all()
    return db_entries


@router.post(
    "/field-stats/",
    response_model=FieldStats,
    status_code=status.HTTP_201_CREATED,
    description="Create a new field stats entry",
)
async def create_field_stats(data: FieldStats, session: AsyncSession = Depends(deps.get_session)) -> FieldStats:
    db_entry = FieldStatsModel(
        id=data.id,
        device_id=data.device_id,
        soil_moisture=data.soil_moisture,
        soil_status=data.soil_status,
        temperature=data.temperature,
        create_time=data.create_time or datetime.utcnow(),
    )
    session.add(db_entry)
    await session.commit()
    await session.refresh(db_entry)
    return db_entry


@router.get(
    "/field-stats/{device_id}",
    response_model=FieldStats,
    description="Get a field stats entry by device ID",
)
async def get_field_stats(device_id: str, session: AsyncSession = Depends(deps.get_session)) -> FieldStats:
    result = await session.execute(select(FieldStatsModel).where(FieldStatsModel.device_id == device_id))
    db_entry = result.scalar_one_or_none()
    if not db_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Field stats entry not found")
    return db_entry


@router.get(
    "/field-stats/",
    response_model=List[FieldStats],
    description="Get all field stats entries",
)
async def get_all_field_stats(session: AsyncSession = Depends(deps.get_session)) -> List[FieldStats]:
    result = await session.execute(select(FieldStatsModel))
    db_entries = result.scalars().all()
    return db_entries


@router.get(
    "/field-stats/recent/{days}",
    response_model=List[FieldStats],
    description="Get field stats entries from the past 'days' number of days",
)
async def get_recent_field_stats(days: int, session: AsyncSession = Depends(deps.get_session)) -> List[FieldStats]:
    if days <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The number of days must be greater than 0.",
        )
    start_time = datetime.utcnow() - timedelta(days=days)
    result = await session.execute(select(FieldStatsModel).where(FieldStatsModel.create_time >= start_time))
    db_entries = result.scalars().all()
    return db_entries
