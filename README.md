# Log Monitoring Agent

A robust log monitoring solution that watches local log files and automatically forwards processed data to a remote database. This agent supports dynamic field mapping, multiple file monitoring, and reliable data transmission.

## Features

- **Real-time Log Monitoring**
  - Watch multiple log files and directories
  - Automatic detection of file creation and modifications
  - Support for log file rotation
  - Configurable watch paths and patterns

- **Dynamic Field Mapping**
  - Flexible field mapping configuration
  - Support for multiple data types (string, integer, datetime)
  - Custom field transformation rules
  - Data validation and filtering

- **Remote Database Integration**
  - Support for PostgreSQL and MySQL
  - Batch insert for better performance
  - Connection pooling
  - Automatic retry on connection failures

- **Performance & Reliability**
  - Asynchronous processing
  - Batch processing for optimal database performance
  - Local buffering during network issues
  - Automatic recovery from failures

## Project Structure

```
log-monitoring-agent/
├── agent.py              # Main agent implementation
├── config.yaml          # Configuration file
├── requirements.txt     # Python dependencies
├── tests/              # Test directory
│   ├── test_path_monitor.py    # Path monitoring tests
│   ├── test_field_mapping.py   # Field mapping tests
│   └── test_db_connection.py   # Database connection tests
└── README.md           # Documentation
```

## Requirements

- Python 3.7+
- PostgreSQL 10+ or MySQL 5.7+
- Required Python packages (see requirements.txt):
  - watchdog==3.0.0
  - sqlalchemy==2.0.23
  - PyYAML==6.0.1
  - psycopg2-binary==2.9.9

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd log-monitoring-agent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure the agent:
   - Copy `config.yaml.example` to `config.yaml`
   - Update configuration values for your environment

## Configuration

The `config.yaml` file contains all necessary settings:

```yaml
monitoring:
  watch_path: "/var/logs/app_log/"
  file_pattern: "*.log"
  fields:
    - raw_field: "original_timestamp"
      map_to: "log_time"
    - raw_field: "original_ip"
      map_to: "client_ip"

database:
  type: "postgres"  # or "mysql"
  host: "localhost"
  port: 5432
  user: "agent_user"
  password: "agent_password"
  db_name: "log_analysis"
  table: "converted_logs"

performance:
  read_interval: 2
  batch_size: 1000
  max_queue_length: 5000
  enable_async_insert: true
```

## Usage

1. Start the agent:
   ```bash
   python agent.py
   ```

2. Monitor agent status:
   - Check console output for real-time status
   - Review log files for detailed information
   - Monitor database for inserted records

3. Stop the agent:
   - Press Ctrl+C for graceful shutdown
   - Agent will complete pending operations before exit

## Testing

The project includes three test scripts to verify core functionality:

### 1. Path Monitoring Test
```bash
python tests/test_path_monitor.py
```
Tests the file monitoring functionality:
- Monitors multiple paths
- Detects file creation and modification
- Validates watchdog integration

### 2. Field Mapping Test
```bash
python tests/test_field_mapping.py
```
Verifies field mapping functionality:
- Tests field transformation rules
- Validates type conversions
- Outputs results to test_output.txt
- Supports custom field mappings

### 3. Database Connection Test
```bash
python tests/test_db_connection.py
```
Tests database connectivity:
- Validates connection settings
- Verifies table existence
- Tests basic queries
- Checks error handling

### Running Tests

1. Create a test environment:
   ```bash
   mkdir -p tests/test_logs/path1 tests/test_logs/path2
   ```

2. Configure test settings:
   - Modify test configurations in each test file
   - Adjust database credentials in test_db_connection.py
   - Customize field mappings in test_field_mapping.py

3. Run individual tests:
   ```bash
   # Test path monitoring
   python tests/test_path_monitor.py

   # Test field mapping
   python tests/test_field_mapping.py

   # Test database connection
   python tests/test_db_connection.py
   ```

4. Check test results:
   - Monitor console output for test status
   - Review test_output.txt for field mapping results
   - Verify database connection status

## Error Handling

The agent handles various error conditions:

1. **File System Errors**
   - Missing files or directories
   - Permission issues
   - File rotation events

2. **Database Errors**
   - Connection failures
   - Transaction errors
   - Constraint violations

3. **Data Processing Errors**
   - Invalid log formats
   - Field mapping errors
   - Type conversion failures

## Performance Optimization

The agent includes several performance features:

1. **Batch Processing**
   - Configurable batch sizes for database inserts
   - Memory usage optimization
   - Reduced database load

2. **Asynchronous Operations**
   - Non-blocking file monitoring
   - Background database operations
   - Queue-based processing

3. **Connection Pooling**
   - Reuse database connections
   - Automatic connection management
   - Configurable pool sizes

## Troubleshooting

Common issues and solutions:

1. **Agent Won't Start**
   - Check Python version compatibility
   - Verify configuration file syntax
   - Ensure required permissions

2. **Database Connection Issues**
   - Verify database credentials
   - Check network connectivity
   - Confirm database server status

3. **Log Processing Problems**
   - Review log file permissions
   - Check field mapping configuration
   - Verify log file format





## Support

For support and questions:
- Open an issue in the repository
- Contact the maintainers
- Check the documentation

## Acknowledgments

- watchdog library for file system monitoring
- SQLAlchemy for database operations
- PyYAML for configuration management

