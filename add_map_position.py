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


def app_map_position():
    """
    This function performs these steps:
    1.) Read all the capital addresses from a given JSON.
    2.) Verify that these are real addresses.
    3.) Add a Latitude and Longitude of the following address object.
    4.) Output the JSON of the address object.
    5.) Verify that the JSON file outputted is Valid JSON.
    """
    state_capitals: List[StateCapital] = grab_state_capital_addresses_from_json("us_capital_addresses.json")
    verify_state_capital_addresses_from_json(state_capitals)

def grab_state_capital_addresses_from_json(filename: str) -> List[StateCapital]:
    with open(filename, "r") as file:
        json_contents = json.load(file)

    state_capital_addresses: List[StateCapital] = json_contents["stateCapitols"]
    return state_capital_addresses

def verify_state_capital_addresses_from_json(state_capitals: List[StateCapital]) -> bool:
    """
    Verify the JSON file using the USPS API.
    USPS API only allows XML.
    """

    api_batch_size = 5
    for index in range(0, len(state_capitals), api_batch_size):
        batch = state_capitals[index: index + api_batch_size]
        xml_addresses = ""
        for batch_index, state_capital in enumerate(batch):
            xml_addresses += f"""
                <Address ID="{batch_index}">
                  <Address1>{state_capital.get("address", {}).get("street")}</Address1>
                  <Address2></Address2>
                  <City>{state_capital.get("address", {}).get("city")}</City>
                  <State>{state_capital.get("state")}</State>
                  <Zip5></Zip5>
                  <Zip4></Zip4>
                </Address>
                """

        xml_batch_request = f"""
            <AddressValidateRequest USERID="{grab_user_id_env()}">
              {xml_addresses}
            </AddressValidateRequest>
            """

        url = f"https://secure.shippingapis.com/ShippingAPI.dll?API=Verify&XML={encoded_xml}"

        response = requests.get(url)
        response.raise_for_status()

        root = ET.fromstring(response.content)

        for batch_index, address in enumerate(root.findall('address')):
            error = address.find('Error')
            if error is not None:
                desc = error.findtext('Description')
                print(f"Address contains Error! Address:{batch[batch_index]} Error: {desc}")
                return False

            response_address2 = address.findtext('secondaryAddress', default='')
            response_city = address.findtext('city', default='')
            response_state = address.findtext('state', default='')
            response_zip_code = address.findtext('ZIPCode', default='')
            batch_address = batch[batch_index].get('address', {}).get('street')
            batch_city = batch[batch_index].get('address', {}).get('city')
            batch_state = batch[batch_index].get('state')
            batch_zip_code = batch[batch_index].get('address', {}).get('zipCode')

            if batch_state != response_state:
                print(f"JSON State Capital State: {batch_state} does not match {response_state} from USPS API ")
                return False
            elif batch_city != response_city:
                print(f"JSON State Capitals City: {batch_city} does not match {response_city} from USPS API ")
                return False
            elif batch_address != response_address2:
                print(f"JSON State Capitals City: {response_address2} does not match {batch_address} from USPS API ")
                return False
            elif batch_zip_code != response_zip_code:
                print(f"JSON State Capitals City: {batch_zip_code} does not match {response_zip_code} from USPS API ")
                return False

    print(f"JSON Validated Successfully!")
    return True

def grab_user_id_env() -> str | None:
    return os.getenv("USERID")

if __name__ == "__main__":
    load_dotenv()
    app_map_position()