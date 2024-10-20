from flask import Flask, jsonify, request
from flask_cors import CORS

from Service.model.Agent import Agent
from Service.db.MockAgentDb import MockAgentDb
from Service.api.AgentTranslator import AgentTranslator

app = Flask(__name__)
CORS(app)
mock_db = MockAgentDb()
api_translator = AgentTranslator(mock_db)

@app.route('/v1/agents/<int:agent_id>', methods=['GET'])
def get_agent_by_id(agent_id: int):
    return jsonify(message=api_translator.get_agent(agent_id))

@app.route('/v1/agents', methods=['PUT'])
def upsert_agent():
    agent_data = request.get_json()
    agent = Agent(**agent_data)
    return jsonify(message=api_translator.upsert_agent(agent))


if __name__ == '__main__':
    app.run(port=8000)