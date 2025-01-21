import os
import time
import yaml
import logging
from queue import Queue
from threading import Thread, Event
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sqlalchemy import create_engine, Table, Column, MetaData
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LogProcessor:
    def __init__(self, config_path='config.yaml'):
        self.config = self._load_config(config_path)
        self.file_positions = {}
        self.queue = Queue(maxsize=self.config['performance']['max_queue_length'])
        self.stop_event = Event()
        self.db_engine = self._create_db_engine()
        self.metadata = MetaData()
        self.log_table = self._create_table()

    def _load_config(self, config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def _create_db_engine(self):
        db_config = self.config['database']
        url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['db_name']}"
        return create_engine(url)

    def _create_table(self):
        table_name = self.config['database']['table']
        return Table(table_name, self.metadata,
            Column('id', 'INTEGER', primary_key=True),
            Column('log_time', 'TIMESTAMP'),
            Column('client_ip', 'VARCHAR'),
            Column('response_status', 'INTEGER'),
            Column('size', 'INTEGER'),
            Column('agent_id', 'VARCHAR'),
            Column('created_at', 'TIMESTAMP', default=datetime.utcnow)
        )

    def process_log_line(self, line):
        """Process a single log line and return structured data"""
        try:
            # Add your log parsing logic here
            # This is a simplified example
            parsed_data = {
                'log_time': datetime.now(),
                'client_ip': '127.0.0.1',
                'response_status': 200,
                'size': 1024,
                'agent_id': os.uname().nodename
            }
            return parsed_data
        except Exception as e:
            logger.error(f"Error processing log line: {e}")
            return None

    def insert_batch(self, records):
        """Insert a batch of records into the database"""
        if not records:
            return

        try:
            with self.db_engine.begin() as conn:
                stmt = insert(self.log_table).values(records)
                conn.execute(stmt)
            logger.info(f"Inserted {len(records)} records")
        except Exception as e:
            logger.error(f"Database insertion error: {e}")

class LogHandler(FileSystemEventHandler):
    def __init__(self, processor):
        self.processor = processor

    def on_modified(self, event):
        if not event.is_directory:
            self._handle_log_file(event.src_path)

    def _handle_log_file(self, filepath):
        try:
            current_position = self.processor.file_positions.get(filepath, 0)
            
            with open(filepath, 'r') as f:
                f.seek(current_position)
                new_lines = f.readlines()
                
                for line in new_lines:
                    processed_data = self.processor.process_log_line(line)
                    if processed_data:
                        self.processor.queue.put(processed_data)
                
                self.processor.file_positions[filepath] = f.tell()
        except Exception as e:
            logger.error(f"Error handling log file {filepath}: {e}")

def database_worker(processor):
    """Background worker to batch insert records"""
    batch = []
    batch_size = processor.config['performance']['batch_size']
    
    while not processor.stop_event.is_set() or not processor.queue.empty():
        try:
            record = processor.queue.get(timeout=1)
            batch.append(record)
            
            if len(batch) >= batch_size:
                processor.insert_batch(batch)
                batch = []
        except Exception:
            if batch:  # Insert remaining records
                processor.insert_batch(batch)
                batch = []

def main():
    processor = LogProcessor()
    
    # Start database worker thread
    db_thread = Thread(target=database_worker, args=(processor,))
    db_thread.start()
    
    # Set up watchdog
    event_handler = LogHandler(processor)
    observer = Observer()
    observer.schedule(event_handler, 
                     processor.config['monitoring']['watch_path'], 
                     recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        processor.stop_event.set()
        observer.stop()
        db_thread.join()
        observer.join()

if __name__ == "__main__":
    main()