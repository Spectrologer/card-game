import time
import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PythonChangeHandler(FileSystemEventHandler):
    """Restarts the script when a .py file is modified."""
    def __init__(self):
        self.process = None
        self.start_process()

    def start_process(self):
        """Starts or restarts the main.py script."""
        if self.process:
            self.process.kill()
        print(">>> Starting main.py...")
        self.process = subprocess.Popen(['python', 'main.py'])

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f">>> Detected change in {os.path.basename(event.src_path)}. Restarting...")
            self.start_process()

if __name__ == "__main__":
    path = '.' # Watch the current directory and all subdirectories
    event_handler = PythonChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(">>> Watching for file changes...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        event_handler.process.kill()
    observer.join()