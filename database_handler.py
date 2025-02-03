import mysql.connector
from mysql.connector import pooling
from typing import Dict, Any, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pool = self._create_connection_pool()

    def _create_connection_pool(self):
        db_config = {
            'host': self.config['host'],
            'port': self.config['port'],
            'user': self.config['user'],
            'password': self.config['password'],
            'database': self.config['database'],
            'pool_name': 'mypool',
            'pool_size': 5
        }
        return mysql.connector.pooling.MySQLConnectionPool(**db_config)

    def get_connection(self):
        return self.pool.get_connection()

    def insert_log(self, table: str, data: Dict[str, Any]) -> None:
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            values = tuple(data.values())
            
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, values)
                conn.commit()
        except Exception as e:
            logger.error(f"Error inserting data: {str(e)}")
            raise

    def close(self):
        if hasattr(self, 'pool'):
            self.pool._remove_connections()