import requests
from bs4 import BeautifulSoup

def get_pokemon_type_images():
    url = "https://commons.wikimedia.org/wiki/Category:Pok%C3%A9mon_types_icons"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    gallery = soup.find('ul', class_='gallery mw-gallery-traditional')
    if not gallery:
        print("Gallery not found")
        return []

    image_urls = []
    for img in gallery.find_all('img'):
        src = img.get('src')
        if src:
            # Convert relative URL to absolute URL
            if src.startswith('//'):
                src = 'https:' + src
            image_urls.append(src)

    return image_urls

pokemon_type_images = get_pokemon_type_images()
for url in pokemon_type_images:
    print(url)

# Example usage
# if __name__ == "__main__":
#     pokemon_type_images = get_pokemon_type_images()
#     for url in pokemon_type_images:
#         print(url)
