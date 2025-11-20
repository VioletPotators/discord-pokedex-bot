from sqlalchemy import create_engine, Column, Integer, String, Text, JSON, select, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from functools import wraps
import traceback
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

# Criar o engine que aponta para o banco de dados SQLite
engine = create_engine('sqlite:///banco.db', echo=False)

Base = declarative_base()

# Definir uma tabela simples
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    time = Column(Text, default="[]")

class Pokemon(Base):
    __tablename__ = 'pokemons'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description_x = Column(Text, nullable=True)
    description_y = Column(Text, nullable=True)
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

TYPES_EMOJIS = {
    "normal": "🔶",
    "fighting": "👊",
    "flying": "💨",
    "poison": "🍄",
    "ground": "🏔",
    "rock": "🗿",
    "bug": "🕸",
    "ghost": "👻",
    "steel": "⚙️",
    "fire": "🔥",
    "water": "💧",
    "grass": "🍃",
    "electric": "⚡️",
    "psychic": "👁️",
    "ice": "❄️",
    "dragon": "🐲",
    "dark": "🌙",
    "fairy": "🌈"
}

DISCORD_TYPE_COLORS = {
    "bug": discord.Color.from_str('#A6B91A'),
    "dark": discord.Color.from_str('#705746'),
    "dragon": discord.Color.from_str('#6F35FC'),
    "electric": discord.Color.from_str('#F7D02C'),
    "fairy": discord.Color.from_str('#D685AD'),
    "fighting": discord.Color.from_str('#C22E28'),
    "fire": discord.Color.from_str('#EE8130'),
    "flying": discord.Color.from_str('#A98FF3'),
    "ghost": discord.Color.from_str('#735797'),
    "grass": discord.Color.from_str('#7AC74C'),
    "ground": discord.Color.from_str('#E2BF65'),
    "ice": discord.Color.from_str('#96D9D6'),
    "normal": discord.Color.from_str('#A8A77A'),
    "poison": discord.Color.from_str('#A33EA1'),
    "psychic": discord.Color.from_str('#F95587'),
    "rock": discord.Color.from_str('#B6A136'),
    "steel": discord.Color.from_str('#82b6cf'),
    "water": discord.Color.from_str('#6390F0')
}

TYPE_ICONS = {
    "bug": "https://archives.bulbagarden.net/media/upload/thumb/9/9c/Bug_icon_SwSh.png/64px-Bug_icon_SwSh.png",
    "dark": "https://archives.bulbagarden.net/media/upload/thumb/d/d5/Dark_icon_SwSh.png/64px-Dark_icon_SwSh.png",
    "dragon": "https://archives.bulbagarden.net/media/upload/thumb/7/70/Dragon_icon_SwSh.png/64px-Dragon_icon_SwSh.png",
    "electric": "https://archives.bulbagarden.net/media/upload/thumb/7/7b/Electric_icon_SwSh.png/64px-Electric_icon_SwSh.png",
    "fairy": "https://archives.bulbagarden.net/media/upload/thumb/c/c6/Fairy_icon_SwSh.png/64px-Fairy_icon_SwSh.png",
    "fighting": "https://archives.bulbagarden.net/media/upload/thumb/3/3b/Fighting_icon_SwSh.png/64px-Fighting_icon_SwSh.png",
    "fire": "https://archives.bulbagarden.net/media/upload/thumb/a/ab/Fire_icon_SwSh.png/64px-Fire_icon_SwSh.png",
    "flying": "https://archives.bulbagarden.net/media/upload/thumb/b/b5/Flying_icon_SwSh.png/64px-Flying_icon_SwSh.png",
    "ghost": "https://archives.bulbagarden.net/media/upload/thumb/0/01/Ghost_icon_SwSh.png/64px-Ghost_icon_SwSh.png",
    "grass": "https://archives.bulbagarden.net/media/upload/thumb/a/a8/Grass_icon_SwSh.png/64px-Grass_icon_SwSh.png",
    "ground": "https://archives.bulbagarden.net/media/upload/thumb/2/27/Ground_icon_SwSh.png/64px-Ground_icon_SwSh.png",
    "ice": "https://archives.bulbagarden.net/media/upload/thumb/1/15/Ice_icon_SwSh.png/64px-Ice_icon_SwSh.png",
    "normal": "https://archives.bulbagarden.net/media/upload/thumb/9/95/Normal_icon_SwSh.png/64px-Normal_icon_SwSh.png",
    "poison": "https://archives.bulbagarden.net/media/upload/thumb/8/8d/Poison_icon_SwSh.png/64px-Poison_icon_SwSh.png",
    "psychic": "https://archives.bulbagarden.net/media/upload/thumb/7/73/Psychic_icon_SwSh.png/64px-Psychic_icon_SwSh.png",
    "rock": "https://archives.bulbagarden.net/media/upload/thumb/1/11/Rock_icon_SwSh.png/64px-Rock_icon_SwSh.png",
    "steel": "https://archives.bulbagarden.net/media/upload/thumb/0/09/Steel_icon_SwSh.png/64px-Steel_icon_SwSh.png",
    "water": "https://archives.bulbagarden.net/media/upload/thumb/8/80/Water_icon_SwSh.png/64px-Water_icon_SwSh.png"
}

def error_handling(func):
    """Decorator to ensure the correct chat is loaded before calling the function."""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            # Await the asynchronous function
            return await func(self, *args, **kwargs)
        
        except Exception as e:
            traceback.print_exc()
            print(f"Error in function '{func.__name__}': {e}")
        
    
    return wrapper

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def get_type_color(type):
    return DISCORD_TYPE_COLORS[type]

async def description_x_formatter(description_x, name):
    description_x = description_x.replace("\n", " ")
    description_x_list = description_x.split(" ")
    final_list = []
    for word in description_x_list:
        # Check if the word contains the Pokémon's name (case-insensitive)
        if name.lower() in word.lower():
            # Replace the Pokémon's name in the word, preserving case for the rest
            word_lower = word.lower()
            name_index = word_lower.index(name.lower())
            capitalized_name = name.lower().capitalize()
            new_word = word[:name_index] + capitalized_name + word[name_index + len(name):]
            final_list.append(new_word)
        else:
            final_list.append(word)
    final_description_x = " ".join(final_list)
    return final_description_x    

async def types_formatter(types):
    types_list = []
    for key, value in types.items():
        types_list.append(f"{TYPES_EMOJIS[value]}{value.capitalize()}")
    final_types = "\n".join(types_list)
    return final_types

async def height_weight_formatter(height, weight):
    if height >= 10:
        final_height = f"{height/10} m"
    else:
        final_height = f"{height*10} cm"
    if weight >= 10:
        final_weight = f"{weight/10} kg"
    else:
        final_weight = f"{weight*100} g"
    return final_height, final_weight

async def stats_formatter(stats):
    stats_list = []
    for key, value in stats.items():
        formatted_key = key.replace("-", " ").capitalize()
        stats_list.append(f"{formatted_key}: {value}")
    final_stats = "\n".join(stats_list)
    return final_stats

async def last_id():
    result = session.execute(select(func.max(Pokemon.id)))
    last_id = result.scalar()
    return last_id


class PokedexView(View):
    def __init__(self, current_pokemon_id):
        super().__init__()
        self.current_pokemon_id = current_pokemon_id

    @error_handling
    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.primary)
    async def previous_pokemon(self, interaction: discord.Interaction, button: Button):
        # Defer the interaction response to avoid the "interaction failed" message
        await interaction.response.defer()

        self.current_pokemon_id -= 1
        pokemon_data = await find_pokemon(self.current_pokemon_id)

        if pokemon_data is None:
            self.current_pokemon_id = await last_id()
            pokemon_data = await find_pokemon(self.current_pokemon_id)

        await pokemon_embed(pokemon_data, interaction, interaction.message)
    
    @error_handling
    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary)
    async def next_pokemon(self, interaction: discord.Interaction, button: Button):
        # Defer the interaction response to avoid the "interaction failed" message
        await interaction.response.defer()

        self.current_pokemon_id += 1
        pokemon_data = await find_pokemon(self.current_pokemon_id)

        if pokemon_data is None:
            self.current_pokemon_id = 1
            pokemon_data = await find_pokemon(self.current_pokemon_id)

        await pokemon_embed(pokemon_data, interaction, interaction.message)

@error_handling
async def pokemon_embed(pokemon_data, interaction, message=None):
    final_description = await description_formatter(pokemon_data.description, pokemon_data.name)
    final_types = await types_formatter(pokemon_data.types)
    final_height, final_weight = await height_weight_formatter(pokemon_data.height, pokemon_data.weight)
    final_stats = await stats_formatter(pokemon_data.stats)

    embed = discord.Embed(
        title=pokemon_data.name,
        description=final_description,
        color=get_type_color(pokemon_data.types["1"]),
    )
    embed.add_field(name="Types", value=final_types, inline=False)
    embed.add_field(name="Height", value=final_height, inline=True)
    embed.add_field(name="Weight", value=final_weight, inline=True)
    embed.add_field(name="Base Stats", value=final_stats, inline=False)
    embed.set_thumbnail(url=TYPE_ICONS[pokemon_data.types["1"]])
    file = discord.File(f'Pokemon_images/{pokemon_data.name}.png', filename='image.png')
    embed.set_image(url="attachment://image.png")
    view = PokedexView(pokemon_data.id)

    if message:
        # Edit the existing message with the new embed and file
        await message.edit(embed=embed, attachments=[file])
    else:
        # Send a new message if no message is provided
        message = await interaction.response.send_message(file=file, embed=embed, view=view)

    return message

async def find_pokemon(pokemon):
    try:
        pokemon = int(pokemon)
        pokemon_data = session.query(Pokemon).filter(Pokemon.id == pokemon).first()
    except:
        pokemon_data = session.query(Pokemon).filter(Pokemon.name == pokemon.capitalize()).first()

    return pokemon_data



#fuzzy search

@bot.tree.command(name='pokedex', description='Search for a Pokémon in the Pokédex')
@app_commands.describe(pokemon="Enter a Pokémon's name or ID number")
@error_handling
async def pokedex(
    interaction: discord.Interaction, 
    pokemon: app_commands.Range[str, 1, 1025]
    ):
    
    pokemon_data = await find_pokemon(pokemon)
    
    if pokemon_data is None:
        error_embed = discord.Embed(
            title="Pokémon not found",
            description="Please enter a valid Pokémon's name or ID number",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=error_embed)
        return
    await pokemon_embed(pokemon_data, interaction)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}')

# # Adicionar um novo usuário
# new_user = User(id=1, name='Carolina Johnson')
# session.add(new_user)
# session.commit()

if __name__ == "__main__":
    users = session.query(User).all()
    for user in users:
        print(user.id, user.name)

    bot.run('')


