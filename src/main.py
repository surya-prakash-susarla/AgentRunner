from runner.agent_runner import AgentRunner

print("Creating runner")
runner = AgentRunner()

print("Runner created")
query = "test query"
print("Runner response: {response}".format(response = runner.get_response(query)))

print("Terminating")