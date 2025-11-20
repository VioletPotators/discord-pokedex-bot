from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
# List of Pokémon types
pokemon_types = ['bug', 'dark', 'dragon', 'electric', 'fairy', 'fighting', 'fire', 'flying', 'ghost', 'grass', 'ground', 'ice', 'normal', 'poison', 'psychic', 'rock', 'steel', 'water']

# Base URL for the images
base_url = "https://bulbapedia.bulbagarden.net/wiki/Type#/media/File:{}_icon_SwSh.png"

# Set up the Selenium WebDriver
# Replace '/path/to/chromedriver' with the actual path to your ChromeDriver executable
#service = Service('/path/to/chromedriver')
driver = webdriver.Chrome()#service=service)

# Function to get image URL for a Pokemon type
def get_image_url(pokemon_type):
    url = base_url.format(pokemon_type.capitalize())
    driver.get(url)
    time.sleep(3)
    #get body element and pritn content
    body_element = driver.find_element(By.TAG_NAME, 'body')
    print(body_element.text)
    try:
        # Wait for the image to be loaded using xpath with a partial match for the src attribute
        img_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, f'//img[@alt="{pokemon_type.capitalize()} icon SwSh.png"]'))
        )
        return img_element.get_attribute('src')
    except:
        return None

# Get and print image URLs for each type
for pokemon_type in pokemon_types:
    image_url = get_image_url(pokemon_type)
    if image_url:
        print(f"{pokemon_type}: {image_url}")
    else:
        print(f"Failed to find image URL for {pokemon_type} type icon")

# Close the browser
driver.quit()

print("All Pokemon type icon URLs printed successfully!")
