from fastapi import FastAPI, HTTPException
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
import uvicorn
import aiohttp
import asyncio
import json
app = FastAPI(
    title="KBuses API",
    description="API for KBuses service",
    version="1.0.0"
)

class Bus():
    def __init__(self):
        self.name = None
        self.type = None
        self.from_station = None
        self.to_station = None
        self.start_time = None
        self.bus_url = None
        self.duration = None
    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "from_station": self.from_station,
            "to_station": self.to_station,
            "start_time": self.start_time,
            "bus_url": self.bus_url,
            "duration": self.duration
        }
    
def convert_time(time_str):
    # Convert 12:30 AM to 00:30
    t1 = int(time_str.split(":")[0])
    t2 = int(time_str.split(":")[1].split(" ")[0])
    t1 = t1 % 12
    if "pm" in time_str:
        t1 += 12
    return f"{t1:02d}:{t2:02d}"

async def fetch_buses_from_page(session, from_station: str, to_station: str, page: int) -> List[Bus]:
    url = f"https://www.kbuses.in/v3/Find/source/{from_station}/destination/{to_station}/type/all/timing/all?page={page}"
    async with session.get(url) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        buses_data = soup.find_all('section', id='bulllist')[0].find_all('div', class_='row')
        buses = []
        for bus in buses_data:
            bus_obj = Bus()
            bus_obj.name = bus.find('span', id='bus_name').text.strip()
            bus_obj.type = bus.find('div', class_='bustype').text.strip()
            bus_obj.from_station = bus.find_all('span', class_='card-text')[0].text.strip()
            bus_obj.to_station = bus.find_all('span', class_='card-text')[1].text.strip()
            bus_obj.start_time = convert_time(bus.find('span', id='bus_time').text.strip())
            bus_obj.bus_url = "http://localhost:8000/bus?url=" + bus.find('a', class_='btn')['href']
            try:
                bus_obj.duration = bus.find_all('span', class_='smalltxt')[0].text.strip()
            except:
                bus_obj.duration = None


            buses.append(bus_obj)
        return buses

@app.get("/")
async def root():
    return {"message": "Welcome to KBuses API"}

@app.get("/station_query")
async def station_query(q: str):
    if len(q) > 2:
        url = f"https://www.kbuses.in/places?term={q}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                text_R = await response.text()
                return json.loads(text_R)
    else:
        return {"message": "Query must be at least 3 characters long"}

@app.get("/buses/{from_station}/{to_station}")
async def get_bus(from_station: str, to_station: str):
    # Get first page to determine total number of pages
    response = requests.get(f"https://www.kbuses.in/v3/Find/source/{from_station}/destination/{to_station}/type/all/timing/all?page=1")
    soup = BeautifulSoup(response.text, 'html.parser')
    no_of_pages = int(soup.find_all('ul', class_='pagination')[0].find_all('li')[-1].find('a')['href'].split('page=')[-1])
    
    # Get buses from first page
    first_page_buses = []
    buses_data = soup.find_all('section', id='bulllist')[0].find_all('div', class_='row')
    for bus in buses_data:
        bus_obj = Bus()
        bus_obj.name = bus.find('span', id='bus_name').text.strip()
        bus_obj.type = bus.find('div', class_='bustype').text.strip()
        bus_obj.from_station = bus.find_all('span', class_='card-text')[0].text.strip()
        bus_obj.to_station = bus.find_all('span', class_='card-text')[1].text.strip()
        bus_obj.start_time = convert_time(bus.find('span', id='bus_time').text.strip())
        bus_obj.bus_url = "http://localhost:8000/bus?url=" + bus.find('a', class_='btn')['href']
        try:
            bus_obj.duration = bus.find_all('span', class_='smalltxt')[0].text.strip()
        except:
            bus_obj.duration = None


        first_page_buses.append(bus_obj)

    # Fetch remaining pages asynchronously
    async with aiohttp.ClientSession() as session:
        tasks = []
        for page_number in range(2, no_of_pages + 1):
            tasks.append(fetch_buses_from_page(session, from_station, to_station, page_number))
        
        # Wait for all tasks to complete
        remaining_buses = await asyncio.gather(*tasks)
        
        # Combine all buses
        all_buses = first_page_buses + [bus for page_buses in remaining_buses for bus in page_buses]
        
        return {"count": len(all_buses), "buses": [bus.to_dict() for bus in all_buses]}

@app.get("/bus")
async def get_bus_from_url(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    indibus = soup.find_all('div', class_='indibus')[0].find_all('span')
    bus_name = indibus[0].text.strip()
    bus_type = indibus[2].text.strip()
    from_station = indibus[1].text.split("-")[0].strip()
    to_station = indibus[1].text.split("-")[1].strip()

    stations = []
    tds = soup.find("tbody").find_all("td")
    for i in range(0, len(tds), 2):
        stations.append({"name": tds[i].text.strip(), "time": convert_time(tds[i+1].text.strip())})

    return {"bus_name": bus_name, "bus_type": bus_type, "from_station": from_station, "to_station": to_station, "stations": stations}   

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)