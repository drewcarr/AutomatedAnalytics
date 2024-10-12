from random import random

from resources.ApiConnectionResource import api_connection_client

if __name__ == '__main__':
    api_connection_details = {
        "id": str(random()),
        "name": "Test API Connection",
        "endpoint_url": "http://localhost:8000",
        "auth_type": "Bearer",
        "api_key": "test_api_key",
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "headers": {"Custom-Header": "test_value"},
        "rate_limit": 1000,
        "timeout": 30,
        "api_version": "v1"
    }

    print(api_connection_client.upsert_api_connection(api_connection_details))
    print(api_connection_client.get_api_connection_by_id(1))