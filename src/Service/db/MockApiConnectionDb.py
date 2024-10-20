import logging
from Service.db.model.ApiConnectionStored import ApiConnectionStored

class MockDb:
    def __init__(self):
        self.data = {}

    def get_by_connection_id(self, connection_id: int) -> ApiConnectionStored:
        return self.data.get(connection_id)

    def upsert(self, api_connection: ApiConnectionStored):
        if api_connection.id is None:
            api_connection.id = len(self.data) + 1
        self.data[api_connection.id] = api_connection
        logging.debug(f"Upserted data: {self.data}")
        return self.data[api_connection.id]