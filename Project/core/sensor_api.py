import requests
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SensorAPI:
    """Real sensor API integration for PTS2 and ATG devices"""

    def __init__(self, pts2_config: Dict = None, atg_config: Dict = None):
        """
        Initialize sensor API with configurations

        Args:
            pts2_config: PTS2 API configuration
            atg_config: ATG API configuration
        """
        # Load configurations from environment variables
        pts2_url = os.getenv('PTS2_API_URL', 'https://api.pts2-sensor.com/v1/readings')
        pts2_key = os.getenv('PTS2_API_KEY', 'demo_pts2_key_12345')
        pts2_timeout = int(os.getenv('PTS2_TIMEOUT', '30'))

        atg_url = os.getenv('ATG_API_URL', 'https://api.atg-sensor.com/v1/levels')
        atg_key = os.getenv('ATG_API_KEY', 'demo_atg_key_67890')
        atg_timeout = int(os.getenv('ATG_TIMEOUT', '30'))

        # PTS2 configuration from environment
        self.pts2_config = pts2_config or {
            'base_url': pts2_url,
            'api_key': pts2_key,
            'timeout': pts2_timeout,
            'auth_type': 'api_key'
        }

        # ATG configuration from environment
        self.atg_config = atg_config or {
            'base_url': atg_url,
            'api_key': atg_key,
            'timeout': atg_timeout,
            'auth_type': 'api_key'
        }

        # Sensor mappings from environment
        sensor_mappings_str = os.getenv('SENSOR_MAPPINGS', '{}')
        try:
            sensor_mappings = json.loads(sensor_mappings_str)
        except json.JSONDecodeError:
            sensor_mappings = {}

        self.sensor_mappings = {
            'PTS2': sensor_mappings.get('PTS2', {}),
            'ATG': sensor_mappings.get('ATG', {})
        }

    def _make_request(self, url: str, method: str = 'GET', headers: Dict = None,
                     params: Dict = None, data: Dict = None, config: Dict = None) -> Dict:
        """
        Make HTTP request with error handling

        Args:
            url: Request URL
            method: HTTP method
            headers: Request headers
            params: Query parameters
            data: Request body
            config: API configuration

        Returns:
            Response data or error info
        """
        try:
            # Prepare headers with authentication
            request_headers = headers or {}
            if config and config.get('auth_type') == 'api_key':
                request_headers['Authorization'] = f"Bearer {config['api_key']}"
                request_headers['Content-Type'] = 'application/json'

            timeout = config.get('timeout', 30) if config else 30

            logger.info(f"Making {method} request to {url}")

            if method.upper() == 'GET':
                response = requests.get(url, headers=request_headers, params=params, timeout=timeout)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=request_headers, json=data, timeout=timeout)
            else:
                return {'error': f'Unsupported HTTP method: {method}'}

            response.raise_for_status()

            if response.headers.get('content-type', '').startswith('application/json'):
                return response.json()
            else:
                return {'data': response.text}

        except requests.exceptions.Timeout:
            error_msg = f"Request timeout for {url}"
            logger.error(error_msg)
            return {'error': error_msg, 'timeout': True}

        except requests.exceptions.ConnectionError:
            error_msg = f"Connection error for {url}"
            logger.error(error_msg)
            return {'error': error_msg, 'connection_error': True}

        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP error {e.response.status_code} for {url}: {e.response.text}"
            logger.error(error_msg)
            return {'error': error_msg, 'http_error': True, 'status_code': e.response.status_code}

        except Exception as e:
            error_msg = f"Unexpected error for {url}: {str(e)}"
            logger.error(error_msg)
            return {'error': error_msg, 'unexpected_error': True}

    def get_pts2_reading(self, sensor_id: str) -> Optional[float]:
        """
        Get fuel level reading from PTS2 sensor

        Args:
            sensor_id: PTS2 sensor identifier

        Returns:
            Fuel level in liters or None if error
        """
        try:
            url = f"{self.pts2_config['base_url']}/sensors/{sensor_id}/reading"

            response = self._make_request(url, config=self.pts2_config)

            if 'error' in response:
                logger.warning(f"PTS2 sensor {sensor_id} error: {response['error']}")
                return None

            # Parse PTS2 response format
            if 'level_value' in response:
                level = float(response['level_value'])
                timestamp = response.get('timestamp', datetime.now().isoformat())

                logger.info(f"PTS2 sensor {sensor_id}: Level={level}L at {timestamp}")
                return level

            logger.warning(f"Invalid PTS2 response format for sensor {sensor_id}")
            return None

        except Exception as e:
            logger.error(f"Error getting PTS2 reading for sensor {sensor_id}: {str(e)}")
            return None

    def get_atg_reading(self, sensor_id: str) -> Optional[float]:
        """
        Get fuel level reading from ATG sensor

        Args:
            sensor_id: ATG sensor identifier

        Returns:
            Fuel level in liters or None if error
        """
        try:
            url = f"{self.atg_config['base_url']}/sensors/{sensor_id}/level"

            response = self._make_request(url, config=self.atg_config)

            if 'error' in response:
                logger.warning(f"ATG sensor {sensor_id} error: {response['error']}")
                return None

            # Parse ATG response format
            if 'level_value' in response:
                level = float(response['level_value'])
                timestamp = response.get('timestamp', datetime.now().isoformat())

                logger.info(f"ATG sensor {sensor_id}: Level={level}L at {timestamp}")
                return level

            logger.warning(f"Invalid ATG response format for sensor {sensor_id}")
            return None

        except Exception as e:
            logger.error(f"Error getting ATG reading for sensor {sensor_id}: {str(e)}")
            return None

    def get_sensor_reading(self, sensor_type: str, sensor_id: str) -> Optional[float]:
        """
        Get sensor reading based on type

        Args:
            sensor_type: 'PTS2' or 'ATG'
            sensor_id: Sensor identifier

        Returns:
            Fuel level in liters or None if error
        """
        if sensor_type.upper() == 'PTS2':
            return self.get_pts2_reading(sensor_id)
        elif sensor_type.upper() == 'ATG':
            return self.get_atg_reading(sensor_id)
        else:
            logger.error(f"Unknown sensor type: {sensor_type}")
            return None

    def update_sensor_mappings(self, mappings: Dict[str, Dict[str, str]]):
        """
        Update sensor to tank/pump mappings

        Args:
            mappings: {'PTS2': {sensor_id: tank_id}, 'ATG': {sensor_id: tank_id}}
        """
        self.sensor_mappings.update(mappings)
        logger.info(f"Updated sensor mappings: {mappings}")

    def get_all_sensor_readings(self) -> Dict[str, float]:
        """
        Get readings from all configured sensors

        Returns:
            Dict of tank_id -> level_value
        """
        readings = {}

        for sensor_type, sensor_map in self.sensor_mappings.items():
            for sensor_id, tank_id in sensor_map.items():
                level = self.get_sensor_reading(sensor_type, sensor_id)
                if level is not None:
                    readings[tank_id] = level
                    logger.info(f"Got reading for tank {tank_id}: {level}L from {sensor_type} sensor {sensor_id}")
                else:
                    logger.warning(f"Failed to get reading for tank {tank_id} from {sensor_type} sensor {sensor_id}")

        return readings

    def test_connection(self, sensor_type: str) -> bool:
        """
        Test connection to sensor API

        Args:
            sensor_type: 'PTS2' or 'ATG'

        Returns:
            True if connection successful
        """
        try:
            if sensor_type.upper() == 'PTS2':
                url = f"{self.pts2_config['base_url']}/health"
                response = self._make_request(url, config=self.pts2_config)
            elif sensor_type.upper() == 'ATG':
                url = f"{self.atg_config['base_url']}/status"
                response = self._make_request(url, config=self.atg_config)
            else:
                return False

            return 'error' not in response

        except Exception as e:
            logger.error(f"Connection test failed for {sensor_type}: {str(e)}")
            return False

# Global sensor API instance
sensor_api = SensorAPI()

def get_sensor_api() -> SensorAPI:
    """Get global sensor API instance"""
    return sensor_api

def initialize_sensor_api(pts2_config: Dict = None, atg_config: Dict = None,
                         sensor_mappings: Dict = None):
    """
    Initialize global sensor API instance

    Args:
        pts2_config: PTS2 API configuration
        atg_config: ATG API configuration
        sensor_mappings: Sensor to tank mappings
    """
    global sensor_api
    sensor_api = SensorAPI(pts2_config, atg_config)

    if sensor_mappings:
        sensor_api.update_sensor_mappings(sensor_mappings)

    logger.info("Sensor API initialized successfully")

# For testing
if __name__ == "__main__":
    # Test connections
    pts2_ok = sensor_api.test_connection('PTS2')
    atg_ok = sensor_api.test_connection('ATG')

    print(f"PTS2 connection: {'OK' if pts2_ok else 'FAILED'}")
    print(f"ATG connection: {'OK' if atg_ok else 'FAILED'}")
