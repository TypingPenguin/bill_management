# app.py
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import jumbo_kassabon
import yaml
import os
import requests
import datetime

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
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],  # You can specify allowed headers or use ["*"] to allow all headers
)

@app.get("/jumbo/kassabon/latest")
async def get_jumbo_kassabon():
    item_list = jumbo_kassabon.get_bill_items()
    return item_list


@app.get("/ping")
async def ping():
    return "ping"

@app.get("/version")
async def ping():
    return "v0.1"

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
