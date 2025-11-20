import json


with open('extracted_data.json', 'r') as file:
    data = json.load(file)

def get_pokemon_types():
    all_pokemon_types = set()
    for pokemon in data:
        types = pokemon.get('types', {}).values()
        all_pokemon_types.update(types)
    return sorted(list(all_pokemon_types))

# Example usage
unique_types = get_pokemon_types()
print(unique_types)


