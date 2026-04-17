import os
from datetime import datetime
from fli.search import SearchFlights
from fli.models import Airport, FlightSearchFilters, FlightSegment, Airline, SortBy, PassengerInfo, TripType

# --- Configuration ---
DESTINATIONS = [Airport.SDQ, Airport.PUJ, Airport.LRM]
OUT_DATE = "2026-07-17"
IN_DATE = "2026-07-21"
AIRLINES = [Airline.AA, Airline.B6] # Monitoring AA and JetBlue

def format_res(res):
    if not res: return "N/A"
    
    best_option = res[0]
    
    # Unpack tuple if it's a round-trip
    if isinstance(best_option, tuple):
        flight = best_option[0]
    else:
        flight = best_option
        
    airline = flight.legs[0].airline.value
    # Removed the airport tag logic entirely since tables are separated
    return f"${flight.price} ({airline})"

def generate_html(mia_data, fll_data):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def build_rows(data_list):
        rows = ""
        for item in data_list:
            rows += f"""
            <tr>
                <td class="dest-cell"><strong>{item['dest']}</strong></td>
                <td class="price-cell">{item['rt']}</td>
                <td class="price-cell">{item['out']}</td>
                <td class="price-cell">{item['ret']}</td>
            </tr>
            """
        return rows

    html_template = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Miami/FLL Flight Board</title>
        <style>
            :root {{ --teal: #008080; --orange: #ff8c00; --bg: #f8fafc; }}
            body {{ font-family: 'Inter', sans-serif; background-color: var(--bg); margin: 0; padding: 20px; color: #1e293b; }}
            .container {{ max-width: 1000px; margin: 0 auto; }}
            header {{ text-align: center; margin-bottom: 30px; }}
            h1 {{ color: var(--teal); margin-bottom: 5px; }}
            h2 {{ color: #334155; margin-top: 40px; margin-bottom: 15px; font-size: 1.2rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 5px; }}
            .table-container {{ background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow-x: auto; border: 1px solid #e2e8f0; margin-bottom: 30px; }}
            table {{ width: 100%; border-collapse: collapse; min-width: 700px; }}
            th {{ background: #f1f5f9; padding: 15px; text-align: left; font-size: 0.8rem; text-transform: uppercase; color: #475569; border-bottom: 2px solid #e2e8f0; }}
            td {{ padding: 15px; border-bottom: 1px solid #f1f5f9; }}
            .dest-cell {{ border-left: 4px solid var(--orange); font-size: 1.1rem; width: 15%; }}
            .price-cell {{ font-weight: 500; width: 28%; }}
            footer {{ text-align:center; margin-top:40px; padding-bottom: 20px; color:#94a3b8; font-size:0.8rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>✈️ South Florida to Caribbean</h1>
                <p><strong>Dates:</strong> {OUT_DATE} to {IN_DATE}</p>
            </header>
            
            <h2>🛫 Departures from Miami (MIA)</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Destination</th>
                            <th>🔄 Round-Trip (Best)</th>
                            <th>🛫 Outbound OW</th>
                            <th>🛬 Return OW</th>
                        </tr>
                    </thead>
                    <tbody>{build_rows(mia_data)}</tbody>
                </table>
            </div>

            <h2>🛫 Departures from Fort Lauderdale (FLL)</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Destination</th>
                            <th>🔄 Round-Trip (Best)</th>
                            <th>🛫 Outbound OW</th>
                            <th>🛬 Return OW</th>
                        </tr>
                    </thead>
                    <tbody>{build_rows(fll_data)}</tbody>
                </table>
            </div>

            <footer>Updated: {now} UTC</footer>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

def fetch_data_for_origin(origin_airport):
    search = SearchFlights()
    data = []
    
    for dest in DESTINATIONS:
        print(f"Checking {origin_airport.name} -> {dest.name}...")
        
        # RT Search
        rt_filters = FlightSearchFilters(trip_type=TripType.ROUND_TRIP, passenger_info=PassengerInfo(adults=1),
            flight_segments=[FlightSegment(departure_airport=[[origin_airport, 0]], arrival_airport=[[dest, 0]], travel_date=OUT_DATE),
                             FlightSegment(departure_airport=[[dest, 0]], arrival_airport=[[origin_airport, 0]], travel_date=IN_DATE)],
            airlines=AIRLINES, sort_by=SortBy.CHEAPEST)
        rt = search.search(rt_filters)
        
        # Outbound OW
        out_filters = FlightSearchFilters(trip_type=TripType.ONE_WAY, passenger_info=PassengerInfo(adults=1),
            flight_segments=[FlightSegment(departure_airport=[[origin_airport, 0]], arrival_airport=[[dest, 0]], travel_date=OUT_DATE)], airlines=AIRLINES)
        out_ow = search.search(out_filters)

        # Return OW
        in_filters = FlightSearchFilters(trip_type=TripType.ONE_WAY, passenger_info=PassengerInfo(adults=1),
            flight_segments=[FlightSegment(departure_airport=[[dest, 0]], arrival_airport=[[origin_airport, 0]], travel_date=IN_DATE)], airlines=AIRLINES)
        in_ow = search.search(in_filters)

        data.append({
            'dest': dest.name,
            'rt': format_res(rt),
            'out': format_res(out_ow),
            'ret': format_res(in_ow)
        })
    return data

def check_flights():
    print("--- Fetching MIA Flights ---")
    mia_data = fetch_data_for_origin(Airport.MIA)
    
    print("--- Fetching FLL Flights ---")
    fll_data = fetch_data_for_origin(Airport.FLL)

    generate_html(mia_data, fll_data)

if __name__ == "__main__":
    check_flights()
