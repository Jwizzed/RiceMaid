from datetime import datetime

import requests
from fastapi import APIRouter, HTTPException, Query

from app.core.config import get_settings
from app.schemas import WaterResourcesResponse

router = APIRouter()
settings = get_settings()


@router.get(
    "/twsapi/v1.0/SmallsizedWaterResources",
    response_model=WaterResourcesResponse,
    summary="Fetch small-sized water resources data",
    description="Retrieve water resources information based on various parameters.",
)
async def get_small_water_resources(
    interval: str = Query(..., description="Data interval", regex="^(P-Daily)$"),
    latest: bool = Query(..., description="Fetch latest data or a specific range"),
    startDatetime: datetime | None = Query(None, description="Start date (required if latest is false)"),
    endDatetime: datetime | None = Query(None, description="End date (required if latest is false)"),
    provinceCode: str | None = Query(None, description="Province code filter"),
    amphoeCode: str | None = Query(None, description="Amphoe code filter"),
    tambonCode: str | None = Query(None, description="Tambon code filter"),
):
    # Validate dependencies: start and end datetime must be provided if latest is false
    if not latest and (not startDatetime or not endDatetime):
        raise HTTPException(
            status_code=400, detail="startDatetime and endDatetime are required when 'latest' is false."
        )

    # Construct query parameters
    query_params = {
        "interval": interval,
        "latest": latest,
        "startDatetime": startDatetime.isoformat() if startDatetime else None,
        "endDatetime": endDatetime.isoformat() if endDatetime else None,
        "provinceCode": provinceCode,
        "amphoeCode": amphoeCode,
        "tambonCode": tambonCode,
    }

    try:
        # Make the external API call
        response = requests.get(
            f"{settings.external_api_base_url}/twsapi/v1.0/SmallsizedWaterResources",
            params=query_params,
            headers={"Authorization": f"Bearer {settings.api_token}"},
        )
        response.raise_for_status()  # Raise exception for HTTP errors
    except requests.HTTPError as e:
        raise HTTPException(status_code=response.status_code, detail=f"Error fetching data: {e.response.text}")

    return response.json()
