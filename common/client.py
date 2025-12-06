import requests


class RestClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_json_response(self, url: str, method: str = 'GET', url_params: dict = None, data: dict = None, headers: dict = None, params: dict = None, timeout: int = 10) -> dict:
        try:
            full_url = self.base_url + url.format(**(url_params or {}))
            response = requests.request(method, full_url, json=data, headers=headers, params=params, timeout=timeout)
            return response.json()
        except requests.exceptions.JSONDecodeError as e:
            print(f"Failed to parse json response with status code {response.status_code} from url {full_url}: {response.text}")
            return dict()
        except Exception as e:
            print(f"An error occured whilte trying to get json response from {full_url}: {e}")
            return dict()