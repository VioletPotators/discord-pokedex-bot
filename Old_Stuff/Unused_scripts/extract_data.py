import requests
import json
from tqdm import tqdm
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from functools import wraps

engine = create_engine('sqlite:///banco.db', echo=False)

Base = declarative_base()

class Pokemon(Base):
    __tablename__ = 'pokemons'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    types = Column(JSON, nullable=False) 
    image = Column(String, nullable=True)
    height = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    stats = Column(JSON, nullable=False)  

# Criar todas as tabelas no banco de dados
Base.metadata.create_all(engine)


# Criar uma sessão para interagir com o banco de dados
Session = sessionmaker(bind=engine)
session = Session()


def extract_data(pokemon_id):
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_id}/"
    response = requests.get(url)
    data = response.json()
    return data



def extract_flavor_text(id):
    url = f"https://pokeapi.co/api/v2/pokemon-species/{id}/"
    response = requests.get(url)
    data = response.json()

    flavor_text_entries = data['flavor_text_entries']
    
    for entry in flavor_text_entries:
        if entry['language']['name'] == 'en':
            flavor_text = entry['flavor_text']
            break
    return flavor_text


def extract_types(data):
    types_dict = {}
    for type_info in data['types']:
        types_dict[type_info['slot']] = type_info['type']['name']
    return types_dict


def extract_height_weight(data):
    height_weight_data = {
        "height": data['height'],
        "weight": data['weight']
    }
    return height_weight_data


def extract_stats(data):
    stats_dict = {}
    for stat_info in data['stats']:
        stats_dict[stat_info['stat']['name']] = stat_info['base_stat']
    return stats_dict

def main():
    for pokemon_id in tqdm(range(1, 1026)):
        image = pokemon_image(pokemon_id)
        data = extract_data(pokemon_id)
        flavor_text = extract_flavor_text(pokemon_id)
        types = extract_types(data)
        height_weight = extract_height_weight(data)
        stats = extract_stats(data)
        new_pokemon = Pokemon(name=data['name'].capitalize(), description=flavor_text, types=types, image=image, height=height_weight['height'], weight=height_weight['weight'], stats=stats)
        session.add(new_pokemon)
        session.commit()

def all_pokemons_ids():
    with open('pokemon_data.json', 'r') as file:
        data = json.load(file)
    
    pokemons_ids = set()
    for result in data['results']:
        url = result['url']
        pokemon_id = int(url.split('/')[-2])
        if pokemon_id < 10000:
            pokemons_ids.add(pokemon_id)

    with open('pokemon_ids.json', 'w') as json_file:
        json.dump(list(pokemons_ids), json_file, indent=4)

def count_pokemons_ids():
    with open('pokemon_ids.json', 'r') as file:
        data = json.load(file)
    last_id = data[-1]
    all_ids = set(range(1, last_id + 1))
    missing_ids = all_ids - set(data)
    
    if not missing_ids:
        print("All pokemons ids are in the list")
    else:
        print("Missing pokemons ids:", sorted(missing_ids))
    
def pokemon_image(id):
    id = str(id)
    num_zeros = "0" * (3 - len(id))
    id_completo = num_zeros + id
    pokemon_image = f"https://www.pokemon.com/static-assets/content-assets/cms2/img/pokedex/full/{id_completo}.png"
    return pokemon_image

if __name__ == "__main__":
   main()


    