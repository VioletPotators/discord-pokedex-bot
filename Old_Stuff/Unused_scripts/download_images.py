import os
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import Base, Pokemon
import time
from tqdm import tqdm
# Create a database engine
engine = create_engine('sqlite:///banco.db')

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a session
session = Session()

# Ensure the directory exists
os.makedirs('Pokemon_images', exist_ok=True)

# Query all Pokémon entries
pokemons = session.query(Pokemon).all()

#pobre / podre
proxy_host = ""
proxy_port = 35337
proxy_user = ""
proxy_pass = ""
proxies = {
    "http": f"socks5://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}",
    "https": f"socks5://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
}


# Download each image and update the database
for pokemon in tqdm(pokemons):
    if pokemon.image:
        image_url = pokemon.image
        image_path = os.path.join('Pokemon_images', f"{pokemon.name}.png")
        retries = 20
        backoff_factor = 2
        for attempt in range(retries):
            time.sleep(0.5)
            # Download the image
            response = requests.get(image_url, proxies=proxies)
            response.raise_for_status()  # Raise an error for bad responses

            # Save the image to the specified path
            if len(response.content) == 212:
                print(f"Failed to download {pokemon.name}'s image: No image found")
                if attempt < retries - 1:
                    wait_time = backoff_factor ** attempt
                    print(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
            else:
                with open(image_path, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded {pokemon.name}'s image.")
                break
                
            # Update the image path in the database
            pokemon.image = image_path
            session.commit()
            
# Close the session
session.close()
