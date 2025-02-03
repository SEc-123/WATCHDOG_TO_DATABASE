import logging
from sqlalchemy import create_engine, text
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestDBConnection:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.engine = None
        
    def _load_config(self, config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def test_connection(self):
        """Test database connection and basic operations."""
        try:
            db_config = self.config['database']
            url = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['db_name']}"
            
            # Try to create engine
            logger.info("Testing database connection...")
            self.engine = create_engine(url)
            
            # Test connection by executing simple query
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                logger.info("Database connection successful!")
                
                # Test table existence
                table_name = db_config['table']
                result = conn.execute(text(
                    f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table_name}')"
                ))
                table_exists = result.scalar()
                
                if table_exists:
                    logger.info(f"Table '{table_name}' exists")
                else:
                    logger.warning(f"Table '{table_name}' does not exist")
                
            return True
            
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return False

def test_db():
    # Test configuration
    test_config = {
        'database': {
            'type': 'postgres',
            'host': 'localhost',
            'port': 5432,
            'user': 'test_user',
            'password': 'test_password',
            'db_name': 'test_db',
            'table': 'test_logs'
        }
    }
    
    # Save test config
    with open('test_db_config.yaml', 'w') as f:
        yaml.dump(test_config, f)
    
    # Run connection test
    db_tester = TestDBConnection('test_db_config.yaml')
    db_tester.test_connection()

if __name__ == "__main__":
    test_db()