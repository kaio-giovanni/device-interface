import logging
import asyncio

import requests

class HttpRequests:
    def __init__(self, base_url):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug(f"Using the API Url: {base_url}")

    async def sendData(self, address, values):
        data = {
            'address': address,
            'values': values
        }
        try:
            await asyncio.to_thread(requests.post, self.base_url, json = data)
        except Exception as exc:
            self.logger.error(f"Error trying to send data {data} to endpoint {self.base_url} - {exc}")
