# main.py
import threading
import multiprocessing

# Import the task provider and allocation functions
from task_provider import task_provider
from task_allocation import allocate_tasks

def main():
    # Create a shared multiprocessing queue
    q = multiprocessing.Queue()

    # Start task provider
    provider_thread = threading.Thread(target=task_provider, args=(q,))
    provider_thread.start()

    # Start task allocation
    allocation_thread = threading.Thread(target=allocate_tasks, args=(q,))
    allocation_thread.start()

    provider_thread.join()
    allocation_thread.join()

if __name__ == "__main__":
    main()
