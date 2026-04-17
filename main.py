import os
import requests
from fli.search import SearchFlights
from fli.models import Airport, FlightSearchFilters, FlightSegment, Airline, SortBy

# --- Configuration ---
DEPARTURE_CITY = Airport.MIA
DESTINATIONS = [Airport.SDQ, Airport.PUJ, Airport.LRM]
DATES = ["2026-07-17"] # Departure date
RETURN_DATE = "2026-07-21"
AIRLINES = [Airline.AA, Airline.B6] # American and JetBlue
PRICE_THRESHOLD = 450  # Only notify if flight is below this price

def send_pushover(message):
    data = {
        "token": os.environ["PUSHOVER_TOKEN"],
        "user": os.environ["PUSHOVER_USER"],
        "message": message,
        "title": "Flight Price Alert ✈️"
    }
    requests.post("https://api.pushover.net/1/messages.json", data=data)

def check_flights():
    search = SearchFlights()
    found_deals = []

    for dest in DESTINATIONS:
        filters = FlightSearchFilters(
            flight_segments=[
                FlightSegment(
                    departure_airport=[[DEPARTURE_CITY, 0]],
                    arrival_airport=[[dest, 0]],
                    travel_date=DATES[0]
                )
            ],
            airlines=AIRLINES,
            sort_by=SortBy.CHEAPEST
        )

        results = search.search(filters)
        if results:
            cheapest = results[0]
            if cheapest.price <= PRICE_THRESHOLD:
                deal_info = f"{dest.name}: ${cheapest.price} ({cheapest.legs[0].airline.value})"
                found_deals.append(deal_info)

    if found_deals:
        send_pushover("\n".join(found_deals))
    else:
        print("No flights found under threshold.")

if __name__ == "__main__":
    check_flights()
