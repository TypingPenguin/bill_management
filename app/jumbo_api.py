from loguru import logger
import os

import requests, jwt, time
import dotenv
import json

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

class product():
    def __init__(self, name, price):
        self.name = name
        self.price = price

class jumbo():
    def __init__(self):
        self.token_endpoint = os.environ['TOKEN_ENDPOINT']
        self.client_id = os.environ['CLIENT_ID']
        self.refresh_token = os.environ['REFRESH_TOKEN']
        self.access_token = None

    def __create_headers(self):
        self.__check_token_validity_and_update()
        return {
            'Authorization': f'Bearer {self.access_token}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Referer': 'https://loyalty-app.jumbo.com/profile/digital-receipts',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=4'
        }


    def get_bill(self, bill_id):
        list = []
        logger.info("Starting get_bill")
        headers = self.__create_headers()
        logger.info("Getting bill with id: " + bill_id)
        response = requests.get(f'https://loyalty-app.jumbo.com/api/receipt/{bill_id}', headers=headers)
        # response = requests.get(f'https://loyalty-app.jumbo.com/api/receipt/5wigc64hvh-a2965e92-4a95-11ef-8837-ac190a7f0000.json', headers=headers)

        response = response.json()
        image = json.loads(response['receiptImage']['image'])
        with open("Output.txt", "w") as text_file:
            text_file.write(str(image))
        textObjects = image['documents'][0]['documents'][0]['printSections'][0]['textObjects']
        for textObject in textObjects:
            textlines = textObject['textLines']
            for textline in textlines:
                texts = textline['texts']

                ## Products
                if len(texts) == 4:
                    name = ''
                    price = ''
                    for i in [0, 3]:
                        text = texts[i]['text']
                        text = text.strip()
                        text = text.capitalize()
                        if text != '':
                            if i == 0:
                                name = text
                            else:
                                price = text
                    list.append(product(name, price))


                # If we are under the totaal section, we can stop
                if texts[0]['text'] == 'Totaal                        ':
                    return list
        return list

    def get_list_bonnen(self):
        logger.info("Starting get_list_bonnen")
        headers = self.__create_headers()

        logger.info("Getting list of bonnen")
        response = requests.get('https://loyalty-app.jumbo.com/api/receipt/customer/overviews', headers=headers)
        return response.json()

    def __check_token_validity_and_update(self):
        logger.info("Checking token validity")
        if self.__get_remaining_time() < 100:
            logger.info("Token expired, getting new token")
            self.access_token, self.refresh_token = self.__get_new_token()
            if self.access_token is None:
                return False

    def __get_remaining_time(self):
        logger.info("Getting remaining time")
        if self.access_token is None:
            return 0
        decoded_token = jwt.decode(self.access_token, options={"verify_signature": False})
        current_time = int(time.time())
        return decoded_token['exp'] - current_time


    def __get_new_token(self):
        logger.info("Getting new token")
        payload = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'refresh_token': self.refresh_token
        }

        response = requests.post(self.token_endpoint, data=payload)
        if response.status_code == 200:
            tokens = response.json()
            new_access_token = tokens['access_token']
            new_refresh_token = tokens.get('refresh_token', self.refresh_token)  # Update refresh token if provided
            try:
                dotenv.set_key(dotenv_file, 'REFRESH_TOKEN', new_refresh_token)
            except:
                logger.error("Failed to update refresh token in .env file")

            try:
                os.environ['REFRESH_TOKEN'] = new_refresh_token
            except:
                logger.error("Failed to update refresh token in environment variables")
            return new_access_token, new_refresh_token
        else:
            return None, None
