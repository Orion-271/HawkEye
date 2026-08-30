import requests
import time
import math


API_URL = "https://api.worldpop.org/v2"


def get_population(lat, lon, size_m=100, year=2025):
    """
    Get estimated population and population density
    around a latitude/longitude coordinate.

    Parameters:
        lat (float): Latitude
        lon (float): Longitude
        size_m (float): Width and height of query area in metres
        year (int): WorldPop dataset year

    Returns:
        population (float)
        density (float)
    """

    # Convert metres to degrees
    lat_offset = (size_m / 2) / 111320

    lon_offset = (size_m / 2) / (
        111320 * math.cos(math.radians(lat))
    )

    # Create square around coordinate
    polygon = [
        [lon - lon_offset, lat - lat_offset],
        [lon + lon_offset, lat - lat_offset],
        [lon + lon_offset, lat + lat_offset],
        [lon - lon_offset, lat + lat_offset],
        [lon - lon_offset, lat - lat_offset]
    ]

    payload = {
        "geojson": {
            "type": "Polygon",
            "coordinates": [polygon]
        },
        "year": year,
        "resolution": "100m"
    }

    # Send request to WorldPop
    response = requests.post(
        f"{API_URL}/population",
        json=payload
    )

    response.raise_for_status()

    data = response.json()

    task_id = data["task_id"]

    # Wait for WorldPop
    while True:

        result_response = requests.get(
            f"{API_URL}/tasks/{task_id}"
        )

        result_response.raise_for_status()

        result = result_response.json()

        if result["status"] == "success":

            population = result["result"]["total_population"]
            density = result["result"]["population_density"]

            return population, density

        elif result["status"] == "failure":

            raise Exception(
                result.get(
                    "error",
                    "WorldPop request failed"
                )
            )

        time.sleep(2)


def estimate_building_population(
    lat,
    lon,
    building_area_m2
):
    """
    Estimate population exposure for a building.
    """

    # Get local population density
    _, density = get_population(
        lat,
        lon,
        size_m=100
    )

    # Convert m² to km²
    building_area_km2 = building_area_m2 / 1_000_000

    # Estimate population exposure
    estimated_population = (
        density * building_area_km2
    )

    return estimated_population, density


def analyze_building(building):
    """
    Analyze one building.

    Expected input:

    {
        "id": "B001",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "area": 400
    }
    """

    building_id = building["id"]
    lat = building["latitude"]
    lon = building["longitude"]
    area = building["area"]

    population, density = estimate_building_population(
        lat,
        lon,
        area
    )

    building["estimated_population"] = population
    building["population_density"] = density

    return building