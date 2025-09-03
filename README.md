# Lexi Jagriti API

A FastAPI-based service that integrates with the Jagriti portal to search District Consumer Court (DCDRC) cases in India.

## Overview

This API provides a clean REST interface to search consumer court cases from the e-Jagriti portal (https://e-jagriti.gov.in). It supports various search types including case number, complainant, respondent, advocates, industry type, and judge searches.

## Features

- **Multiple Search Types**: Search by case number, complainant, respondent, advocates, industry type, or judge
- **State & Commission Management**: Retrieve available states and commissions with their internal IDs
- **Clean API Design**: Well-structured REST endpoints with proper error handling
- **Async Implementation**: Built with FastAPI for high performance
- **Input Validation**: Comprehensive request validation and error handling
- **CORS Support**: Cross-origin resource sharing enabled

## API Endpoints

### Metadata Endpoints

- `GET /states` - Get all available states with internal IDs
- `GET /commissions/{state_id}` - Get commissions for a specific state

### Case Search Endpoints

- `POST /cases/by-case-number` - Search by case number
- `POST /cases/by-complainant` - Search by complainant name
- `POST /cases/by-respondent` - Search by respondent name
- `POST /cases/by-complainant-advocate` - Search by complainant advocate
- `POST /cases/by-respondent-advocate` - Search by respondent advocate
- `POST /cases/by-industry-type` - Search by industry type
- `POST /cases/by-judge` - Search by judge name

### Utility Endpoints

- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

## Request Format

All search endpoints accept the following JSON payload:

```json
{
  "state_id": "11290000",
  "commission_id": "15290525",
  "search_value": "Reddy",
  "from_date": "2024-01-01",
  "to_date": "2024-12-31"
}
```

## Response Format

Each case search returns an array of cases:

```json
[
  {
    "case_number": "CC/123/2024",
    "case_stage": "Hearing",
    "filing_date": "2024-08-15",
    "complainant": "John Doe",
    "complainant_advocate": "Adv. Smith",
    "respondent": "XYZ Ltd.",
    "respondent_advocate": "Adv. Jones",
    "document_link": "https://e-jagriti.gov.in/case-document/123"
  }
]
```

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd lexi-jagriti-api
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set environment variables:

```bash
export ENV=development
export DEBUG=true
export HOST=0.0.0.0
export PORT=8000
```

## Running the Application

### Development Mode

```bash
python run.py
# or (production via Docker)
docker build -t lexi:latest .
docker run -e ENV=production -e PORT=8000 -p 8000:8000 lexi:latest
```

## Architecture

### Project Structure

```
lexi/
├── __init__.py          # Package initialization
├── main.py              # FastAPI app and route definitions
├── models.py            # Pydantic models for requests/responses
├── services.py          # Business logic and Jagriti integration
├── config.py            # Configuration settings
└── utils.py             # Utility functions
```

### Key Components

- **Models**: Pydantic models for request/response validation
- **Services**: `JagritiService` handles all interactions with the Jagriti portal
- **Config**: Centralized configuration management
- **Utils**: Helper functions for data processing and validation

## Configuration

The application can be configured using environment variables:

- `ENV`: Environment (development/production)
- `DEBUG`: Enable debug mode (true/false)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)

## Error Handling

The API provides comprehensive error handling with appropriate HTTP status codes:

- `400 Bad Request`: Invalid input parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side errors

Error responses follow a consistent format:

```json
{
  "error": "Bad Request",
  "message": "Invalid search value",
  "status_code": 400
}
```
