# State Capital Project from EMRTS

The goal of this project is to use a JSON with State Capital Values, add a Latitude and Longitude to those values,
output it to a JSON file. Within the program, make sure the values have been validated by using the
USPS API.

## How to run

1. Install Python 3 in your computer.
2. Install uv (Package manager for Python3).
3. Change filename .env.example to .env and add the values needed from USPS API.
4. Add dependencies named requests (v2.32.2) and python-dotenv (v1.1.0)
    > uv pip install python-dotenv requests
5. Run the following command:
    > uv run add_map_position.py
