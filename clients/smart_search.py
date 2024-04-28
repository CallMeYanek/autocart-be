import requests

from utils.utils import log_return_value


class SmartSearchClient:
    def __init__(self):
        self.base_url = 'http://localhost:8000/api/v1/'
        self.products_url = self.base_url + 'products/'

    @log_return_value
    def api_call(self, url, user_id) -> str:
        headers = {"USER-ID": user_id}
        response = requests.get(url, headers=headers)
        resp_json = response.json()
        return resp_json

    def get_products(self, tags: str, user_id: str) -> str:
        url = f'{self.products_url}?tags={tags}'
        resp = self.api_call(url=url, user_id=user_id)
        return resp
