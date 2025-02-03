import json
import time
import logging
import os
import re
from typing import Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from log_parser import LogParser
from database_handler import DatabaseHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LogFileHandler(FileSystemEventHandler):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_handler = DatabaseHandler(config["database"])
        self.parsers = {}
        self.file_positions = {}
        
        for log_config in config["log_files"]:
            self.parsers[log_config["file_pattern"]] = {
                "parser": LogParser(log_config),
                "table": log_config["table"]
            }

    def on_created(self, event):
        if event.is_directory:
            return
        logger.info(f"New file created: {event.src_path}")
        self._process_file(event.src_path, 0)

    def on_modified(self, event):
        if event.is_directory:
            return
        logger.info(f"File modified: {event.src_path}")
        last_position = self.file_positions.get(event.src_path, 0)
        self._process_file(event.src_path, last_position)

    def _process_file(self, file_path: str, start_position: int):
        for pattern, config in self.parsers.items():
            if re.search(pattern, os.path.basename(file_path)):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        f.seek(start_position)
                        new_content = f.read()
                        
                        if not new_content:
                            return

                        current_position = f.tell()
                        self.file_positions[file_path] = current_position
                        
                        for line in new_content.splitlines():
                            if line.strip():
                                record = config["parser"].parse_line(line)
                                if record:
                                    try:
                                        self.db_handler.insert_log(config["table"], record)
                                        logger.debug(f"Inserted record: {record}")
                                    except Exception as e:
                                        logger.error(f"Error inserting record: {str(e)}")
                                        
                except Exception as e:
                    logger.error(f"Error processing file {file_path}: {str(e)}")

    def cleanup_file_positions(self):
        for file_path in list(self.file_positions.keys()):
            if not os.path.exists(file_path):
                del self.file_positions[file_path]

def main():
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        return

    try:
        event_handler = LogFileHandler(config)
        observer = Observer()
        observer.schedule(
            event_handler, 
            config["watch_directory"], 
            recursive=config.get("recursive", False)
        )

        logger.info(f"Starting file monitoring in {config['watch_directory']}...")
        observer.start()

        try:
            while True:
                time.sleep(1)
                event_handler.cleanup_file_positions()
        except KeyboardInterrupt:
            logger.info("Stopping file monitoring...")
            observer.stop()
            event_handler.db_handler.close()
        observer.join()

    except Exception as e:
        logger.error(f"Error in main loop: {str(e)}")

if __name__ == "__main__":
    main()