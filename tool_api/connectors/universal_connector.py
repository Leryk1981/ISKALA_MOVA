import json
import requests
import logging
import datetime
from typing import Dict, Any
from pathlib import Path

class UniversalToolConnector:
    def __init__(self, tools_dir: str = "/a0/instruments/custom/iskala/tool_api/tools"):
        self.tools_dir = Path(tools_dir)
        self.logger = logging.getLogger(__name__)
        self.secrets = {}
        
    def load_secrets(self, secrets_file: str = ".env"):
        """Load secrets from environment file"""
        try:
            with open(secrets_file) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        self.secrets[key] = value
        except FileNotFoundError:
            self.logger.warning("Secrets file not found")
    
    def load_tool_api(self, tool_id: str) -> Dict[str, Any]:
        """Load tool_api definition from JSON file"""
        tool_file = self.tools_dir / f"{tool_id}.json"
        with open(tool_file, encoding='utf-8') as f:
            return json.load(f)
    
    def execute_intent(self, intent: str, context: Dict[str, Any], tool_id: str = None) -> Dict[str, Any]:
        """Execute an intent using the appropriate tool_api"""
        if not tool_id:
            tool_id = self.find_tool_for_intent(intent)
        
        tool_api = self.load_tool_api(tool_id)
        return self.execute_tool_api(tool_api, context)
    
    def execute_tool_api(self, tool_api: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific tool_api with given context"""
        try:
            # Prepare request
            url = tool_api['url']
            method = tool_api['method']
            headers = self._process_headers(tool_api.get('headers', {}))
            
            # Validate input against schema
            input_data = self._validate_input(context, tool_api.get('input_schema', {}))
            
            # Execute request
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=input_data,
                timeout=30
            )
            
            # Process response
            result = {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'data': response.json() if response.content else None,
                'tool_id': tool_api['id']
            }
            
            # Log action
            self._log_action(tool_api['id'], input_data, result)
            
            return result
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'tool_id': tool_api['id']
            }
            self._log_action(tool_api['id'], context, error_result)
            return error_result
    
    def _process_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Process headers with secret substitution"""
        processed = {}
        for key, value in headers.items():
            if '{{' in value and '}}' in value:
                # Extract secret key
                secret_key = value.replace('{{secrets.', '').replace('}}', '')
                processed[key] = self.secrets.get(secret_key, value)
            else:
                processed[key] = value
        return processed
    
    def _validate_input(self, context: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input against schema"""
        validated = {}
        for field, field_type in schema.items():
            if field in context:
                validated[field] = context[field]
        return validated
    
    def _log_action(self, tool_id: str, input_data: Dict[str, Any], result: Dict[str, Any]):
        """Log action to file"""
        log_entry = {
            'timestamp': str(datetime.datetime.now()),
            'tool_id': tool_id,
            'input': input_data,
            'result': result
        }
        
        # Создаем относительный путь к логам
        log_file = Path('./tool_api/logs/action_log.json')
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                json.dump(log_entry, f, ensure_ascii=False)
                f.write('\n')
        except Exception as e:
            self.logger.warning(f"Не удалось записать лог: {e}")
    
    def find_tool_for_intent(self, intent: str) -> str:
        """Find appropriate tool for given intent"""
        catalog_file = Path('./tool_api/catalogs/tool_api.catalog.json')
        try:
            with open(catalog_file, encoding='utf-8') as f:
                catalog = json.load(f)
            
            for tool in catalog['tools']:
                if tool['intent'] == intent:
                    return tool['id']
            
            raise ValueError(f"No tool found for intent: {intent}")
        except FileNotFoundError:
            raise ValueError(f"Catalog file not found: {catalog_file}")
        except Exception as e:
            raise ValueError(f"Error reading catalog: {e}")

if __name__ == "__main__":
    connector = UniversalToolConnector()
    print("✅ Universal Tool API Connector loaded successfully")
