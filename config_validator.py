from typing import Dict, Any, Set
import re
import os

class ConfigValidationError(Exception):
    """配置验证错误异常"""
    pass

class ConfigValidator:
    """配置验证器类"""
    
    VALID_FIELD_TYPES: Set[str] = {'string', 'int', 'float', 'datetime', 'bool'}

    @staticmethod
    def validate_database_config(config: Dict[str, Any]) -> None:
        """验证数据库配置"""
        if not isinstance(config, dict):
            raise ConfigValidationError("Database configuration must be a dictionary")

        # 验证必需的数据库字段
        required_fields = {'host', 'port', 'user', 'password', 'database'}
        missing_fields = required_fields - set(config.keys())
        if missing_fields:
            raise ConfigValidationError(f"Missing required database fields: {missing_fields}")

        # 验证字段类型和值
        if not isinstance(config['port'], int):
            raise ConfigValidationError("Database port must be an integer")
        if config['port'] < 1 or config['port'] > 65535:
            raise ConfigValidationError("Database port must be between 1 and 65535")
        
        for str_field in ['host', 'user', 'password', 'database']:
            if not isinstance(config[str_field], str):
                raise ConfigValidationError(f"Database {str_field} must be a string")
            if not config[str_field]:
                raise ConfigValidationError(f"Database {str_field} cannot be empty")

        # 验证重试配置
        if 'retry' in config:
            retry = config['retry']
            if not isinstance(retry, dict):
                raise ConfigValidationError("Retry configuration must be a dictionary")
            
            required_retry_fields = {'max_attempts', 'delay', 'backoff'}
            missing_retry_fields = required_retry_fields - set(retry.keys())
            if missing_retry_fields:
                raise ConfigValidationError(f"Missing retry configuration fields: {missing_retry_fields}")

            if not isinstance(retry['max_attempts'], int) or retry['max_attempts'] < 1:
                raise ConfigValidationError("max_attempts must be a positive integer")
            if not isinstance(retry['delay'], (int, float)) or retry['delay'] <= 0:
                raise ConfigValidationError("delay must be a positive number")
            if not isinstance(retry['backoff'], (int, float)) or retry['backoff'] <= 1:
                raise ConfigValidationError("backoff must be greater than 1")

        # 验证清理配置
        if 'cleanup' in config:
            cleanup = config['cleanup']
            if not isinstance(cleanup, dict):
                raise ConfigValidationError("Cleanup configuration must be a dictionary")
            
            required_cleanup_fields = {'enabled', 'retention_days', 'interval_hours'}
            missing_cleanup_fields = required_cleanup_fields - set(cleanup.keys())
            if missing_cleanup_fields:
                raise ConfigValidationError(f"Missing cleanup configuration fields: {missing_cleanup_fields}")

            if not isinstance(cleanup['enabled'], bool):
                raise ConfigValidationError("cleanup.enabled must be a boolean")
            if not isinstance(cleanup['retention_days'], int) or cleanup['retention_days'] < 1:
                raise ConfigValidationError("retention_days must be a positive integer")
            if not isinstance(cleanup['interval_hours'], int) or cleanup['interval_hours'] < 1:
                raise ConfigValidationError("interval_hours must be a positive integer")

    @staticmethod
    def validate_watch_config(config: Dict[str, Any]) -> None:
        """验证监控配置"""
        if 'watch_directory' not in config:
            raise ConfigValidationError("Missing watch_directory configuration")
        
        if not isinstance(config['watch_directory'], str):
            raise ConfigValidationError("watch_directory must be a string")
        
        if not os.path.exists(config['watch_directory']):
            raise ConfigValidationError(f"Watch directory does not exist: {config['watch_directory']}")
        
        if not os.path.isdir(config['watch_directory']):
            raise ConfigValidationError(f"watch_directory must be a directory: {config['watch_directory']}")

        # 验证递归配置
        if 'recursive' in config:
            if not isinstance(config['recursive'], bool):
                raise ConfigValidationError("recursive must be a boolean value")

    @staticmethod
    def validate_field_mapping(mapping: Dict[str, Any]) -> None:
        """验证单个字段映射配置"""
        if not isinstance(mapping, dict):
            raise ConfigValidationError("Field mapping must be a dictionary")

        required_mapping_fields = {'source_field', 'target_field', 'type'}
        missing_mapping_fields = required_mapping_fields - set(mapping.keys())
        if missing_mapping_fields:
            raise ConfigValidationError(f"Missing field mapping fields: {missing_mapping_fields}")

        if not isinstance(mapping['source_field'], str) or not mapping['source_field']:
            raise ConfigValidationError("source_field must be a non-empty string")
        
        if not isinstance(mapping['target_field'], str) or not mapping['target_field']:
            raise ConfigValidationError("target_field must be a non-empty string")

        if mapping['type'] not in ConfigValidator.VALID_FIELD_TYPES:
            raise ConfigValidationError(
                f"Invalid field type: {mapping['type']}. "
                f"Must be one of: {ConfigValidator.VALID_FIELD_TYPES}"
            )

    @staticmethod
    def validate_log_files_config(config: Dict[str, Any]) -> None:
        """验证日志文件配置"""
        if 'log_files' not in config:
            raise ConfigValidationError("Missing log_files configuration")
        
        if not isinstance(config['log_files'], list):
            raise ConfigValidationError("log_files must be a list")
        
        if not config['log_files']:
            raise ConfigValidationError("log_files cannot be empty")

        for idx, log_config in enumerate(config['log_files']):
            if not isinstance(log_config, dict):
                raise ConfigValidationError(f"Log file configuration #{idx} must be a dictionary")

            required_fields = {'file_pattern', 'table', 'field_mappings'}
            missing_fields = required_fields - set(log_config.keys())
            if missing_fields:
                raise ConfigValidationError(f"Missing fields in log file #{idx}: {missing_fields}")

            # 验证文件模式
            if not isinstance(log_config['file_pattern'], str) or not log_config['file_pattern']:
                raise ConfigValidationError(f"file_pattern in log file #{idx} must be a non-empty string")
            
            try:
                re.compile(log_config['file_pattern'])
            except re.error as e:
                raise ConfigValidationError(f"Invalid regex pattern in log file #{idx}: {str(e)}")

            # 验证表名
            if not isinstance(log_config['table'], str) or not log_config['table']:
                raise ConfigValidationError(f"table in log file #{idx} must be a non-empty string")

            # 验证字段映射
            if not isinstance(log_config['field_mappings'], list):
                raise ConfigValidationError(f"field_mappings in log file #{idx} must be a list")
            
            if not log_config['field_mappings']:
                raise ConfigValidationError(f"field_mappings in log file #{idx} cannot be empty")

            for mapping_idx, mapping in enumerate(log_config['field_mappings']):
                try:
                    ConfigValidator.validate_field_mapping(mapping)
                except ConfigValidationError as e:
                    raise ConfigValidationError(
                        f"Invalid field mapping #{mapping_idx} in log file #{idx}: {str(e)}"
                    )

    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> None:
        """验证整个配置文件"""
        if not isinstance(config, dict):
            raise ConfigValidationError("Configuration must be a dictionary")

        required_sections = {'database', 'watch_directory', 'log_files'}
        missing_sections = required_sections - set(config.keys())
        if missing_sections:
            raise ConfigValidationError(f"Missing required configuration sections: {missing_sections}")

        cls.validate_database_config(config['database'])
        cls.validate_watch_config(config)
        cls.validate_log_files_config(config)