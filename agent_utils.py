import yaml

def get_free_agents():
    with open("./agents.yaml", 'r') as f:
        agents = yaml.safe_load(f)
    free_agents = [agent for agent in agents if agent["status"] == "free"]
    print(f"Free Agents: {free_agents}")  # Debug print
    return free_agents


def set_agent_status(agent_name, status):
    with open("./agents.yaml", 'r') as f:
        agents = yaml.safe_load(f)
        
    for agent in agents:
        if agent["name"] == agent_name:
            agent["status"] = status

    with open("./agents.yaml", 'w') as f:
        yaml.safe_dump(agents, f)

