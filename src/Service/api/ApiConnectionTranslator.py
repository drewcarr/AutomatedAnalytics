from Service.db.model.ApiConnectionStored import ApiConnectionStored
from Service.model.ApiConnection import ApiConnection
from Service.db.MockApiConnectionDb import MockDb

class ApiConnectionTranslator:
    def __init__(self, mockDb: MockDb):
        self.mockDb = mockDb

    def get_api_connection(self, connection_id: int) -> ApiConnection:
        #TODO: update to actual db call
        api_connection_stored = self.mockDb.get_by_connection_id(connection_id)
        return self._to_api_connection(api_connection_stored)

    def upsert_api_connection(self, api_connection: ApiConnection) -> ApiConnection:
        #TODO: update to actual db call
        api_connection_stored = self.mockDb.upsert(self._to_api_connection_stored(api_connection))
        return self._to_api_connection(api_connection_stored)

    @staticmethod
    def _to_api_connection(api_connection_stored: ApiConnectionStored) -> ApiConnection:
        return ApiConnection(
            id=api_connection_stored.id,
            name=api_connection_stored.name,
            endpoint_url=api_connection_stored.endpoint_url,
            auth_type=api_connection_stored.auth_type,
            api_key=api_connection_stored.api_key,
            client_id=api_connection_stored.client_id,
            client_secret=api_connection_stored.client_secret,
            access_token=api_connection_stored.access_token,
            refresh_token=api_connection_stored.refresh_token,
            headers=api_connection_stored.headers,
            rate_limit=api_connection_stored.rate_limit,
            timeout=api_connection_stored.timeout,
            api_version=api_connection_stored.api_version
        )

    @staticmethod
    def _to_api_connection_stored(api_connection: ApiConnection) -> ApiConnectionStored:
        return ApiConnectionStored(
            id=api_connection.id,
            name=api_connection.name,
            endpoint_url=api_connection.endpoint_url,
            auth_type=api_connection.auth_type,
            api_key=api_connection.api_key,
            client_id=api_connection.client_id,
            client_secret=api_connection.client_secret,
            access_token=api_connection.access_token,
            refresh_token=api_connection.refresh_token,
            headers=api_connection.headers,
            rate_limit=api_connection.rate_limit,
            timeout=api_connection.timeout,
            api_version=api_connection.api_version
        )