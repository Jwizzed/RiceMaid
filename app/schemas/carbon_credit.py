from pydantic import BaseModel


class CarbonCreditRequest(BaseModel):
    area: float
    harvest_age: int


class CarbonCreditResponse(BaseModel):
    methane_emission: float
    carbon_credit: float
