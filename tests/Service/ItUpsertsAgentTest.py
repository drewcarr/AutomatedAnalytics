from IntegrationTestRig.IntegrationTestRig import IntegrationTestRig
from Service.client.AgentClient import AgentClient
from Service.model.Agent import Agent

class ItUpsertsAgentTest(IntegrationTestRig):
    resource_file = "AgentResource.py"

    @staticmethod
    def test_agent_upsert():
        client = AgentClient()

        expected = Agent(
            id=1,
            name="Test Agent",
            system_prompt="Be a test agent",
            model="gpt-3",
            functions=["test"],
            response_format="json",
            temperature=1.0,
            top_p=1.0,
            api_version="v1"
        )

        client.upsert_agent(expected)

        actual = client.get_agent_by_id(expected.id)

        assert expected == actual