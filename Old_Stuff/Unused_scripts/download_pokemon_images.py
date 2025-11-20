import os
import base64
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from selenium import webdriver
from selenium.webdriver.common.by import By
from main import Base, Pokemon

# Set up the Selenium WebDriver
driver = webdriver.Chrome() 

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

# Download each image using Selenium
for pokemon in pokemons:
    if pokemon.image:
        image_url = pokemon.image
        # Use Selenium to navigate to the image URL
        driver.get(image_url)
        
        # Locate the image element
        image_element = driver.find_element(By.TAG_NAME, 'img')
        
        # Get the image as a base64 string
        image_base64 = driver.execute_script(
            "return arguments[0].src;", image_element)
        #.split(',')[0]
        
        # Decode the base64 string and save the image
        image_data = base64.b64decode(image_base64)
        image_path = os.path.join('Pokemon_images', f"{pokemon.name}.png")
        with open(image_path, 'wb') as file:
            file.write(image_data)
        
        print(f"Downloaded: {pokemon.name}.png")
        break
# Close the WebDriver
driver.quit()
