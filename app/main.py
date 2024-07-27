# app.py
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import jumbo_kassabon, jumbo_api
import yaml
import os
import requests
import datetime
from loguru import logger
import sys


app = FastAPI()

# Activate if we need variables
# with open("myconfig.yaml", "r") as file:
#     config = yaml.load(file, Loader=yaml.FullLoader)
# for key, value in config.get("data", {}).items():
#     os.environ[key] = value

# Configure CORS settings
origins = [
    "http://localhost",  # Add the origins (domains) you want to allow here
    "http://localhost:3000",  # Example: Allow requests from a React app running locally
    "http://192.168.1.68",
    "http://192.168.1.68:9000",
    "http://192.168.1.22",
    "http://192.168.1.22:9000",
    "https://bill_website.typingpenguin.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],  # You can specify allowed headers or use ["*"] to allow all headers
)

logger.info("Creating jumbo object")
jumbo = jumbo_api.jumbo()

@app.get("/jumbo/kassabon/latest")
async def get_jumbo_kassabon():
    logger.info("Getting request for latest kassabon")
    bill_list = jumbo.get_list_bonnen()
    latest_bill = bill_list[0]
    latest_bill_id = latest_bill['transactionId']
    get_bill = jumbo.get_bill(latest_bill_id)
    return get_bill

@app.get("/jumbo/kassabon/{bill_id}")
async def get_jumbo_kassabon(bill_id: str):
    logger.info("Getting request for kassabon with id: " + bill_id)
    get_bill = jumbo.get_bill(bill_id)
    return get_bill

@app.get("/jumbo/kassabonnen")
async def get_jumbo_kassabonnen():
    logger.info("Getting request for all kassabonnen")
    bill_list = jumbo.get_list_bonnen()
    return bill_list

@app.get("/jumbo/kassabon/date/{date}")

@app.get("/ping")
async def ping():
    logger.info("Ping request")
    return "ping"

@app.get("/version")
async def version():
    return "v0.22"

@app.post("/post/splitwise/multiplier")
async def post_splitwise_multiplier(items : List[jumbo_kassabon.Item_multiplier]):

    data, headers, url = await jumbo_kassabon.prepare_data_splitwise(items)

    response = requests.post(url, json=data, headers=headers)

    print(response.status_code)

    # Check the response status code
    if response.status_code == 200:  # Successful request (HTTP status code 200 OK)
        response_data = {
            "status": "success",
            "message": "Request was successful!",
            "data": response.json(),
        }
    else:
        response_data = {
            "status": "error",
            "message": f"Request failed with status code {response.status_code}",
        }
        # Handle the error accordingly
        if response.status_code == 400:
            response_data["error_message"] = "Bad Request: Check your request data."
        elif response.status_code == 401:
            response_data["error_message"] = "Unauthorized: Check your authentication."
        else:
            response_data["error_message"] = "Other error occurred."

    return response_data
