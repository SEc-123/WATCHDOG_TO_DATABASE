import yaml
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestFieldMapper:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.output_file = "test_output.txt"
        
    def _load_config(self, config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def process_log_line(self, line):
        """Test processing a log line with configured field mappings."""
        try:
            # Parse the input line (assuming JSON format for test)
            input_data = json.loads(line)
            output_data = {}
            
            # Apply field mappings
            for field_map in self.config['monitoring']['fields']:
                raw_field = field_map['raw_field']
                map_to = field_map['map_to']
                
                if raw_field in input_data:
                    # Apply any type conversion if specified
                    if 'type' in field_map:
                        if field_map['type'] == 'datetime':
                            output_data[map_to] = datetime.fromisoformat(input_data[raw_field])
                        elif field_map['type'] == 'integer':
                            output_data[map_to] = int(input_data[raw_field])
                        else:
                            output_data[map_to] = input_data[raw_field]
                    else:
                        output_data[map_to] = input_data[raw_field]
            
            # Write to output file
            with open(self.output_file, 'a') as f:
                f.write(f"Input: {line}\n")
                f.write(f"Mapped: {json.dumps(output_data, default=str)}\n\n")
                
            return output_data
            
        except Exception as e:
            logger.error(f"Error processing line: {e}")
            return None

def test_field_mapping():
    # Test configuration
    test_config = {
        'monitoring': {
            'fields': [
                {'raw_field': 'timestamp', 'map_to': 'log_time', 'type': 'datetime'},
                {'raw_field': 'ip', 'map_to': 'client_ip'},
                {'raw_field': 'status', 'map_to': 'response_status', 'type': 'integer'}
            ]
        }
    }
    
    # Save test config
    with open('test_config.yaml', 'w') as f:
        yaml.dump(test_config, f)
    
    # Create mapper instance
    mapper = TestFieldMapper('test_config.yaml')
    
    # Test data
    test_logs = [
        '{"timestamp": "2023-01-01T10:00:00", "ip": "192.168.1.1", "status": "200"}',
        '{"timestamp": "2023-01-01T10:01:00", "ip": "192.168.1.2", "status": "404"}'
    ]
    
    # Process test logs
    for log in test_logs:
        result = mapper.process_log_line(log)
        logger.info(f"Processed log: {result}")

if __name__ == "__main__":
    test_field_mapping()