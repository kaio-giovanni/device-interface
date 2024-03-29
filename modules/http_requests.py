import asyncio
import logging
import os

import requests


class HttpRequests:

    def __init__(self, base_url):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.info(f"Using the API Url: {base_url}")
        self.api_token = os.getenv("API_TOKEN", "")
        self.api_scope = os.getenv("API_SCOPE", "")

    async def send_data(self, data) -> bool:
        try:
            endpoint = self.base_url + "/v1/items/measurements"
            http_response = await asyncio.to_thread(requests.post,
                                                    endpoint,
                                                    json=data,
                                                    headers={"token": self.api_token, "scope": self.api_scope})
            if http_response.ok:
                self.logger.info(f"The JSON: {data} was successfully sent to the endpoint: {self.base_url}")
                return True
            else:
                self.logger.error(f"The API returned an error message: {http_response}")
                return False
        except Exception as exc:
            self.logger.error(f"The API returned an error message: {exc}")
            return False
