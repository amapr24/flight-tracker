import os
import requests
from fli.search import SearchFlights
from fli.models import Airport, FlightSearchFilters, FlightSegment, Airline, SortBy, PassengerInfo

# --- Configuration ---
DEPARTURE_CITY = Airport.MIA
DESTINATIONS = [Airport.SDQ, Airport.PUJ, Airport.LRM]
DEPARTURE_DATE = "2026-07-17" 
AIRLINES = [Airline.AA, Airline.B6] # American and JetBlue
PRICE_THRESHOLD = 500  # Set your max alert price here

def send_pushover(message):
    try:
        data = {
            "token": os.environ["PUSHOVER_TOKEN"],
            "user": os.environ["PUSHOVER_USER"],
            "message": message,
            "title": "Flight Price Alert ✈️"
        }
        r = requests.post("https://api.pushover.net/1/messages.json", data=data)
        r.raise_for_status()
    except Exception as e:
        print(f"Failed to send Pushover: {e}")

def check_flights():
    search = SearchFlights()
    found_deals = []

    for dest in DESTINATIONS:
        print(f"Checking flights to {dest.name}...")
        
        # Corrected Filters with PassengerInfo
        filters = FlightSearchFilters(
            passenger_info=PassengerInfo(adults=1), # This was the missing piece!
            flight_segments=[
                FlightSegment(
                    departure_airport=[[DEPARTURE_CITY, 0]],
                    arrival_airport=[[dest, 0]],
                    travel_date=DEPARTURE_DATE
                )
            ],
            airlines=AIRLINES,
            sort_by=SortBy.CHEAPEST
        )

        try:
            results = search.search(filters)
            if results:
                cheapest = results[0]
                print(f"Found: {dest.name} for ${cheapest.price}")
                
                if cheapest.price <= PRICE_THRESHOLD:
                    # Accessing the airline name from the first leg of the trip
                    airline_name = cheapest.legs[0].airline.value if cheapest.legs else "Unknown"
                    deal_info = f"{dest.name}: ${cheapest.price} ({airline_name})"
                    found_deals.append(deal_info)
        except Exception as e:
            print(f"Error searching for {dest.name}: {e}")

    if found_deals:
        send_pushover("\n".join(found_deals))
        print("Alert sent to Pushover!")
    else:
        print("No flights found under your price threshold.")

if __name__ == "__main__":
    check_flights()
