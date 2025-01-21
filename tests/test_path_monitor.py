import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestLogHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            logger.info(f"File modified: {event.src_path}")
            
    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"File created: {event.src_path}")

def test_path_monitoring(paths):
    """Test monitoring multiple paths for file changes."""
    observer = Observer()
    handler = TestLogHandler()
    
    # Set up monitoring for each path
    for path in paths:
        if not os.path.exists(path):
            os.makedirs(path)
        observer.schedule(handler, path, recursive=False)
        logger.info(f"Monitoring path: {path}")
    
    observer.start()
    try:
        # Create test files in each path
        for path in paths:
            test_file = os.path.join(path, "test.log")
            with open(test_file, "w") as f:
                f.write("Initial content\n")
            time.sleep(1)
            
            # Modify test files
            with open(test_file, "a") as f:
                f.write("New content\n")
            time.sleep(1)
            
    except KeyboardInterrupt:
        observer.stop()
    observer.stop()
    observer.join()

if __name__ == "__main__":
    # Test with multiple paths
    test_paths = [
        "./test_logs/path1",
        "./test_logs/path2"
    ]
    test_path_monitoring(test_paths)