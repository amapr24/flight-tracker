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

def send_pushover(message):
    try:
        data = {
            "token": os.environ["PUSHOVER_TOKEN"],
            "user": os.environ["PUSHOVER_USER"],
            "message": message,
            "title": "Flight Monitoring Report ✈️"
        }
        requests.post("https://api.pushover.net/1/messages.json", data=data).raise_for_status()
    except Exception as e:
        print(f"Pushover Error: {e}")

def get_cheapest(search_obj, filters):
    try:
        results = search_obj.search(filters)
        return results[0] if results else None
    except Exception as e:
        print(f"Search Error: {e}")
        return None

def check_flights():
    search = SearchFlights()
    reports = []

    for dest in DESTINATIONS:
        print(f"Checking {dest.name}...")
        
        # 1. Official Round Trip
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
        rt = get_cheapest(search, rt_filters)
        # Note: RT returns a tuple (outbound, return). We take price from first leg.
        rt_price = f"${rt[0].price} ({rt[0].legs[0].airline.value})" if rt else "N/A"

        # 2. One Way Out (MIA -> Dest)
        ow_out_filters = FlightSearchFilters(
            trip_type=TripType.ONE_WAY,
            passenger_info=PassengerInfo(adults=1),
            flight_segments=[FlightSegment(departure_airport=[[ORIGIN, 0]], arrival_airport=[[dest, 0]], travel_date=OUT_DATE)],
            airlines=AIRLINES
        )
        outbound = get_cheapest(search, ow_out_filters)
        out_price = f"${outbound.price} ({outbound.legs[0].airline.value})" if outbound else "N/A"

        # 3. One Way Back (Dest -> MIA)
        ow_in_filters = FlightSearchFilters(
            trip_type=TripType.ONE_WAY,
            passenger_info=PassengerInfo(adults=1),
            flight_segments=[FlightSegment(departure_airport=[[dest, 0]], arrival_airport=[[ORIGIN, 0]], travel_date=IN_DATE)],
            airlines=AIRLINES
        )
        inbound = get_cheapest(search, ow_in_filters)
        in_price = f"${inbound.price} ({inbound.legs[0].airline.value})" if inbound else "N/A"

        # Construct the report for this destination
        report = (
            f"📍 MIA ⇄ {dest.name}\n"
            f"📅 {OUT_DATE} to {IN_DATE}\n"
            f"──────────────────\n"
            f"🔄 Round-Trip: {rt_price}\n"
            f"🛫 Outbound OW: {out_price}\n"
            f"🛬 Return OW:   {in_price}"
        )
        reports.append(report)

    if reports:
        send_pushover("\n\n".join(reports))
        print("Success: Report sent.")

if __name__ == "__main__":
    check_flights()
