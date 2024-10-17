import requests

from model.ApiConnection import ApiConnection


class ApiConnectionClient:
    def __init__(self):
        # TODO: eventually point this towards our load balancer
        self.base_url = "http://localhost:8000"

    def get_api_connection_by_id(self, connection_id: int):
        try:
            response = requests.get(self.base_url + "/v1/connections/" + str(connection_id))
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def upsert_api_connection(self, api_connection: ApiConnection):
        try:
            response = requests.put(self.base_url + "/v1/connections", json=api_connection.__dict__)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}