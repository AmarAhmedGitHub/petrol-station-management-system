"""
Flask API Service for Petrol Pump Management System
Provides REST API endpoints for external integrations and monitoring
"""

import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
from contextlib import contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('api_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Flask app configuration
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration (same as main app)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "Petrolpump_Management_Enhanced"),
    "charset": "utf8mb4"
}

@contextmanager
def get_db_connection():
    """Database connection context manager"""
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        yield conn
    except pymysql.Error as err:
        logger.error(f"Database connection error: {err}")
        raise
    finally:
        if conn:
            conn.close()

def log_api_request(method, path, user_agent=None, ip_address=None):
    """Log API request details"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO SystemLogs
                         (Station_ID, Event_Type, Description, Severity)
                         VALUES (%s, %s, %s, %s)''',
                      (None, 'API_REQUEST', f'{method} {path} - User-Agent: {user_agent} - IP: {ip_address}', 'info'))
            conn.commit()
            logger.info(f"API request logged: {method} {path}")
    except Exception as e:
        logger.error(f"Failed to log API request: {e}")

@app.route('/welcome', methods=['GET'])
def welcome():
    """
    Welcome endpoint that logs request metadata and returns JSON response
    """
    try:
        # Log request metadata
        method = request.method
        path = request.path
        user_agent = request.headers.get('User-Agent', 'Unknown')
        ip_address = request.remote_addr

        logger.info(f"Request received: {method} {path} from {ip_address}")

        # Log to database if available
        try:
            log_api_request(method, path, user_agent, ip_address)
        except Exception as db_error:
            logger.warning(f"Database logging failed: {db_error}")

        # Return welcome message
        response = {
            "message": "Welcome to the Petrol Pump Management System API!",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "status": "active"
        }

        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in welcome endpoint: {e}")
        return jsonify({
            "error": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify API status
    """
    try:
        # Test database connection
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT 1")
            db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.warning(f"Database health check failed: {e}")

    response = {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "database": db_status,
        "service": "Petrol Pump Management API"
    }

    status_code = 200 if db_status == "connected" else 503
    return jsonify(response), status_code

@app.route('/api/v1/stations', methods=['GET'])
def get_stations():
    """
    Get all active petrol stations
    """
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT Station_ID, Station_Name, City, State FROM PetrolStations WHERE Is_Active = TRUE')
            stations = c.fetchall()

        station_list = []
        for station in stations:
            station_list.append({
                "id": station[0],
                "name": station[1],
                "city": station[2],
                "state": station[3]
            })

        return jsonify({
            "stations": station_list,
            "count": len(station_list),
            "timestamp": datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"Error retrieving stations: {e}")
        return jsonify({
            "error": "Failed to retrieve stations",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "message": f"The requested URL {request.path} was not found on this server",
        "timestamp": datetime.now().isoformat()
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        "error": "Method not allowed",
        "message": f"The method {request.method} is not allowed for {request.path}",
        "timestamp": datetime.now().isoformat()
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal server error",
        "timestamp": datetime.now().isoformat()
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    logger.info(f"Starting Flask API service on port {port}")
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug,
        threaded=True
    )
