import json
import os
from typing import List, TypedDict

from dotenv import load_dotenv

import requests

class Address(TypedDict):
    buildingName: str
    street: str
    city: str
    state: str
    zipCode: str

class StateCapital(TypedDict):
    state: str
    capital: str
    address: Address


def app_map_position(token: str):
    """
    This function performs these steps:
    1.) Read all the capital addresses from a given JSON.
    2.) Verify that these are real addresses.
    3.) Add a Latitude and Longitude of the following address object.
    4.) Output the JSON of the address object.
    5.) Verify that the JSON file outputted is Valid JSON.
    """
    state_capitals: List[StateCapital] = grab_state_capital_addresses_from_json("us_capital_addresses.json")
    verify_state_capital_addresses_from_json(state_capitals, token)

def grab_state_capital_addresses_from_json(filename: str) -> List[StateCapital]:
    with open(filename, "r") as file:
        json_contents = json.load(file)

    state_capital_addresses: List[StateCapital] = json_contents["stateCapitols"]
    return state_capital_addresses

def verify_state_capital_addresses_from_json(state_capitals: List[StateCapital], token: str) -> bool:
    """
    Verify the JSON file using the USPS API.
    USPS API only allows XML.
    """
    api_endpoint = "https://apis.usps.com/addresses/v3/address"

    header = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Traveling Salesman/1.0"
    }

    for state_capital in state_capitals:
        state_capital_city = state_capital.get("address", {}).get("city")
        state_capital_state = state_capital.get("address", {}).get("state")
        state_capital_zip_code = state_capital.get("address", {}).get("zipCode")
        state_capital_street_address = state_capital.get("address", {}).get("street")

        body = {
            "streetAddress": state_capital_street_address,
            "state": state_capital_state
        }

        response = requests.get("https://apis.usps.com/addresses/v3/address", headers=header, json=body)
        response.raise_for_status()
        response_state_capital = response.json()
        response_state_capital_city = response_state_capital.get("address", {}).get("city")
        response_state_capital_state = response_state_capital.get("address", {}).get("state")
        response_state_capital_zip_code = response_state_capital.get("address", {}).get("ZIPCode")
        response_state_capital_street_address = response_state_capital.get("address", {}).get("street")

        if state_capital_city != response_state_capital_city:
            print(f"City from JSON:{state_capital_city} and City from Response:{response_state_capital_city} do not match!")
            return False
        elif state_capital_state != response_state_capital_state:
            print(f"State from JSON:{state_capital_state} and State from Response:{response_state_capital_state} do not match!")
            return False
        elif state_capital_zip_code != response_state_capital_zip_code:
            print(f"Zip Code from JSON:{state_capital_zip_code} and Zip Code from Response:{response_state_capital_state} do not match!")
            return False
        elif state_capital_street_address != response_state_capital_street_address:
            print(f"Street Address from JSON:{state_capital_street_address} and Street Address from Response:{response_state_capital_street_address} do not match!")
            return False

        print(f"Address has been validated for {response_state_capital_state}")

    return True


def grab_user_id_env() -> str | None:
    return os.getenv("USER_ID")

def grab_oauth_token() -> str | None:
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    body = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post("https://apis.usps.com/oauth2/v3/token", headers=headers, json=body)
    response.raise_for_status()
    return response.json()['access_token']

if __name__ == "__main__":
    load_dotenv()
    OAuthToken = grab_oauth_token()
    app_map_position(OAuthToken)