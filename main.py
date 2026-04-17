import os
import requests
from datetime import datetime
from fli.search import SearchFlights
from fli.models import Airport, FlightSearchFilters, FlightSegment, Airline, SortBy, PassengerInfo, TripType

# --- Configuration ---
# Including both Miami and Fort Lauderdale
ORIGINS = [[Airport.MIA, 0], [Airport.FLL, 0]] 
DESTINATIONS = [Airport.SDQ, Airport.PUJ, Airport.LRM]
OUT_DATE = "2026-07-17"
IN_DATE = "2026-07-21"
AIRLINES = [Airline.AA, Airline.B6]

def generate_html(data_list):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows_html = ""
    for item in data_list:
        rows_html += f"""
        <tr>
            <td class="dest-cell"><strong>{item['dest']}</strong></td>
            <td class="price-cell">{item['rt']}</td>
            <td class="price-cell">{item['out']}</td>
            <td class="price-cell">{item['ret']}</td>
        </tr>
        """

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
            .table-container {{ background: white; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow-x: auto; border: 1px solid #e2e8f0; }}
            table {{ width: 100%; border-collapse: collapse; min-width: 700px; }}
            th {{ background: #f1f5f9; padding: 15px; font-size: 0.8rem; text-transform: uppercase; color: #475569; border-bottom: 2px solid #e2e8f0; }}
            td {{ padding: 15px; border-bottom: 1px solid #f1f5f9; }}
            .dest-cell {{ border-left: 4px solid var(--orange); font-size: 1.1rem; }}
            .price-cell {{ font-weight: 500; }}
            .airport-tag {{ font-size: 0.7rem; background: #e2e8f0; padding: 2px 6px; border-radius: 4px; margin-left: 5px; color: #475569; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>✈️ MIA & FLL to CDC</h1>
                <p><strong>Dates:</strong> {OUT_DATE} to {IN_DATE}</p>
                <p style="font-size: 0.8rem; color: #64748b;">Monitoring American (MIA) and JetBlue (FLL)</p>
            </header>
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
                    <tbody>{rows_html}</tbody>
                </table>
            </div>
            <footer style="text-align:center; margin-top:20px; color:#94a3b8; font-size:0.8rem;">Updated: {now} UTC</footer>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

def format_res(res):
    if not res: return "N/A"
    # Handling list vs tuple (RT vs OW)
    flight = res[0] if isinstance(res, list) else res[0]
    airline = flight.legs[0].airline.value
    # Get departure airport of the first leg
    apt = flight.legs[0].departure_airport.name
    return f"${flight.price} ({airline}) <span class='airport-tag'>{apt}</span>"

def check_flights():
    search = SearchFlights()
    data_for_web = []

    for dest in DESTINATIONS:
        print(f"Checking {dest.name}...")
        
        # RT Search (MIA/FLL -> Dest -> MIA/FLL)
        rt_filters = FlightSearchFilters(trip_type=TripType.ROUND_TRIP, passenger_info=PassengerInfo(adults=1),
            flight_segments=[FlightSegment(departure_airport=ORIGINS, arrival_airport=[[dest, 0]], travel_date=OUT_DATE),
                             FlightSegment(departure_airport=[[dest, 0]], arrival_airport=ORIGINS, travel_date=IN_DATE)],
            airlines=AIRLINES, sort_by=SortBy.CHEAPEST)
        rt = search.search(rt_filters)
        
        # Outbound OW
        out_filters = FlightSearchFilters(trip_type=TripType.ONE_WAY, passenger_info=PassengerInfo(adults=1),
            flight_segments=[FlightSegment(departure_airport=ORIGINS, arrival_airport=[[dest, 0]], travel_date=OUT_DATE)], airlines=AIRLINES)
        out_ow = search.search(out_filters)

        # Return OW
        in_filters = FlightSearchFilters(trip_type=TripType.ONE_WAY, passenger_info=PassengerInfo(adults=1),
            flight_segments=[FlightSegment(departure_airport=[[dest, 0]], arrival_airport=ORIGINS, travel_date=IN_DATE)], airlines=AIRLINES)
        in_ow = search.search(in_filters)

        data_for_web.append({
            'dest': dest.name,
            'rt': format_res(rt),
            'out': format_res(out_ow),
            'ret': format_res(in_ow)
        })

    generate_html(data_for_web)

if __name__ == "__main__":
    check_flights()
