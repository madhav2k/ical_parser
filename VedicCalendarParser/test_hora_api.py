import http.client
import json
from datetime import datetime

def test_hora_api():
    # API parameters
    api_key = "1c998321-4363-5535-91a6-2331c3c2c012"
    base_url = "api.vedicastroapi.com"
    
    # Test parameters
    date = "05/04/2025"  # DD/MM/YYYY format
    lat = "37.33939"     # San Jose latitude
    lon = "-121.89496"   # San Jose longitude
    tz = "-7"           # Pacific timezone
    lang = "en"
    
    try:
        # Create connection
        conn = http.client.HTTPSConnection(base_url)
        
        # Construct the endpoint
        endpoint = f"/v3-json/panchang/hora-muhurta?api_key={api_key}&date={date}&tz={tz}&lat={lat}&lon={lon}&lang={lang}"
        
        print(f"Making request to: {endpoint}")
        
        # Make the request
        conn.request("GET", endpoint)
        response = conn.getresponse()
        
        # Read and decode the response
        data = response.read().decode("utf-8")
        
        # Parse JSON response
        json_data = json.loads(data)
        
        # Print the response
        print("\nResponse status:", response.status)
        print("Response headers:", response.getheaders())
        print("\nResponse content:")
        print(json.dumps(json_data, indent=2))
        
        # Close the connection
        conn.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_hora_api() 