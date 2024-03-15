import asyncio
import logging

import requests


class HttpRequests:

    def __init__(self, base_url):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        self.api_token = None
        self.api_scope = None
        self.logger.setLevel(logging.INFO)
        self.logger.info(f"Using the API Url: {base_url}")

    async def send_data(self, data) -> bool:
        endpoint = self.base_url + "/v1/items/measurements"

        http_response = await asyncio.to_thread(requests.post,
                                                endpoint,
                                                json=data,
                                                headers={"token": "API_TOKEN", "scope": "API_SCOPE"})
        if http_response.ok:
            self.logger.info(f"The JSON: {data} was successfully sent to the endpoint: {self.base_url}")
            return True
        else:
            self.logger.error(
                f"The API returned an error message when trying to send the json: {data} to endpoint {self.base_url}")
            return False

    async def login(self, credentials):
        endpoint = "/login"
        http_response = await asyncio.to_thread(requests.post,
                                                endpoint,
                                                json=credentials)

        if http_response.ok:
            self.logger.info("Successfully logged")
            json = http_response.json()
        else:
            self.logger.error("Error trying to login")
