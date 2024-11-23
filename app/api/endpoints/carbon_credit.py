from fastapi import APIRouter, HTTPException
from app.schemas.carbon_credit import CarbonCreditResponse, CarbonCreditRequest

router = APIRouter()

METHANE_EMISSION_COEFF = 0.1952
GWP_METHANE = 25


def estimate_methane_emission(
    coefficient_methane_emission: float, area_rice_field: float, harvest_age: int, gwp_methane: float
) -> float:
    """
    Estimate the methane emission from rice fields.

    Parameters:
    - coefficient_methane_emission (float): Coefficient of methane emission in season (s) for example unit (i)
    - area_rice_field (float): Area of rice field in season (s) for example unit (i) (in hectares or appropriate units)
    - harvest_age (int): Harvest age of season (s) in days
    - gwp_methane (float): Global Warming Potential of methane (GWP)

    Returns:
    - float: Estimated methane emission (in kg CO2 equivalent, or appropriate units)
    """
    methane_emission = coefficient_methane_emission * area_rice_field * harvest_age * 10**-3 * gwp_methane
    return methane_emission


@router.post(
    "/",
    response_model=CarbonCreditResponse,
    description="Calculate methane emission and estimate carbon credit",
)
async def calculate_carbon_credit(data: CarbonCreditRequest) -> CarbonCreditResponse:
    if data.area <= 0:
        raise HTTPException(status_code=400, detail="Area must be greater than 0")
    if data.harvest_age <= 0:
        raise HTTPException(status_code=400, detail="Harvest age must be greater than 0")

    methane_emission = estimate_methane_emission(
        coefficient_methane_emission=METHANE_EMISSION_COEFF,
        area_rice_field=data.area,
        harvest_age=data.harvest_age,
        gwp_methane=GWP_METHANE,
    )

    carbon_credit = methane_emission / 1000

    return CarbonCreditResponse(methane_emission=methane_emission, carbon_credit=carbon_credit)
