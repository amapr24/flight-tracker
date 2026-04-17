import os
import requests
from fli.search import SearchFlights
from fli.models import Airport, FlightSearchFilters, FlightSegment, Airline, SortBy, PassengerInfo, TripType

# --- Configuration ---
ORIGIN = Airport.MIA
DESTINATIONS = [Airport.SDQ, Airport.PUJ, Airport.LRM]
OUT_DATE = "2026-07-17"
IN_DATE = "2026-07-21"
AIRLINES = [Airline.AA, Airline.B6]
PRICE_THRESHOLD = 550 

def send_pushover(message):
    try:
        data = {
            "token": os.environ["PUSHOVER_TOKEN"],
            "user": os.environ["PUSHOVER_USER"],
            "message": message,
            "title": "Flight Price Alert ✈️"
        }
        requests.post("https://api.pushover.net/1/messages.json", data=data).raise_for_status()
    except Exception as e:
        print(f"Failed to send Pushover: {e}")

def get_best_flight(search_obj, filters):
    try:
        results = search_obj.search(filters)
        return results[0] if results else None
    except:
        return None

def check_flights():
    search = SearchFlights()
    found_deals = []

    for dest in DESTINATIONS:
        print(f"🔍 Analyzing MIA <-> {dest.name}...")

        # 1. Check Official Round Trip
        rt_filters = FlightSearchFilters(
            trip_type=TripType.ROUND_TRIP,
            passenger_info=PassengerInfo(adults=1),
            flight_segments=[
                FlightSegment(departure_airport=[[ORIGIN, 0]], arrival_airport=[[dest, 0]], travel_date=OUT_DATE),
                FlightSegment(departure_airport=[[dest, 0]], arrival_airport=[[ORIGIN, 0]], travel_date=IN_DATE)
            ],
            airlines=AIRLINES,
            sort_by=SortBy.CHEAPEST
        )
        rt_result = get_best_flight(search, rt_filters)
        
        # 2. Check One Way Out
        out_filters = FlightSearchFilters(
            trip_type=TripType.ONE_WAY,
            passenger_info=PassengerInfo(adults=1),
            flight_segments=[FlightSegment(departure_airport=[[ORIGIN, 0]], arrival_airport=[[dest, 0]], travel_date=OUT_DATE)],
            airlines=AIRLINES
        )
        out_one_way = get_best_flight(search, out_filters)

        # 3. Check One Way Back
        in_filters = FlightSearchFilters(
            trip_type=TripType.ONE_WAY,
            passenger_info=PassengerInfo(adults=1),
            flight_segments=[FlightSegment(departure_airport=[[dest, 0]], arrival_airport=[[ORIGIN, 0]], travel_date=IN_DATE)],
            airlines=AIRLINES
        )
        in_one_way = get_best_flight(search, in_filters)

        # Comparison Logic
        best_price = float('inf')
        details = ""

        # Option A: Round Trip
        if rt_result:
            # Note: For RT, fli returns a tuple; the price is usually in the first element
            rt_price = rt_result[0].price
            if rt_price < best_price:
                best_price = rt_price
                details = f"🔄 Round-Trip ({rt_result[0].legs[0].airline.value})"

        # Option B: Mix & Match One-Ways
        if out_one_way and in_one_way:
            mix_price = out_one_way.price + in_one_way.price
            if mix_price < best_price:
                best_price = mix_price
                details = f"🔀 Mix: {out_one_way.legs[0].airline.value} + {in_one_way.legs[0].airline.value}"

        # If we found a viable price under the threshold
        if best_price <= PRICE_THRESHOLD:
            msg = (f"📍 MIA to {dest.name}\n"
                   f"📅 {OUT_DATE} to {IN_DATE}\n"
                   f"💰 ${best_price} | {details}")
            found_deals.append(msg)

    if found_deals:
        send_pushover("\n\n".join(found_deals))
    else:
        print("No flights found under threshold.")

if __name__ == "__main__":
    check_flights()
