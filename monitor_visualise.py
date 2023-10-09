import os
import time
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

AGENT_SCHEDULES_DIR = "/home/stark/Academics/Main project/Test_4/agent_schedules"  # Adjust the path as needed
AGENTS_YAML_PATH = "/home/stark/Academics/Main project/Test_4/agents.yaml"

# Handler for file changes
class AgentScheduleHandler(FileSystemEventHandler):

    def on_modified(self, event):
        if event.is_directory:
            return
        if "output_agent" in event.src_path:
            self.process_updated_schedule(event.src_path)

    def process_updated_schedule(self, filepath):
        with open(filepath, 'r') as file:
            agent_data = yaml.load(file, Loader=yaml.FullLoader)
        
        max_time = max(item['t'] for item in agent_data['schedule'])
        agent_name = agent_data['agent']
        
        # Start a timer
        start_time = time.time()
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time >= max_time:
                final_position = [agent_data['schedule'][-1]['x'], agent_data['schedule'][-1]['y']]
                update_agents_yaml(agent_name, final_position)
                break

def update_agents_yaml(agent_name, new_position):
    with open(AGENTS_YAML_PATH, 'r') as file:
        agents = yaml.load(file, Loader=yaml.FullLoader)

    for agent in agents:
        if agent['name'] == agent_name:
            agent['start'] = new_position
            agent['status'] = 'free'
            break

    with open(AGENTS_YAML_PATH, 'w') as file:
        yaml.dump(agents, file)

    print(f"Updated {agent_name} in agents.yaml with position {new_position} and set status to 'free'.")

if __name__ == "__main__":
    event_handler = AgentScheduleHandler()
    observer = Observer()
    observer.schedule(event_handler, path=AGENT_SCHEDULES_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
