import time
import os
import subprocess
import sys
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
        # We need to run the main.py from the project root.
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        main_script_path = os.path.join(project_root, 'main.py')
        # Use sys.executable to ensure we use the same python interpreter (from .venv)
        python_executable = sys.executable
        self.process = subprocess.Popen([python_executable, main_script_path], cwd=project_root)

    def on_modified(self, event):
        if event.src_path.endswith('.py') or event.src_path.endswith('.json'):
            print(f">>> Detected change in {os.path.basename(event.src_path)}. Restarting...")
            self.start_process()

if __name__ == "__main__":
    path = '..' # Watch the parent directory (project root) and all subdirectories
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