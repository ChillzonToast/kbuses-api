# KBuses API

A FastAPI-based web scraping API for KBuses.in, providing bus information and schedules for Kerala bus services.

## Features

- Search buses between stations
- Get detailed bus information including routes and timings
- Station name autocomplete
- Asynchronous data fetching for better performance

## API Endpoints

### 1. Search Buses
```
GET /buses/{from_station}/{to_station}
```
Returns a list of buses between two stations.

**Response Format:**
```json
{
    "count": 10,
    "buses": [
        {
            "name": "Bus Name",
            "type": "Bus Type",
            "from_station": "Source Station",
            "to_station": "Destination Station",
            "start_time": "HH:MM",
            "bus_url": "http://localhost:8000/bus?url=...",
            "duration": "Duration"
        }
    ]
}
```

### 2. Get Bus Details
```
GET /bus?url={url}
```
Returns detailed information about a specific bus including all stops and timings.

**Response Format:**
```json
{
    "bus_name": "Bus Name",
    "bus_type": "Bus Type",
    "from_station": "Source Station",
    "to_station": "Destination Station",
    "stations": [
        {
            "name": "Station Name",
            "time": "HH:MM"
        }
    ]
}
```

### 3. Station Search
```
GET /station_query?q={query}
```
Returns a list of matching stations for autocomplete functionality.

**Response Format:**
```json
[
    {
        "response":"true",
        "message":[
            {
                "label":"Sultan Bathery, Sultan Bathery < Wayanad >",
                "value":"Sultan Bathery"
            },
            {
                "label":"Sultanbathery, Sultan Bathery, Kerala",
                "value":"Sultanbathery"
            }
        ]
    }
]
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd kbuses-api
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start the server:
```bash
uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## Dependencies

- FastAPI: Web framework
- Uvicorn: ASGI server
- Requests: HTTP client
- BeautifulSoup4: HTML parsing
- aiohttp: Asynchronous HTTP client

## Notes

- The API uses web scraping to fetch data from KBuses.in
- All times are converted to 24-hour format
- Station search requires at least 3 characters
- Bus URLs are proxied through the API for security

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).
