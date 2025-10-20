from pydantic import BaseModel
from typing import List


class Vehicle(BaseModel):
    id: int
    name: str
    brand: str
    model: str
    year: int
    color: str
    price: float
    fuel_type: str
    mileage_km: int
    transmission: str
    image_url: str
    description: str
    rating: float


class VehiclesResponse(BaseModel):
    response: List[Vehicle]
