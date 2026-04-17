import os
import requests
from datetime import datetime
from fli.search import SearchFlights
from fli.models import Airport, FlightSearchFilters, FlightSegment, Airline, SortBy, PassengerInfo, TripType

# --- Configuration ---
ORIGIN = Airport.MIA
DESTINATIONS = [Airport.SDQ, Airport.PUJ, Airport.LRM]
OUT_DATE = "2026-07-17"
IN_DATE = "2026-07-21"
AIRLINES = [Airline.AA, Airline.B6]

def generate_html(data_list):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Generate table rows
    rows_html = ""
    for item in data_list:
        rows_html += f"""
        <tr>
            <td class="dest-cell"><strong>{item['dest']}</strong><br><small>MIA ⇄ {item['dest']}</small></td>
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
        <title>Miami Flight Board</title>
        <style>
            :root {{ --teal: #008080; --orange: #ff8c00; --bg: #f8fafc; }}
            body {{ 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; 
                background-color: var(--bg); 
                margin: 0; padding: 20px; color: #1e293b; 
            }}
            .container {{ max-width: 900px; margin: 0 auto; }}
            header {{ text-align: center; margin-bottom: 30px; }}
            h1 {{ color: var(--teal); margin-bottom: 5px; font-size: 2rem; }}
            .last-updated {{ color: #64748b; font-size: 0.85rem; }}
            
            /* Table Styling */
            .table-container {{ 
                background: white; 
                border-radius: 12px; 
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); 
                overflow-x: auto; /* For mobile responsiveness */
                border: 1px solid #e2e8f0;
            }}
            table {{ 
                width: 100%; 
                border-collapse: collapse; 
                text-align: left; 
                min-width: 600px; /* Ensures columns don't get too squished */
            }}
            th {{ 
                background-color: #f1f5f9; 
                padding: 15px; 
                font-size: 0.85rem; 
                text-transform: uppercase; 
                letter-spacing: 0.05em; 
                color: #475569;
                border-bottom: 2px solid #e2e8f0;
            }}
            td {{ padding: 15px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }}
            tr:hover {{ background-color: #f8fafc; }}
            
            .dest-cell {{ border-left: 4px solid var(--orange); }}
            .price-cell {{ font-weight: 500; color: #0f172a; }}
            
            small {{ color: #94a3b8; font-size: 0.75rem; }}
            footer {{ text-align: center; margin-top: 30px; color: #94a3b8; font-size: 0.8rem; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>✈️ Caribbean Flight Monitor</h1>
                <p class="last-updated">Last Refresh: {now} UTC</p>
                <p><strong>Travel Dates:</strong> {OUT_DATE} to {IN_DATE}</p>
            </header>
            
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Destination</th>
                            <th>🔄 Round-Trip</th>
                            <th>🛫 Outbound (MIA Out)</th>
                            <th>🛬 Return (MIA In)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows_html}
                    </tbody>
                </table>
            </div>
            
            <footer>
                Built with fli-library • Hosted on Vercel • Updates every 6 hours
            </footer>
        </div>
    </body>
    </html>
    """
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)

def check_flights():
    search = SearchFlights()
    data_for_web = []

    for dest in DESTINATIONS:
        # Search Round Trip
        rt_filters = FlightSearchFilters(trip_type=TripType.ROUND_TRIP, passenger_info=PassengerInfo(adults=1),
            flight_segments=[FlightSegment(departure_airport=[[ORIGIN, 0]], arrival_airport=[[dest, 0]], travel_date=OUT_DATE),
                             FlightSegment(departure_airport=[[dest, 0]], arrival_airport=[[ORIGIN, 0]], travel_date=IN_DATE)],
            airlines=AIRLINES, sort_by=SortBy.CHEAPEST)
        rt = search.search(rt_filters)
        
        # Search One Ways
        out_filters = FlightSearchFilters(trip_type=TripType.ONE_WAY, passenger_info=PassengerInfo(adults=1),
            flight_segments=[FlightSegment(departure_airport=[[ORIGIN, 0]], arrival_airport=[[dest, 0]], travel_date=OUT_DATE)], airlines=AIRLINES)
        out_ow = search.search(out_filters)

        in_filters = FlightSearchFilters(trip_type=TripType.ONE_WAY, passenger_info=PassengerInfo(adults=1),
            flight_segments=[FlightSegment(departure_airport=[[dest, 0]], arrival_airport=[[ORIGIN, 0]], travel_date=IN_DATE)], airlines=AIRLINES)
        in_ow = search.search(in_filters)

        data_for_web.append({
            'dest': dest.name,
            'rt': f"${rt[0][0].price} ({rt[0][0].legs[0].airline.value})" if rt else "N/A",
            'out': f"${out_ow[0].price} ({out_ow[0].legs[0].airline.value})" if out_ow else "N/A",
            'ret': f"${in_ow[0].price} ({in_ow[0].legs[0].airline.value})" if in_ow else "N/A"
        })

    generate_html(data_for_web)

if __name__ == "__main__":
    check_flights()
