import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import os

class Watcher:

    def __init__(self, watch_directory, target_file):
        self.TARGET_FILE = os.path.join(watch_directory, target_file)  # This is now a full path.
        self.watch_directory = watch_directory
        self.event_handler = None
        self.observer = Observer()

    def run_command(self):
        print("[DEBUG] Running command...")
        # Modify the command below as per your requirement
        command = ["python3", "/home/stark/Academics/Main project/Test_4/cbs.py", "/home/stark/Academics/Main project/Test_4/input.yaml", "/home/stark/Academics/Main project/Test_4/agent_schedules"]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[DEBUG] Error executing command: {result.stderr}")
        else:
            print("[DEBUG] Command executed.")

	    


    def start(self):
        self.event_handler = FileChangeHandler(self.TARGET_FILE, self.run_command)
        print(f"[DEBUG] Starting observer on directory '{self.watch_directory}' to watch '{self.TARGET_FILE}'")
        self.observer.schedule(self.event_handler, self.watch_directory, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[DEBUG] Keyboard interrupt received. Stopping observer...")
            self.observer.stop()
        self.observer.join()

class FileChangeHandler(FileSystemEventHandler):
    
    def __init__(self, target_file, callback):
        self.target_file = target_file
        self.callback = callback
        self.last_modified_time = os.path.getmtime(self.target_file)  # initialize last_modified_time

    def on_modified(self, event):
        if not event.is_directory:
            if event.src_path == self.target_file:
                time.sleep(0.5)  # wait to ensure the file write is complete
                if os.path.getmtime(self.target_file) != self.last_modified_time:
                    print("[DEBUG] Detected a change in file:", event.src_path)
                    self.last_modified_time = os.path.getmtime(self.target_file)
                    self.callback()
            else:
                print("[DEBUG] Change detected in another file:", event.src_path, ". Ignoring...")
    def on_moved(self, event):
        # Handle the event where a file might be replaced
        if not event.is_directory:
            # Check for the destination path because the file was moved to this location
            if event.dest_path == self.target_file:
                print("[DEBUG] Detected a move event in file:", event.dest_path)
                self.callback()
            else:
                print("[DEBUG] File moved to another location:", event.dest_path, ". Ignoring...")


if __name__ == "__main__":
    # Specify the directory path and the target file
    watch_directory = '/home/stark/Academics/Main project/Test_4/'  # Current directory
    target_file = 'input.yaml'
    watcher = Watcher(watch_directory, target_file)
    watcher.start()

