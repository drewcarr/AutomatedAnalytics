from IntegrationTestRig.IntegrationTestRig import IntegrationTestRig

from Service.client.ApiConnectionClient import ApiConnectionClient
from Service.model.ApiConnection import ApiConnection

class ItUpsertsApiConnectionTest(IntegrationTestRig):
    resource_file = "ApiConnectionResource.py"

    @staticmethod
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

        client.upsert_api_connection(expected)

        actual = client.get_api_connection_by_id(expected.id)

        assert expected == actual

