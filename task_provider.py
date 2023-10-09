import random
import time
import multiprocessing
import yaml
from agent_utils import get_free_agents, set_agent_status

def random_free_location(dimensions, obstacles):
    while True:
        rand_x = random.randint(0, dimensions[0] - 1)
        rand_y = random.randint(0, dimensions[1] - 1)
        if (rand_x, rand_y) not in obstacles:
            return [rand_x, rand_y]

def task_provider(queue):
    count = 0
    while True:
        # Your map dimensions and obstacles
        dimensions = [32, 32]
        obstacles = [[1, 28], [27, 20], [1, 14], [4, 26], [8, 1], [0, 27], [15, 22], 
        [6, 9], 
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

        free_agents = get_free_agents()
        tasks_for_cnp = []

        for i in range(len(free_agents)):
            location = random_free_location(dimensions, obstacles)
            print(f"Providing Task {count}: {location}")
            tasks_for_cnp.append(location)
            count += 1

        tasks_to_save = []
        for task in tasks_for_cnp:
            priority = random.uniform(0, 1)
            tasks_to_save.append({
                'location': task,
                'priority': priority
            })
            queue.put((task, priority))  # send task and its priority to the queue
        
        # Save tasks to tasks.yaml
        with open('tasks.yaml', 'w') as f:
            yaml.safe_dump(tasks_to_save, f)
        
        time.sleep(45)

if __name__ == "__main__":
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=task_provider, args=(q,))
    p.start()