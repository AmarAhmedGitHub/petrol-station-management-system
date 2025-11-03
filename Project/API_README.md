# Petrol Pump Management System - Flask API Service

## Overview
This Flask API service provides REST endpoints for external integrations with the Petrol Pump Management System. It includes request logging, database integration, and CORS support.

## Installation & Setup

### Dependencies
Install the required packages:
```bash
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the project root:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=Petrolpump_Management_Enhanced
API_PORT=5000
FLASK_DEBUG=False
```

### Running the API Service
```bash
python api_service.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### GET /welcome
Returns a welcome message with system information.

**Response:**
```json
{
  "message": "Welcome to the Petrol Pump Management System API!",
  "timestamp": "2024-01-15T10:30:00.000000",
  "version": "1.0.0",
  "status": "active"
}
```

**Features:**
- Logs request metadata (method, path, user-agent, IP address)
- Stores logs in the system database
- Returns JSON response with timestamp

### GET /health
Health check endpoint to verify API and database status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000000",
  "database": "connected",
  "service": "Petrol Pump Management API"
}
```

### GET /api/v1/stations
Retrieves all active petrol stations.

**Response:**
```json
{
  "stations": [
    {
      "id": "ST001",
      "name": "محطة الوقود الرئيسية",
      "city": "الرياض",
      "state": "الرياض"
    }
  ],
  "count": 1,
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

## Error Handling

The API includes comprehensive error handling:

- **404 Not Found**: Invalid endpoints
- **405 Method Not Allowed**: Unsupported HTTP methods
- **500 Internal Server Error**: Server-side errors

All errors return JSON responses with timestamps.

## Logging

- **File Logging**: All requests and errors are logged to `api_service.log`
- **Database Logging**: API requests are logged to the `SystemLogs` table
- **Console Logging**: Real-time logging to console

## CORS Support

CORS is enabled for all routes, allowing cross-origin requests from web applications.

## Security Considerations

- Input validation on all endpoints
- Database connection error handling
- Request logging for audit trails
- Environment variable configuration for sensitive data

## Future Enhancements

- Authentication and authorization
- Rate limiting
- API versioning
- Swagger documentation
- Additional endpoints for full CRUD operations
