import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartHandler(FileSystemEventHandler):
    def __init__(self, script_name):
        self.script_name = script_name
        self.process = None
        self.start_script()

    def start_script(self):
        if self.process:
            self.process.terminate()
        self.process = subprocess.Popen([sys.executable, self.script_name])

    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            print(f"Change detected in {event.src_path}. Restarting ...")
            self.start_script()
        
if __name__ == "__main__":
    script = "app.py"
    event_handler = RestartHandler(script)
    observer = Observer()
    observer.schedule(event_handler, ".", recursive = True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()