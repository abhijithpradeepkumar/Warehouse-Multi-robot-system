import yaml
import random
import math
import time
import multiprocessing
from agent_utils import get_free_agents, set_agent_status


class Task:
    def __init__(self, goal, priority=1):
        self.goal = goal
        self.priority = priority
        self.assigned_agent = None

class Agent:
    def __init__(self, start, name):
        self.start = start
        self.name = name
        self.goal = None
    
    def __repr__(self):
        return self.name

    def compute_bid(self, goal, priority=1, wd=1, wp=1):
        distance_cost = abs(goal[0] - self.start[0]) + abs(goal[1] - self.start[1])
        priority_cost = 1 - priority  # since 1 is high priority and 0 is low
        total_cost = wd * distance_cost + wp * priority_cost
        return total_cost

    def perform_task(self, task):
        bid = self.compute_bid(task.goal)
        time.sleep(bid / 10)  # Reduced the sleep time by dividing by 10
        print(f'{self.name} has completed the task at {task.goal}.')

    def act_as_auctioneer(self, agents, task):
        if task.assigned_agent is not None:
            return None
        lowest_bid = float('inf')
        winning_agent = None
        for agent in agents:
            bid = agent.compute_bid(task.goal, task.priority)
            if bid < lowest_bid:
                lowest_bid = bid
                winning_agent = agent
        return winning_agent

def create_task_yaml(agents, queue):
    tasks = {
        'map': {
            'dimensions': [32, 32],
            'obstacles': [[1, 28], [27, 20], [1, 14], [4, 26], [8, 1], [0, 27], [15, 22], [6, 9], 
    [6, 25], [25, 12], [28, 25], [22, 5], [25, 16], [15, 29], [14, 12], [31, 31], 
    [18, 31], [29, 12], [14, 19], [8, 26], [30, 8], [14, 30], [13, 8], [13, 26], 
    [14, 10], [0, 13], [22, 21], [1, 9], [6, 0], [26, 27], [23, 31], [24, 30], 
    [21, 16], [16, 14], [17, 11], [26, 7], [4, 9], [2, 13], [22, 13], [10, 29], 
    [15, 16], [2, 24], [2, 27], [10, 9], [17, 16], [13, 30], [3, 21], [2, 4], 
    [18, 12], [0, 9], [22, 23], [31, 5], [5, 13], [9, 12], [7, 20], [16, 30], 
    [29, 26], [31, 7], [24, 3], [28, 9], [11, 19], [8, 28], [20, 0], [23, 11], 
    [2, 8], [3, 27], [19, 5], [3, 8], [23, 16], [11, 15], [23, 1], [13, 2], 
    [28, 21], [20, 3], [10, 16], [13, 5], [13, 6], [25, 17], [28, 17], [10, 7], 
    [9, 27], [17, 3], [29, 17], [4, 23], [12, 22], [5, 18], [27, 11], [0, 12], 
    [5, 6], [22, 17], [18, 21], [8, 18], [26, 25], [30, 27], [10, 21], [28, 2], 
    [8, 23], [17, 18], [6, 29], [9, 7], [30, 16], [16, 31], [23, 2], [9, 6], 
    [1, 5], [24, 14], [27, 13], [12, 21], [26, 6], [20, 17], [28, 0], [1, 11], 
    [31, 23], [24, 28], [16, 12], [9, 18], [3, 13], [24, 0], [14, 27], [12, 16], 
    [1, 18], [8, 21], [24, 15], [2, 6], [19, 24], [29, 29], [3, 26], [3, 19], 
    [11, 10], [18, 14], [6, 2], [31, 4], [17, 17], [24, 19], [25, 5], [26, 30], 
    [30, 9], [21, 6], [0, 31], [27, 24], [3, 2], [13, 23], [4, 20], [6, 31], 
    [17, 26], [2, 28], [10, 24], [29, 25], [24, 8], [6, 10], [17, 23], [1, 0], 
    [10, 26], [6, 8], [24, 25], [21, 23], [8, 15], [18, 23], [27, 2], [0, 21], 
    [11, 0], [16, 4], [2, 30], [13, 28], [8, 17], [31, 17], [23, 10], [5, 28], 
    [23, 15], [7, 4], [1, 20], [28, 26], [0, 15], [22, 18], [22, 15], [30, 2], 
    [30, 7], [25, 8], [23, 30], [6, 28], [23, 19], [7, 31], [22, 27], [7, 14], 
    [3, 31], [9, 4], [17, 25], [29, 24], [23, 17], [2, 5], [8, 22], [18, 0], 
    [30, 31], [31, 2], [30, 20], [0, 2], [14, 7], [7, 1], [12, 11], [3, 22], 
    [19, 21], [29, 16], [30, 4], [20, 18]]
        },
        'agents': [],
        'tasks': []
    }

    tasks_list = []

    for agent in agents:
        task_info = queue.get()  # This now includes location and priority
        agent.goal = list(task_info[0])  # Get task from queue
        priority = task_info[1]

        tasks['agents'].append({
            'name': agent.name,
            'start': agent.start,
            'goal': list(agent.goal)
        })

        task = Task(agent.goal, priority)
        tasks_list.append(task)

        tasks['tasks'].append({
            'goal': task.goal,
            'priority': task.priority,
            'assigned_agent': None
        })

    with open('/home/stark/Academics/Main project/Test_4/input.yaml', 'w') as file:
        yaml.safe_dump(tasks, file)

    return tasks_list, tasks



def perform_cnp(agents, tasks, tasks_dict):
    unassigned_tasks = [task for task in tasks if task.assigned_agent is None]
    active_agents = agents.copy()

    while unassigned_tasks:
        print(f"Remaining tasks: {len(unassigned_tasks)}")  # Debugging print statement
        random.shuffle(active_agents)
        for agent in active_agents:
            print(f"CNP is being executed for agent {agent.name}.")  # Debugging print statement
            task_to_bid = unassigned_tasks[0]  # Task to be bid on in this round
            print(f"Attempting to assign task {task_to_bid.goal}")  # Debugging print statement
            winning_agent = agent.act_as_auctioneer(active_agents, task_to_bid)
            if winning_agent is None:  # If no agent could take the task, skip it for this round
                print(f"No agent could take task {task_to_bid.goal}")  # Debugging print statement
                continue
            print(f"Assigning task {task_to_bid.goal} to agent {winning_agent.name}")  # Debugging print statement
            
            # Assign the task to the winner
            task_to_bid.assigned_agent = winning_agent.name
            
            set_agent_status(winning_agent.name, "busy")

            # Update the agent's goal in tasks_dict
            for agent_dict in tasks_dict['agents']:
                if agent_dict['name'] == winning_agent.name:
                    agent_dict['goal'] = task_to_bid.goal
            
            # Update the assigned agent for the task in tasks_dict
            for task_dict in tasks_dict['tasks']:
                if task_dict['goal'] == task_to_bid.goal:
                    task_dict['assigned_agent'] = winning_agent.name
                    
            unassigned_tasks.remove(task_to_bid)  # Remove the task from the unassigned list
            active_agents.remove(winning_agent)  # The winner won't bid until the next round
            
            if not unassigned_tasks or not active_agents:  # Exit if no tasks or no agents left
                break

def load_agents_from_yaml(filepath):
    """Load agent details from a given YAML file."""
    with open(filepath, 'r') as file:
        agents_data = yaml.safe_load(file)
    return agents_data

def update_tasks_yaml(assigned_tasks):
    with open('tasks.yaml', 'r') as f:
        existing_tasks = yaml.safe_load(f)
    
    # Remove tasks that have been assigned
    for assigned_task in assigned_tasks:
        for task in existing_tasks:
            if task['location'] == assigned_task.goal:
                existing_tasks.remove(task)
                break

    with open('tasks.yaml', 'w') as f:
        yaml.safe_dump(existing_tasks, f)

def allocate_tasks(queue):
    
    # Load agent details from YAML
    agents_data = load_agents_from_yaml('agents.yaml')
    
    # Create Agent instances only for free agents
    agents_list = [Agent(data['start'], data['name']) for data in agents_data if data['status'] == 'free']
    
    tasks_list, tasks_dict = create_task_yaml(agents_list, queue)

    for agent_task in tasks_dict['agents']:
        print(f"{agent_task['name']} starts at {agent_task['start']} and has a goal at {agent_task['goal']}")

    # Perform Contract Net Protocol
    perform_cnp(agents_list, tasks_list, tasks_dict)

    update_tasks_yaml(tasks_list)


    data = tasks_dict

    for agent in data['agents']:
        agent['start'] = str([agent['start'][0], agent['start'][1]])
        agent['goal'] = str([agent['goal'][0], agent['goal'][1]])

    # Convert format of map details
    data['map']['dimensions'] = str([data['map']['dimensions'][0], data['map']['dimensions'][1]])

    # Convert obstacles to desired string format
    obstacles_string = "\n  " + "\n  ".join([f"- !!python/tuple [{obstacle[0]}, {obstacle[1]}]" for obstacle in data['map']['obstacles']])
    data['map']['obstacles'] = 'OBSTACLES_PLACEHOLDER'  # Temporary placeholder

    # Convert the entire dictionary to a YAML string without modifying the global flow style
    yaml_string = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)

    # Replace the placeholder with the desired obstacles string format
    yaml_string = yaml_string.replace("'[", "[").replace("]'", "]")  # Removing the extra quotes
    yaml_string = yaml_string.replace('OBSTACLES_PLACEHOLDER', obstacles_string)

    # Write the modified YAML string to the output file
    with open('/home/stark/Academics/Main project/Test_4/input.yaml', 'w') as f:
        f.write(yaml_string)
