import re
import json
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogParser:
    def __init__(self, log_config: Dict[str, Any]):
        self.log_config = log_config
        self.field_mappings = log_config["field_mappings"]

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        try:
            # 尝试解析为JSON
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                # 使用正则表达式解析
                data = self._parse_text_log(line)

            if not data:
                return None

            # 应用字段映射
            return self._apply_field_mapping(data)
        except Exception as e:
            logger.error(f"Error parsing line: {str(e)}")
            return None

    def _parse_text_log(self, line: str) -> Dict[str, Any]:
        result = {}
        for field_mapping in self.field_mappings:
            source_field = field_mapping["source_field"]
            pattern = f"{source_field}=([^\\s]+)"
            match = re.search(pattern, line)
            if match:
                result[source_field] = match.group(1)
        return result if result else {"raw_message": line.strip()}

    def _apply_field_mapping(self, data: Dict[str, Any]) -> Dict[str, Any]:
        result = {}
        for mapping in self.field_mappings:
            source_field = mapping["source_field"]
            target_field = mapping["target_field"]
            field_type = mapping.get("type", "string")

            if source_field in data:
                value = data[source_field]
                converted_value = self._convert_type(value, field_type)
                if converted_value is not None:
                    result[target_field] = converted_value

        return result if result else None

    def _convert_type(self, value: Any, target_type: str) -> Any:
        try:
            if target_type == "string":
                return str(value)
            elif target_type == "int":
                return int(value)
            elif target_type == "float":
                return float(value)
            elif target_type == "datetime":
                if isinstance(value, str):
                    formats = [
                        "%Y-%m-%d %H:%M:%S",
                        "%Y-%m-%dT%H:%M:%S",
                        "%Y/%m/%d %H:%M:%S",
                        "%Y-%m-%d %H:%M:%S.%f"
                    ]
                    for fmt in formats:
                        try:
                            return datetime.strptime(value, fmt)
                        except ValueError:
                            continue
                    raise ValueError(f"Unable to parse datetime: {value}")
                return value
            elif target_type == "bool":
                return str(value).lower() in ('true', '1', 'yes', 'y')
            return value
        except Exception as e:
            logger.error(f"Type conversion error: {str(e)}")
            return None