import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import os
from selenium.webdriver.common.by import By  # Import the By class
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import re
from pydantic import BaseModel
import datetime
from loguru import logger
import time

import dotenv

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

class Item_multiplier(BaseModel):
    name: str | None = None
    price: float | None = None
    multiplier: float

class Item:
    def __init__(self, name, price):
        self.name = name
        self.price = price

    def __str__(self):
        return f"{self.name}({self.price})"



def get_bill_items():

    print("-------------Setting up driver-------------")
    driver = __set_up_driver()
    logger.remove()
    # time.sleep(5)
    print("Source page:")
    print(driver.page_source)
    print("End of source page")

    try:
        print("-------------Setting up table_text-------------")
        table_text = __goto_bill(driver)

        # print(f"Table text:\n{table_text}")
        print("-------------parsing text-------------")
        item_list = __parse_bill(table_text)

        __debug_html_page(driver)

    # Close the WebDriver when done
    except Exception as e:
        print(f"An error occured: {e}")
        return ["An error has occured" + e.__str__()]
    finally:
        driver.quit()

    return item_list

def __set_up_driver():
    # user_agent = "Chrome/58.0.3029.110"
    user_agent = "Chrome/91.0.4472.124"
    # chrome_driver_path = os.environ['CHROMEDRIVER_PATH']
    # print(chrome_driver_path)
    # os.environ['webdriver.chrome.driver'] = "C:\\Users\\Admin\\PycharmProjects\\bill_management\\chrome-win64\\chromedriver.exe"
    # Specify Chrome options
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')  # Optional: Run Chrome in headless mode
    # chrome_options.add_argument('--disable-gpu')  # Optional: Disable GPU acceleration
    chrome_options.add_argument(f'user-agent={user_agent}')
    chrome_options.add_argument("--no-sandbox")  # Disable sandbox
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    # chrome_options.binary_location = chrome_driver_path
    # Set up the Selenium WebDriver (you'll need to download the appropriate driver for your browser)
    driver = webdriver.Chrome(options=chrome_options)
    # Navigate to the login page
    driver.get('https://loyalty-app.jumbo.com/home')
    return driver


def __goto_bill(driver):
    username = os.environ['MY_USER']
    password = os.environ['MY_PASS']


    # ---Press on first login button
    print("-------------first login button-------------")
    logger.info("-------------first login button-------------")
    time.sleep(4)
    # WebDriverWait(driver, 70).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div/div/div/div/main/div/div/div/div[2]/button[2]')))
    login_button = driver.find_element(By.XPATH, '//*[@id="__nuxt"]/div/div/div[1]/main/div/div[1]/div/div[2]/button')
    login_button.click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/main/section/div/div/div/form/div[3]/button')))
    # ---Login with account
    print("-------------login with account-------------")
    time.sleep(5)

    logger.info("trying to login")
    username_field = driver.find_element(By.XPATH, '//*[@id="username"]')
    password_field = driver.find_element(By.XPATH, '//*[@id="password"]')
    username_field.send_keys(username)
    password_field.send_keys(password)
    time.sleep(5)
    login_button = driver.find_element(By.XPATH, '/html/body/main/section/div/div/div/form/div[2]/button')
    login_button.click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/div[1]/main/div/div[1]/div/div[1]/button')))
    time.sleep(4)
    logger.info("Succesfully logged in")
    # ---Press "Meer"
    print("-------------Meer-------------")
    meer_button = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/nav/ul/li[5]/a/button')
    meer_button.click()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div/div/div[1]/main/div[2]/ul/li[1]/a')))
    # ---Press "Kassabonnen"
    print("-------------Press 'kassabonnen'-------------")
    logger.info("trying to reach kassabonnen")
    kassabonen = driver.find_element(By.XPATH, '/html/body/div[2]/div/div/div[1]/main/div[2]/ul/li[1]/a')
    kassabonen.click()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located(
        (By.XPATH, '/html/body/div[2]/div/div/div[1]/main/div[2]/ul/div[1]/div[1]/a/div/div/p')))
    # print("trying to reach a specific kassabon")
    # ---Press last Kassabon
    latest_kassabon = driver.find_element(By.XPATH,
                                          '/html/body/div[2]/div/div/div[1]/main/div[2]/ul/div[1]/div[1]/a/div/div/p')
    ##Test bon
    # latest_kassabon = driver.find_element(By.XPATH, '//html/body/div[2]/div/div/div[1]/main/div[2]/ul/div[3]/div[1]/a/div/div/p')

    latest_kassabon.click()
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Producten')]")))
    # ---Get elements
    parent_element = driver.find_element(By.XPATH, "//*[contains(text(), 'Producten')]")
    table_element = driver.find_element(By.CLASS_NAME, 'loyal-digital-receipt-details-table')
    table_text = table_element.text
    return table_text


def __debug_html_page(driver):
    print("-----------------MAINPAGE-----------------")
    with open('../index.html', 'w', encoding='utf-8') as f:
        f.write(driver.page_source)


def __parse_bill(table_text):
    lines = table_text.split('\n')
    # Initialize lists to store names and prices
    item_names = []
    item_prices = []
    # Define a regular expression pattern to match the name and price
    pattern = r'^(.*?)\s+([\d,]+)$'
    # Initialize a variable to hold a line with no price
    line_with_no_price = None
    # Loop through each line and extract the name and price
    for line in lines:
        match = re.match(pattern, line)
        if match:
            # If there was a line with no price, append it to the current name
            if line_with_no_price:
                name = line_with_no_price + " " + match.group(1)
                price = match.group(2).replace(',', '.')  # Replace comma with dot for proper float conversion
                item_names.append(name.strip())
                item_prices.append(float(price))
                line_with_no_price = None
            else:
                name = match.group(1)
                price = match.group(2).replace(',', '.')  # Replace comma with dot for proper float conversion
                item_names.append(name.strip())
                item_prices.append(float(price))
        else:
            # If the line doesn't match the pattern, consider it as part of the name
            if line_with_no_price is None:
                line_with_no_price = line.strip()
            else:
                line_with_no_price += " " + line.strip()


    item_list = []
    # Print the parsed names and prices
    for name, price in zip(item_names, item_prices):
        # print(f"Name: {name}, Price: {price}")
        item_list.append(Item(name,price))
    return item_list




async def prepare_data_splitwise(items):
    cost = 0
    details = ""
    multiplier = ""
    for item in items:
        extra_cost = item.price * item.multiplier
        cost += extra_cost
        if item.multiplier != 0:
            match item.multiplier:
                case 0.34:
                    multiplier = "1/3"
                case 0.5:
                    multiplier = "1/2"
                case 0.67:
                    multiplier = "2/3"
                case 1:
                    multiplier = "1"
                case _:
                    multiplier = "Something went wrong..."

            details += f"{item.name}, {item.price} EUR. Multiplier: {multiplier}, gerekende kost: {extra_cost}.\n"
    details += f"Totaal the betalen door Jannick: {cost}."
    current_date_normal = datetime.datetime.now().strftime("%Y-%m-%d")
    current_date = datetime.datetime.utcnow().isoformat() + "Z"
    auth_token = os.environ["BEARER_SPLITWISE"]
    group_id = os.environ["GROUP_ID"]
    category_id = os.environ["CATEGORY_ID"]
    headers = {'Authorization': f'Bearer {auth_token}'}

    data = {
        "cost": str(cost * 2),
        "description": f"Jumbo {current_date_normal}",
        "details": details,
        "date": current_date,
        "repeat_interval": "never",
        "currency_code": "EUR",
        "category_id": category_id,
        "group_id": group_id,
        "split_equally": True
    }

    url = 'https://secure.splitwise.com/api/v3.0/create_expense'

    return data, headers, url