import requests
import json

# Define the URL for the PokeAPI
url = "https://pokeapi.co/api/v2/pokemon?limit=100000&offset=0"

# Make a GET request to the PokeAPI
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the JSON data
    data = response.json()

    # Open a JSON file for writing
    with open('pokemon_data.json', 'w') as file:
        json.dump(data, file, indent=4)
    print("Data has been written to pokemon_data.json")
else:
    print("Failed to retrieve data from the PokeAPI")

