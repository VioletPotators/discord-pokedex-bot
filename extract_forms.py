import requests
import json
import re
from bs4 import BeautifulSoup
import sqlite3
from tqdm import tqdm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Final_data import Base, Pokemon
import traceback
import time
from cloudscraper import create_scraper
import random
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# Update proxy configuration
PROXY_USER = ""
PROXY_PASS = ""
PROXY_ENDPOINT = ""

# Enhanced list of user agents
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (X11; Linux i686; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.2365.66',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/121.0.2277.128',
    'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Brave/122.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Brave/122.0.0.0'
]

def get_pokemon_names_from_banco():
    # # Connect to banco.db
    # banco_conn = sqlite3.connect('banco.db')
    # cursor = banco_conn.cursor()
    
    # # Get all pokemon names from the pokemon table
    # cursor.execute("SELECT name FROM pokemons")
    # pokemon_names = [row[0] for row in cursor.fetchall()]
    # print(len(pokemon_names))
    # banco_conn_saved = sqlite3.connect('pokedex.db')
    # cursor_saved = banco_conn_saved.cursor()
    # cursor_saved.execute("SELECT name FROM pokemons")   
    # saved_pokemon_names = [row[0] for row in cursor_saved.fetchall()]
    # print(len(saved_pokemon_names))
    # pokemon_names = list(set(pokemon_names) - set(saved_pokemon_names))
    # print(len(pokemon_names))
    # cursor.close()
    # cursor_saved.close()
    # banco_conn_saved.close()
    # banco_conn.close()

    pokemon_names = [
        "Nidoran",
        "Mr",
        "Ho",
        "Deoxys",
        "Wormadam",
        "Mime",
        "Porygon",
        "Giratina",
        "Shaymin",
        "Basculin",
        "Darmanitan",
        "Tornadus",
        "Thundurus",
        "Landorus",
        "Keldeo",
        "Meloetta",
        "Meowstic",
        "Aegislash",
        "Pumpkaboo",
        "Gourgeist",
        "Zygarde",
        "Oricorio",
        "Lycanroc",
        "Wishiwashi",
        "Type",
        "Minior",
        "Mimikyu",
        "Jangmo",
        "Hakamo",
        "Kommo",
        "Tapu",
        "Toxtricity",
        "Eiscue",
        "Indeedee",
        "Morpeko",
        "Urshifu",
        "Basculegion",
        "Enamorus",
        "Oinkologne",
        "Maushold",
        "Squawkabilly",
        "Palafin",
        "Tatsugiri",
        "Dudunsparce",
        "Great",
        "Scream",
        "Brute",
        "Flutter",
        "Slither",
        "Sandy",
        "Iron",
        "Wo",
        "Chien",
        "Ting",
        "Chi",
        "Roaring",
        "Walking",
        "Gouging",
        "Raging"
    ]
    return pokemon_names


def fetch_pokemon_data(pokemon_name):
    pokemon_actual_name = pokemon_name.lower().replace(' ', '-')
    url = f'https://www.pokemon.com/br/pokedex/{pokemon_actual_name}'
    
    try:
        # Try with cloudscraper as the primary method
        print(f"Attempting to fetch {pokemon_name} with cloudscraper...")
        
        # Set up cloudscraper with enhanced stealth settings
        # Create compatible browser-platform combinations
        browser_platform_combinations = [
            {'browser': 'firefox', 'platform': 'linux', 'mobile': False},
            {'browser': 'firefox', 'platform': 'windows', 'mobile': False},
            {'browser': 'firefox', 'platform': 'darwin', 'mobile': False},
            {'browser': 'chrome', 'platform': 'linux', 'mobile': False},
            {'browser': 'chrome', 'platform': 'windows', 'mobile': False},
            {'browser': 'chrome', 'platform': 'darwin', 'mobile': False},
            {'browser': 'chrome', 'platform': 'android', 'mobile': True},
            {'browser': 'chrome', 'platform': 'ios', 'mobile': True},
        ]
        
        browser_config = random.choice(browser_platform_combinations)
        
        scraper = create_scraper(
            browser=browser_config,
            delay=5,  # Add delay between requests
            interpreter='js2py'  # Use js2py instead of Node.js
        )
        
        # Select random user agent
        selected_user_agent = random.choice(user_agents)
        
        # Set up proxy for cloudscraper
        proxies = {
            'http': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_ENDPOINT}',
            'https': f'http://{PROXY_USER}:{PROXY_PASS}@{PROXY_ENDPOINT}'
        }
        
        # Enhanced headers to appear more like a real browser
        # Randomize header values to appear more organic
        accept_values = [
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        ]
        
        accept_lang_values = [
            'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'en-US,en;q=0.9,pt-BR;q=0.8',
            'pt-BR,pt;q=0.8,en;q=0.6',
            'en-US,en;q=0.8,pt;q=0.6'
        ]
        
        headers = {
            'User-Agent': selected_user_agent,
            'Accept': random.choice(accept_values),
            'Accept-Language': random.choice(accept_lang_values),
            'Accept-Encoding': random.choice(['gzip, deflate, br', 'gzip, deflate']),
            'Referer': random.choice([
                'https://www.pokemon.com/br/pokedex/',
                'https://www.pokemon.com/br/',
                'https://www.google.com/',
                None
            ]),
            'DNT': random.choice(['1', '0']),
            'Connection': random.choice(['keep-alive', 'close']),
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate', 
            'Sec-Fetch-Site': random.choice(['same-origin', 'none']),
            'Sec-Fetch-User': '?1',
            'Cache-Control': f'max-age={random.randint(0,300)}'
        }
        # Add random sleep before request to mimic human behavior
        time.sleep(random.uniform(1, 3))
        
        try:
            # Add cookies to appear as a returning visitor
            cookies = {
                'visitCount': str(random.randint(2, 10)),
                'lastVisit': str(int(time.time()) - random.randint(86400, 604800))
            }
            
            response = scraper.get(
                url, 
                headers=headers, 
                proxies=proxies, 
                timeout=30,
                cookies=cookies,
                allow_redirects=True
            )
            
            # Random delay after request
            time.sleep(random.uniform(2, 4))
            
            html_content = response.text
            
            if "incapsula" in html_content:
                return None, None, None, None

            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Save the HTML for debugging
            with open(f'Pokedex_html/{pokemon_actual_name}_debug.html', 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            form_buttons = []
            try:
                # Get Pokemon ID
                pokemon_id = soup.find('section', class_="pokedex-pokemon-header")
                pokemon_id = pokemon_id.find('div', class_='pokedex-pokemon-pagination-title')
                pokemon_id = pokemon_id.find('div')
                pokemon_id = pokemon_id.find("span").text.strip().zfill(4)

                pokemon_id = pokemon_id.replace("Nº ", "")
                # Initialize forms list
                forms = []

                # Get all form buttons
                form_select = soup.find('select', id='formes')
                if form_select:
                    form_buttons = form_select.find_all('option')
                else:
                    form_buttons = [None]

            except Exception as e:
                traceback.print_exc()
                print("Error:" + str(e))
                #return None, None, None, None
            
            if not form_buttons:
                form_buttons = [None]  # Handle Pokemon without forms

            
            descriptions = soup.find_all('div', class_='version-descriptions')
            attributes = soup.find_all('div', class_='pokemon-ability-info')
            types_list = soup.find_all('div', class_='pokedex-pokemon-attributes')

            for i, form_button in enumerate(form_buttons):
                # Get descriptions
                description = descriptions[i]
                version_x = description.find('p', class_='version-x').text.strip() if description.find('p', class_='version-x') else ""
                version_y = description.find('p', class_='version-y').text.strip() if description.find('p', class_='version-y') else ""
                
                forms_descriptions = {
                    "version_x": version_x,
                    "version_y": version_y
                }

                # Get physical attributes
                attribute = attributes[i]
                attribute_list = attribute.find_all('span', class_="attribute-value")
                height = attribute_list[0].text.strip()
                weight = attribute_list[1].text.strip()
                gender_span = attribute_list[2]
                gender_icons = gender_span.find_all('i')
                gender = ""

                if gender_icons:
                    for icon in gender_icons:
                        if 'icon_male_symbol' in icon.get('class', []):
                            gender += "Male "
                        if 'icon_female_symbol' in icon.get('class', []):
                            gender += "Female"
                    gender = gender.strip()
                else:
                    gender = "Unknown"  # or gender_span.text.strip() if there's text instead of icons

                # Get image URL
                image_url = soup.find('div', class_='profile-images').find('img')['src']

                # Get types
                type_list = types_list[i].find('div', class_='dtm-type').find_all('li')
                types = [t.text.strip() for t in type_list]

                # Get weaknesses
                weakness_section = types_list[i].find('div', class_='dtm-weaknesses')
                weaknesses_4x = []
                weaknesses_2x = []
                
                if weakness_section:
                    for weakness in weakness_section.find_all('li'):
                        weakness_text = weakness.find('span').text.strip()
                        # Check if there's an extra-damage icon (4x damage)
                        if weakness.find('i', class_='extra-damage'):
                            weaknesses_4x.append(weakness_text)
                        else:
                            weaknesses_2x.append(weakness_text)

                # Get stats
                stats_data = {}
                stats_section = soup.find('div', class_='pokemon-stats-info').find_all('li')
                for stat in stats_section:
                    if stat.find('span'):  # Check if the li element has a span (stat name)
                        stat_name = stat.find('span').text.strip()
                        stat_value = stat.find('li', class_='meter').get('data-value')
                        stats_data[stat_name] = int(stat_value)

                # Get abilities
                abilities_section = soup.find_all('div', class_='pokemon-ability-info-detail')
                abilities = []
                for ability in abilities_section:
                    if ability.find('h3') and ability.find('p'):  # Make sure both elements exist
                        name = ability.find('h3').text.strip()
                        ability_description = ability.find('p').text.strip()
                        abilities.append({"name": name, "description": ability_description})

                # Get evolution chain
                evolution_chain = {
                    "first": {"name": "", "number": "", "image_url": "", "types": []},
                    "middle": [],
                    "last": [],
                    "unknown": []
                }
                
                evolution_section = soup.find('section', class_='section pokedex-pokemon-evolution')
                if evolution_section:
                    # Process each evolution stage
                    for stage in evolution_section.find_all('a'):
                        number = stage.find('span', class_='pokemon-number').text.strip()
                        number = number.replace('Nº ', '').strip()
                        pokemon_info = {
                            "name": stage.find('h3').text.strip().split('\n')[0],  # Get name without number
                            "number": number,
                            "image_url": stage.find('img')['src'],
                            "types": [t.text.strip() for t in stage.find_all('li', class_=lambda x: x and 'background-color-' in x)]
                        }
                        
                        # Determine which stage this evolution belongs to
                        if not evolution_chain["first"]["name"]:
                            evolution_chain["first"] = pokemon_info
                        else:
                            evolution_chain["last"].append(pokemon_info)

                # Create form data
                form_data = {
                    "name": pokemon_actual_name.capitalize() if i == 0 else form_button.text.strip(),
                    "value": str(i),
                    "descriptions": forms_descriptions,
                    "height": height,
                    "weight": weight,
                    "gender": gender,
                    "image_url": image_url,
                    "types": types,
                    "weaknesses": {
                        "4x": weaknesses_4x,
                        "2x": weaknesses_2x
                    },
                    "stats": stats_data,
                    "abilities": abilities
                }
                
                forms.append(form_data)

            
            return pokemon_actual_name, pokemon_id, forms, evolution_chain

        except Exception as scraper_error:
            print(f"Cloudscraper failed: {scraper_error}")
            return None, None, None, None
            # print(f"Cloudscraper failed: {scraper_error}. Trying with Firefox...")
            
            # # Fall back to Firefox + Selenium if cloudscraper fails
            # # Configure Firefox options
            # options = Options()
            # # options.headless = True  # Keep browser visible
            # options.set_preference("dom.webdriver.enabled", False)
            # options.set_preference('useAutomationExtension', False)
            
            # # Add random user agent
            # options.set_preference("general.useragent.override", selected_user_agent)
            
            # # Configure proxy
            # options.set_preference("network.proxy.type", 1)
            # options.set_preference("network.proxy.socks", PROXY_ENDPOINT.split(':')[0])
            # options.set_preference("network.proxy.socks_port", int(PROXY_ENDPOINT.split(':')[1]))
            # options.set_preference("network.proxy.socks_username", PROXY_USER)
            # options.set_preference("network.proxy.socks_password", PROXY_PASS)
            # options.set_preference("network.proxy.socks_version", 5)
            
            # # Set Firefox profile directory to persist user data
            # firefox_profile_path = "./firefox_profile"
            # options.set_preference("profile", firefox_profile_path)
            
            # # Create Firefox driver
            # service = Service(GeckoDriverManager().install())
            # driver = webdriver.Firefox(service=service, options=options)
            
            # try:
            #     driver.get(url)
            #     time.sleep(5)  # Wait for page to load
                
            #     html_content = driver.page_source
            #     soup = BeautifulSoup(html_content, 'html.parser')
                
            #     # Save the HTML for debugging
            #     with open(f'{pokemon_actual_name}_firefox_debug.html', 'w', encoding='utf-8') as f:
            #         f.write(html_content)
                
            #     # Process the rest of the data extraction as before
            #     # ... (same code as in the cloudscraper section)
                
            #     # Removed the test exception
            #     # raise Exception("teste")
                
            #     # The rest of the code is the same as in the cloudscraper section
            #     # ... (copy the same parsing logic here)
                
            #     driver.quit()
            #     return pokemon_actual_name, pokemon_id, forms, evolution_chain
                
            # except Exception as firefox_error:
            #     if driver:
            #         driver.quit()
            #     print(f"All methods failed: {firefox_error}")
            #     return None, None, None, None
    
    except Exception as e:
        traceback.print_exc()
        print(f"Error fetching data for {pokemon_name}: {e}")
        return None, None, None, None

def process_single_pokemon(pokemon_name, session):
    try:
        pokemon_actual_name, pokemon_id, forms, evolution_chain = fetch_pokemon_data(pokemon_name)
        
        if not all([pokemon_actual_name, pokemon_id, forms, evolution_chain]):
            print(f"Failed to fetch complete data for {pokemon_name}")
            return

        for index, form in enumerate(forms):
            current_id = pokemon_id if index == 0 else f"{pokemon_id}f{index + 1}"
            
            height = form['height'].strip()
            weight = form['weight'].strip()

            pokemon = Pokemon(
                name=form['name'],
                id=current_id,
                description_x=form['descriptions']['version_x'],
                description_y=form['descriptions']['version_y'],
                height=height,
                weight=weight,
                types=form['types'],
                image=form['image_url'],
                gender=form['gender'],
                stats=form['stats'],
                abilities=form['abilities'],
                weaknesses_4X=form['weaknesses']['4x'],
                weaknesses_2X=form['weaknesses']['2x'],
                evolution_chain=evolution_chain
            )

            session.merge(pokemon)
            session.commit()
            print(f"Successfully saved {form['name']} (ID: {current_id}) to database")
        return True
        
    except Exception as e:
        traceback.print_exc()
        print(f"Error processing {pokemon_name}: {e}")
        session.rollback()
        return False

def process_all_pokemon_from_banco():
    # Database setup for pokedex.db
    engine = create_engine('sqlite:///pokedex.db', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        pokemon_names = get_pokemon_names_from_banco()
        print(f"Found {len(pokemon_names)} Pokemon to process")

        for pokemon_name in tqdm(pokemon_names, desc="Processing Pokemon"):
            retries = 0
            max_retries = 2
            success = False
            
            while retries < max_retries and not success:
                result = process_single_pokemon(pokemon_name, session)
                if result:
                    success = True
                else:
                    retries += 1
                    if retries < max_retries:
                        print(f"Retry {retries}/{max_retries} for {pokemon_name}")
                        time.sleep(random.uniform(5, 10))
                    else:
                        print(f"Failed to process {pokemon_name} after {max_retries} attempts")

            time.sleep(random.uniform(5, 10))

    finally:
        session.close()

def main():
    # Setup database
    engine = create_engine('sqlite:///pokedex.db', echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    while True:
        print("\nChoose an option:")
        print("1. Process a single Pokemon")
        print("2. Process all Pokemon from banco.db")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            pokemon_name = input("Enter Pokemon name: ")
            process_single_pokemon(pokemon_name, session)
        elif choice == "2":
            process_all_pokemon_from_banco()
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")

    session.close()

if __name__ == "__main__":
    main()