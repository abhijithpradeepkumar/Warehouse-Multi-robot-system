import yaml
import random
import time

def load_agents_from_yaml(filepath):
    """Load agent details from a given YAML file."""
    with open(filepath, 'r') as file:
        agents_data = yaml.safe_load(file)
    return agents_data

def update_random_agents_to_free(filepath):
    """Update the status of a random number of agents to free."""
    agents_data = load_agents_from_yaml(filepath)
    num_of_agents_to_free = random.randint(1, 2)  # Random number between 1 and 2

    busy_agents = [agent for agent in agents_data if agent['status'] == 'busy']

    if not busy_agents:  # If no busy agents, return
        return

    for _ in range(num_of_agents_to_free):
        if busy_agents:
            selected_agent = random.choice(busy_agents)
            selected_agent['status'] = 'free'
            busy_agents.remove(selected_agent)

    with open(filepath, 'w') as file:
        yaml.safe_dump(agents_data, file)

if __name__ == "__main__":
    while True:
        update_random_agents_to_free('agents.yaml')
        time.sleep(15)

