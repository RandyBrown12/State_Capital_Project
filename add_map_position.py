import json
import os
from typing import List, TypedDict
from dotenv import load_dotenv
from datetime import datetime

import requests
from requests import HTTPError

class Address(TypedDict):
    street: str
    city: str
    state: str
    zipCode: str

class StateCapital(TypedDict, total=False):
    state: str
    capital: str
    address: Address
    _comment: str
    latitude: float
    longitude: float

def create_json(token: str):
    """
    This function performs these steps:
    1.) Read all the capital addresses from a given JSON.
    2.) Verify that these are real addresses.
    3.) Add a Latitude and Longitude of the following address object.
    4.) Output the JSON of the address object.
    5.) Verify that the JSON file outputted is Valid JSON.
    """
    state_capitals: List[StateCapital] = verify_json_file("us_capital_addresses.json")
    state_capitals: List[StateCapital] = verify_state_capital_addresses_from_json(state_capitals, token)

    state_capitals_updated: List[StateCapital] = add_latitude_and_longitude(state_capitals)

    output_state_capitals_into_json(state_capitals_updated)

    output_state_capitals: List[StateCapital] = verify_json_file("us_capital_addresses_updated.json")
    output_state_capitals: List[StateCapital] = verify_state_capital_addresses_from_json(output_state_capitals, token)

    print("Program has finished Running!")

def add_latitude_and_longitude(state_capitals: List[StateCapital]) -> List[StateCapital]:
    copied_state_capitals: List[StateCapital] = state_capitals.copy()

    for state_capital in copied_state_capitals:
        params = {
            "q": f"{state_capital['capital']},{state_capital['address']['state']}",
            "format": "json"
        }

        headers = {
            "User-Agent": "State_Capitals/1.0"
        }

        url = "https://nominatim.openstreetmap.org/search"
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            raise HTTPError(f"Error Code: {response.status_code} from {url}. ERROR: {response.json()['error']}")

        response_json = response.json()

        state_capital["latitude"] = float(response_json[0]['lat'])
        state_capital["longitude"] = float(response_json[0]['lon'])
        print(f"{state_capital['state']} has Latitude and Longitude Added!")

    return copied_state_capitals

def output_state_capitals_into_json(state_capitals: List[StateCapital]) -> None:
    state_capitals_json = {"state_capitals": state_capitals}
    with open("us_capital_addresses_updated.json", "w") as file:
        file.write(json.dumps(state_capitals_json, indent=2))

    print("File has been written to JSON")

def verify_json_file(filename: str) -> List[StateCapital]:
    with open(filename, 'r') as file:
        state_capitals: List[StateCapital] = json.load(file)['state_capitals']

    required_keys = ["state", "capital", "address", "_comment"]
    required_address_keys = ["street", "city", "state", "zipCode"]
    optional_keys = ["latitude", "longitude"]

    for state_capital in state_capitals:
        required_key_count = 0
        for state_capital_key in state_capital.keys():
            if state_capital_key not in required_keys and state_capital_key not in optional_keys:
                raise ValueError(f"Invalid Key: ({state_capital_key}) in JSON {state_capital}")
            elif state_capital_key == "address":
                required_key_count += 1
                required_address_key_count = 0
                for address_key in state_capital['address'].keys():
                    if address_key not in required_address_keys:
                        raise ValueError(f"Invalid Address Key: ({address_key}) in JSON {state_capital}")
                    required_address_key_count += 1
                if required_address_key_count != len(required_address_keys):
                    raise ValueError(f"Incorrect Account of Required Keys {len(required_address_keys)}! Received {required_address_key_count} required keys!")
            elif state_capital_key in required_keys:
                required_key_count += 1
        if required_key_count != len(required_keys):
            raise ValueError(f"Incorrect Account of Required Keys {len(required_keys)}! Received {required_key_count} required keys!")
        print("A JSON object has been validated!")
    return state_capitals

def verify_state_capital_addresses_from_json(state_capitals: List[StateCapital], token: str) -> List[StateCapital]:
    """
    Verify the JSON file using the USPS API.
    """
    api_endpoint = "https://apis.usps.com/addresses/v3/address"
    copied_state_capitals = state_capitals.copy()
    header = {
        "Authorization": f"Bearer {token}",
    }

    for state_capital in copied_state_capitals:
        state_capital_city = state_capital.get("address", {}).get("city")
        state_capital_state = state_capital.get("address", {}).get("state")
        state_capital_zip_code = state_capital.get("address", {}).get("zipCode")
        state_capital_street_address = state_capital.get("address", {}).get("street")

        params = {
            "streetAddress": state_capital_street_address,
            "state": state_capital_state,
            "city": state_capital_city
        }

        url = "https://apis.usps.com/addresses/v3/address"
        response = requests.get(url, headers=header, params=params)
        if response.status_code != 200:
            raise HTTPError(f"Error Code: {response.status_code} from {url}. ERROR: {response.json()['error']}")
        response_state_capital = response.json()
        response_state_capital_address = response_state_capital.get("address")
        if response_state_capital_address is None:
            print(f"No Address found for: {response_state_capital_address}")

        response_state_capital_city = response_state_capital_address.get("city")
        response_state_capital_state = response_state_capital_address.get("state")
        response_state_capital_zip_code = response_state_capital_address.get("ZIPCode")
        response_state_capital_street_address = response_state_capital_address.get("streetAddress")

        if state_capital_state.lower() != response_state_capital_state.lower():
            raise ValueError(f"States do not match: JSON:{state_capital_state} != response_JSON:{response_state_capital_state}")
        elif state_capital_street_address.lower() != response_state_capital_street_address.lower():
            raise ValueError(f"Street Addresses do not match: JSON:{state_capital_street_address} != response_JSON:{response_state_capital_street_address}")
        elif state_capital_city.lower() != response_state_capital_city.lower():
            raise ValueError(f"Cities do not match: JSON:{state_capital_city} != response_JSON:{response_state_capital_city}")
        # Note: USPS API does not have Zip Code for New York or Utah or Wisconsin
        elif (state_capital_zip_code.lower() != response_state_capital_zip_code.lower()) and state_capital_state not in ["NY","UT","WI"]:
            raise ValueError(f"Zip Codes do not match: JSON:{state_capital_zip_code} != response_JSON:{response_state_capital_zip_code}")
        elif state_capital.get('latitude', None) is not None:
            if not isinstance(state_capital.get('latitude'), float):
                raise ValueError(f"State {state_capital["state"]} has invalid latitude: {state_capital.get('latitude')}")
        elif state_capital.get('longitude', None) is not None:
            if not isinstance(state_capital.get('longitude'), float):
                raise ValueError(f"State {state_capital["state"]} has invalid latitude: {state_capital.get('latitude')}")

        print(f"State {state_capital["state"]} has been validated!")
        for state_capital_object in copied_state_capitals:
            if state_capital_object["state"] == state_capital["state"]:
                state_capital_object["_comment"] = f"This has been correctly validated by the USPS API on {datetime.now()}"

    return copied_state_capitals

def grab_user_id_env() -> str | None:
    return os.getenv("USER_ID")

def grab_oauth_token() -> str | None:
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "addresses"
    }

    response = requests.post("https://apis.usps.com/oauth2/v3/token", headers=headers, json=body)
    response.raise_for_status()
    return response.json()['access_token']

if __name__ == "__main__":
    load_dotenv()
    OAuthToken = grab_oauth_token()
    create_json(OAuthToken)