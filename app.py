# %%
# Install required packages before running the code
# pip install -r requirements.txt

# %%
# Import necessary libraries
from smolagents import CodeAgent, HfApiModel, load_tool, tool
from Gradio_UI import GradioUI
from typing import Any, Optional, Dict
import datetime
import requests
import json
import pytz
import yaml
import os
import dotenv
import sys
sys.path.append('./tools')
from final_answer import FinalAnswerTool
from today import CurrentDateTool

# %%
# Set the os environment variable for the Huggingface API token
dotenv.load_dotenv() 
os.environ["HF_API_TOKEN"] = os.getenv("HF_API_TOKEN")

# %%
# Define the get_flight_information tool
@tool
def get_flight_information(
    fromId: str, 
    toId: str, 
    departDate: str, 
    returnDate: Optional[str] = None, 
    adults: Optional[int] = 1,
    children: Optional[str] = None,
    sort: Optional[str] = "BEST",
    cabinClass: Optional[str] = "ECONOMY",
    currency_code: Optional[str] = "USD"
) -> str:
    """
    Retrieve flight options for a given route and date, returning a concise summary.

    Args:
        fromId: A string representing the departure airport code (e.g., "SYR.AIRPORT").
        toId: A string representing the arrival airport code (e.g., "EWR.AIRPORT").
        departDate: A string representing the departure date in YYYY-MM-DD (or MM/DD/YYYY) format.
        returnDate: (Optional) A string representing the return date in the same format.
        adults: (Optional) An integer representing the number of adult passengers. Defaults to 1.
        children: (Optional) The number of children, including infants, who are under 18. Example: Child 1 Age = 8 months Child 2 Age = 1 year Child 3 Age = 17 years Here is what the request parameter would look like: children_age: 0,1,17.
        currency_code: (Optional) A string representing the currency code for pricing. Defaults to "USD".
        sort: (Optional) A string representing the sorting method for flight offers. This parameter orders result by BEST, CHEAPEST or FASTEST flights.
        cabinClass: (Optional) Search for flights that match the cabin class specified. Cabin call can be either ECONOMY, PREMIUM_ECONOMY, BUSINESS or FIRST.

    Returns:
        A concise summary of the top three flight offers (departure time, arrival time, airline, price)
        or an error message.
    """

    url = "https://booking-com15.p.rapidapi.com/api/v1/flights/searchFlights"
    api_key = os.getenv("RAPIDAPI_KEY")  # Ensure your RapidAPI key is set in your environment variables

    if not api_key:
        return "Error: No RapidAPI key found. Please set the environment variable 'RAPIDAPI_KEY'."

    querystring = {
        "fromId": fromId,
        "toId": toId,
        "departDate": departDate,
        "returnDate": returnDate if returnDate else "",
        "pageNo": "1",
        "adults": str(adults),
        "children": children if children else "",
        "sort": sort,
        "cabinClass": cabinClass, 
        "currency_code": currency_code
    }
    if returnDate:
        querystring["returnDate"] = returnDate

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        raw_response = response.text

        # Parse and summarize the flight offers
        json_data = json.loads(raw_response)
        offers = json_data.get("data", {}).get("flightOffers", [])
        if not offers:
            return "No flight offers found."

        summary_lines = []
        for offer in offers[:3]:
            segments = offer.get("segments", [])
            if not segments:
                continue
            segment = segments[0]
            departure_time = segment.get("departureTime", "N/A")
            arrival_time = segment.get("arrivalTime", "N/A")
            legs = segment.get("legs", [])
            if legs:
                first_leg = legs[0]
                carriers_data = first_leg.get("carriersData", [])
                airline = carriers_data[0].get("name", "Unknown Airline") if carriers_data else "Unknown Airline"
            else:
                airline = "Unknown Airline"
            price_info = offer.get("priceBreakdown", {}).get("total", {})
            currency = price_info.get("currencyCode", "AED")
            units = price_info.get("units", 0)
            nanos = price_info.get("nanos", 0)
            price = f"{currency} {units}.{str(nanos)[:2]}"
            summary_line = f"Airline: {airline}, Dep: {departure_time}, Arr: {arrival_time}, Price: {price}"
            summary_lines.append(summary_line)
        return "\n".join(summary_lines)
    except Exception as e:
        return f"Error parsing flight data: {str(e)}"

# %%
# Define the get_attractions tool
@tool
def get_attractions(
    query: str,
    startDate: Optional[str] = None,
    endDate: Optional[str] = None,
    currency_code: Optional[str] = "USD",  
    sort: Optional[str] = "trending"
) -> Dict[str, Any]:
    """
    Retrieve attractions based on a search query and optional date range.
    
    Args:
        query: Search term (e.g., "Newark").
        startDate: (Optional) Start date in YYYY-MM-DD format.
        endDate: (Optional) End date in YYYY-MM-DD format.
        currency_code: (Optional) Currency code for pricing. Defaults to "USD".
        sort: (Optional) Sorting method for attractions. Defaults to "trending". Can be "trending", "attr_book_score", or "lowest_price".

    Returns:
        A dictionary containing:
          - "attractions": List of up to 5 attractions.
          - "error": Error message if something goes wrong.
    """    
    
    search_url = "https://booking-com15.p.rapidapi.com/api/v1/attraction/searchLocation"
    api_key = os.getenv("RAPIDAPI_KEY")

    if not api_key:
        return {"error": "No RapidAPI key found. Please set 'RAPIDAPI_KEY'."}

    search_querystring = {"query": query}
    search_headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }

    try:
        # First API call: Get location product ID
        search_response = requests.get(search_url, headers=search_headers, params=search_querystring)
        search_response.raise_for_status()
        search_json_data = search_response.json()

        product_id = None
        
        if "data" in search_json_data and "products" in search_json_data["data"]:
            products = search_json_data["data"]["products"]
            if products and len(products) > 0:
                product_id = products[0].get("id")

        if not product_id:
            return {"error": f"No valid product ID found for query: {query}"}

        # Second API call: Get attractions using product ID
        attractions_url = "https://booking-com15.p.rapidapi.com/api/v1/attraction/searchAttractions"

        attractions_querystring = {
            "id": product_id,
            "startDate": startDate,
            "endDate": endDate,
            "pageNo": "1",
            "sort": sort,
            "currency_code": currency_code
        }

        attractions_headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "booking-com15.p.rapidapi.com"
        }

        attractions_response = requests.get(attractions_url, headers=attractions_headers, params=attractions_querystring)
        attractions_response.raise_for_status()
        
        attractions_json_data = attractions_response.json()

        # Extract top 5 attractions
        attractions_list = []
        
        for attraction in attractions_json_data.get("data", {}).get("products", [])[:5]:  
            name = attraction.get("name", "")
            description = attraction.get("shortDescription", "")  
            price_info = attraction.get("representativePrice", {})
            
            currency = price_info.get("currency", "")
            price_amount = price_info.get("chargeAmount", 0)
            
            price_formatted = f"{currency} {price_amount:.2f}" if currency else ""

            attractions_list.append({
                "name": name,
                "description": description,
                "price": price_formatted
            })

        return {
            "attractions": attractions_list
        }

    except Exception as e:
        return {"error": str(e)}

# %%
# Define the get_hotels tool
@tool
def get_hotels(
    query: str,
    arrival_date: str,
    departure_date: str,
    search_type: Optional[str] = "CITY",
    adults: Optional[int] = 1,
    children: Optional[str] = None,
    room_qty: Optional[int] = 1,
    page_number: Optional[int] = 1,
    currency_code: Optional[str] = "USD"
) -> Dict[str, Any]:
    """
    Retrieve hotels based on a search query (city).
    
    Args:
        query: Search term; names of locations, cities, districts, places, countries, counties etc.
        arrival_date: Arrival date in YYYY-MM-DD format.
        departure_date: Departure date in YYYY-MM-DD format.
        search_type: (Optional) Type of search. Defaults to "CITY". Can be "CITY", "DISTRICT", "PLACE", "COUNTRY", or "COUNTY".
        adults: (Optional) Number of adult guests. Defaults to 1.
        children: (Optional) The number of children under 18. Example format: "0,1,17" (ages).
        room_qty: (Optional) Number of rooms. Defaults to 1.
        page_number: (Optional) Page number for pagination. Defaults to 1.
        currency_code: (Optional) A string representing the currency code for pricing. Defaults to "USD".

    Returns:
        A dictionary containing:
          - "hotels": List of up to 5 hotels.
          - "error": Error message if something goes wrong.
    """    

    api_key = os.getenv("RAPIDAPI_KEY")
    
    if not api_key:
        return {"error": "No RapidAPI key found. Please set 'RAPIDAPI_KEY'."}

    # First API call to get destination ID
    search_url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchDestination"
    
    search_querystring = {"query": query}
    
    search_headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "booking-com15.p.rapidapi.com"
    }

    print(f"DEBUG: Fetching destination ID for '{query}'...")
    
    try:
        search_response = requests.get(search_url, headers=search_headers, params=search_querystring)
        search_response.raise_for_status()
        
        search_json_data = search_response.json()
        
        print(f"DEBUG: Destination API Response:\n{search_json_data}\n")

        dest_id = None
        
        if isinstance(search_json_data.get("data"), list):
            locations = search_json_data["data"]
            if locations and len(locations) > 0:
                dest_id = locations[0].get("dest_id")  

        if not dest_id:
            return {"error": f"No valid destination ID found for query: {query}"}

        print(f"DEBUG: Found Destination ID -> {dest_id}")

        # Second API call to fetch hotels
        hotels_url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"

        hotels_querystring = {
            "dest_id": dest_id,
            "arrival_date": arrival_date,
            "departure_date": departure_date,
            "search_type": search_type,
            "adults": str(adults),
            "children": children if children else "",
            "room_qty": str(room_qty),
            "page_no": str(page_number),
            "currency_code": currency_code,
        }

        print(f"DEBUG: Fetching hotels with parameters:\n{hotels_querystring}\n")

        hotels_headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "booking-com15.p.rapidapi.com"
        }

        hotels_response = requests.get(hotels_url, headers=hotels_headers, params=hotels_querystring)
        
        hotels_response.raise_for_status()
        
        hotels_json_data = hotels_response.json()

        print(f"DEBUG: Hotels API Response:\n{hotels_json_data}\n")

        # Extract top 5 hotels correctly
        hotels_list = []

        for hotel in hotels_json_data.get("data", {}).get("hotels", [])[:5]:  
            name = hotel.get("property", {}).get("name", "")

            price_info = hotel.get("property", {}).get("priceBreakdown", {}).get("grossPrice", {})
            currency = price_info.get("currency", "")
            price_amount = price_info.get("value", 0)
            
            price_formatted = f"{currency} {price_amount:.2f}" if currency else ""

            review_score_word = hotel.get("property", {}).get("reviewScoreWord", "")

            hotels_list.append({
                "name": name,
                "value": price_formatted,
                "reviewScoreWord": review_score_word
            })

        print(f"DEBUG: Extracted Hotels List -> {hotels_list}")

        return {"hotels": hotels_list}


    except Exception as e:
        print(f"ERROR: {str(e)}")
        
        return {"error": str(e)}



# %%
# Initialize final_answer tool
final_answer = FinalAnswerTool()

# Initialize CurrentDateTool tool
current_date = CurrentDateTool()
# %%
# Define the model parameters
model = HfApiModel(
max_tokens=2096,
temperature=0.5,
model_id='Qwen/Qwen2.5-Coder-32B-Instruct',
custom_role_conversions=None,
)

# %%
# Import tool from Hub
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

# %%
# Load the prompt templates from a YAML file
with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

# %%
# Define the code agent
agent = CodeAgent(
    model=model,
    tools=[
        get_attractions,
        get_hotels,
        get_flight_information,
        final_answer,
        current_date,
    ],
    max_steps=5,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)
# %%
# Launch the agent in the Gradio UI
GradioUI(agent).launch()


