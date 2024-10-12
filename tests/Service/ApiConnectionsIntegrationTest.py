from client.ApiConnectionClient import ApiConnectionClient
from model.ApiConnection import ApiConnection
import subprocess
import time
import pytest
import os

@pytest.fixture(scope="module", autouse=True)
def start_service():
    resource_file = os.path.join(os.path.dirname(__file__), '../../Service/resources/ApiConnectionResource.py')

    service_process = subprocess.Popen(["python", resource_file])
    time.sleep(5)

    yield

    service_process.terminate()
    service_process.wait()

def test_upsert_api_connection():
    client = ApiConnectionClient()

    expected = ApiConnection(
        id=1,
        name="Test API Connection",
        endpoint_url="http://localhost:8000",
        auth_type="Bearer",
        api_key="test_api_key",
        client_id="test_client_id",
        client_secret="test_client_secret",
        access_token="test_access_token",
        refresh_token="test_refresh_token",
        headers={"Custom-Header": "test_value"},
        rate_limit={},
        timeout={},
        api_version="v1"
    )

    client.upsert_api_connection(expected.__dict__)

    response = client.get_api_connection_by_id(1)
    actual = response['message']
    assert expected.__dict__ == actual