import json
import requests
import xml.etree.ElementTree as ET
def app_map_position():
    """
    This function performs these steps:
    1.) Read all the capital addresses from a given JSON.
    2.) Verify that these are real addresses.
    3.) Add a Latitude and Longitude of the following address object.
    4.) Output the JSON of the address object.
    5.) Verify that the JSON file outputted is Valid JSON.
    """
    verify_json_file("us_capital_addresses.json")

def verify_json_file(filename: str) -> bool:
    """
    Verify the JSON file using the USPS API.
    USPS API only allows XML.
    """
    with open(filename, "r") as file:
        addresses = json.load(file)

    api_batch_size = 5
    for index in range(0, len(addresses), api_batch_size):
        batch = addresses[index: index + api_batch_size]
        xml_addresses = ""
        for batch_index, full_address in enumerate(batch):
            address, city, state = full_address.split(", ")
            state: str = state[:2]
            xml_addresses += f"""
            <Address ID="{batch_index}">
              <Address1>{address}</Address1>
              <Address2></Address2>
              <State>{state}</State>
              <Zip5></Zip5>
              <Zip4></Zip4>
            </Address>
            """

        test = "a"
        xml_batch_request = f"""
        <AddressValidateRequest USERID="{test}">
        {xml_addresses}
        </AddressValidateRequest>
        """

        print(xml_batch_request)



if __name__ == "__main__":
    app_map_position()