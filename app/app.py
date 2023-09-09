# app.py
from fastapi import FastAPI
from pydantic import BaseModel, Field

import jumbo_kassabon

app = FastAPI()


def _find_next_id():
    return max(country.country_id for country in countries) + 1


class Country(BaseModel):
    country_id: int = Field(default_factory=_find_next_id, alias="id")
    name: str
    capital: str
    area: int


countries = [
    Country(id=1, name="Thailand", capital="Bangkok", area=513120),
    Country(id=2, name="Australia", capital="Canberra", area=7617930),
    Country(id=3, name="Egypt", capital="Cairo", area=1010408),
]


@app.get("/jumbo/kassabon/latest")
async def get_jumbo_kassabon():
    item_list = jumbo_kassabon.get_bill_items()
    return item_list

@app.get("/jumbo/kassabon/date/{date}")
async def get_jumbo_kassabon_date():
    return "Not implemented yet"

@app.get("/ping")
async def ping():
    return "ping"


@app.get("/countries")
async def get_countries():
    return countries


@app.post("/countries", status_code=201)
async def add_country(country: Country):
    countries.append(country)
    return country
