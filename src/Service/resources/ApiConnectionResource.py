from flask import Flask, jsonify, request
from flask_cors import CORS

from api.ApiConnectionTranslator import ApiConnectionTranslator
from model.ApiConnection import ApiConnection
from db.MockDb import MockDb

app = Flask(__name__)
CORS(app)
mock_db = MockDb()
api_connection_translator = ApiConnectionTranslator(mock_db)

@app.route('/v1/connections/<int:connection_id>', methods=['GET'])
def get_api_connection_by_id(connection_id: int):
    return jsonify(message=api_connection_translator.get_api_connection(connection_id))

@app.route('/v1/connections', methods=['PUT'])
def upsert_api_connection():
    api_connection_data = request.get_json()
    api_connection = ApiConnection(**api_connection_data)
    return jsonify(message=api_connection_translator.upsert_api_connection(api_connection))

if __name__ == '__main__':
    app.run(port=8000)