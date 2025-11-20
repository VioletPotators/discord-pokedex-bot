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
import json

from Final_data import session, Pokemon

# Helper function to parse JSON fields
def parse_json_field(field_value):
    if isinstance(field_value, (list, dict)):
        return field_value
    try:
        return json.loads(field_value) if isinstance(field_value, str) else eval(str(field_value))
    except:
        return field_value

def error_handling(func):
    """Decorator to handle errors in async functions."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Await the asynchronous function
            return await func(*args, **kwargs)
        
        except Exception as e:
            traceback.print_exc()
            print(f"Error in function '{func.__name__}': {e}")
            # Try to send error message if it's a Discord interaction
            if args and isinstance(args[0], discord.Interaction):
                try:
                    error_embed = discord.Embed(
                        title="Error",
                        description=f"An error occurred: {str(e)}",
                        color=discord.Color.red()
                    )
                    if args[0].response.is_done():
                        await args[0].followup.send(embed=error_embed)
                    else:
                        await args[0].response.send_message(embed=error_embed)
                except:
                    pass
        
    return wrapper

class PokemonNavigationView(View):
    """View with buttons for navigating between Pokemon"""
    
    def __init__(self, pokemon_data):
        super().__init__(timeout=300)  # 5 minute timeout
        self.pokemon_data = pokemon_data
        
        # Create buttons
        prev_pokemon_btn = Button(label="◀ Previous", style=discord.ButtonStyle.secondary, row=0)
        next_pokemon_btn = Button(label="Next ▶", style=discord.ButtonStyle.secondary, row=0)
        
        # Connect buttons to callbacks
        prev_pokemon_btn.callback = self.button_prev_pokemon
        next_pokemon_btn.callback = self.button_next_pokemon
        
        # Add buttons to view
        self.add_item(prev_pokemon_btn)
        self.add_item(next_pokemon_btn)
        
        # Check if Pokemon has evolutions (more than just itself)
        has_evolutions = self.has_evolutions()
        if has_evolutions:
            prev_evo_btn = Button(label="◀ Prev Evolution", style=discord.ButtonStyle.primary, row=1)
            next_evo_btn = Button(label="Next Evolution ▶", style=discord.ButtonStyle.primary, row=1)
            prev_evo_btn.callback = self.button_prev_evolution
            next_evo_btn.callback = self.button_next_evolution
            self.add_item(prev_evo_btn)
            self.add_item(next_evo_btn)
        
        # Check if Pokemon has multiple forms
        forms = self.get_all_forms()
        if len(forms) > 1:
            prev_form_btn = Button(label="◀ Prev Form", style=discord.ButtonStyle.success, row=2 if has_evolutions else 1)
            next_form_btn = Button(label="Next Form ▶", style=discord.ButtonStyle.success, row=2 if has_evolutions else 1)
            prev_form_btn.callback = self.button_prev_form
            next_form_btn.callback = self.button_next_form
            self.add_item(prev_form_btn)
            self.add_item(next_form_btn)
    
    def get_base_id(self):
        """Extract base ID from Pokemon ID (removes 'f' suffix if present)"""
        pokemon_id = self.pokemon_data.id
        if 'f' in pokemon_id:
            return pokemon_id.split('f')[0]
        return pokemon_id
    
    def get_all_forms(self):
        """Get all forms of the current Pokemon"""
        base_id = self.get_base_id()
        # Find all Pokemon with IDs matching base_id, base_idf2, base_idf3, etc.
        forms = []
        # First, try the base ID
        base_pokemon = session.query(Pokemon).filter(Pokemon.id == base_id).first()
        if base_pokemon:
            forms.append(base_pokemon)
        
        # Then try forms with f suffix (starting from f2)
        form_index = 2
        while form_index <= 20:  # Safety limit
            form_id = f"{base_id}f{form_index}"
            form_pokemon = session.query(Pokemon).filter(Pokemon.id == form_id).first()
            if form_pokemon:
                forms.append(form_pokemon)
                form_index += 1
            else:
                break
        
        # Ensure current Pokemon is in the list
        current_in_list = any(form.id == self.pokemon_data.id for form in forms)
        if not current_in_list:
            forms.append(self.pokemon_data)
        
        # Sort forms by ID to maintain order (base, then f2, f3, etc.)
        def sort_key(x):
            if 'f' in str(x.id):
                parts = str(x.id).split('f')
                try:
                    return (int(parts[0]), int(parts[1]))
                except ValueError:
                    return (parts[0], int(parts[1]) if len(parts) > 1 else 0)
            else:
                try:
                    return (int(x.id), 0)
                except ValueError:
                    return (x.id, 0)
        
        forms.sort(key=sort_key)
        
        return forms
    
    def has_evolutions(self):
        """Check if Pokemon has evolutions (more than just itself)"""
        try:
            evolution_chain = self.pokemon_data.evolution_chain
            if isinstance(evolution_chain, str):
                evolution_chain = json.loads(evolution_chain)
            elif not isinstance(evolution_chain, dict):
                evolution_chain = parse_json_field(evolution_chain)
            
            # Build list of all Pokemon in evolution chain
            evolution_list = []
            if evolution_chain.get('first'):
                evolution_list.append(evolution_chain['first']['name'])
            if evolution_chain.get('middle'):
                for mon in evolution_chain['middle']:
                    evolution_list.append(mon['name'])
            if evolution_chain.get('last'):
                for mon in evolution_chain['last']:
                    evolution_list.append(mon['name'])
            
            # If there's more than one Pokemon in the chain, it has evolutions
            return len(evolution_list) > 1
        except:
            return False
    
    @error_handling
    async def get_next_pokemon_by_id(self, current_id, direction=1):
        """Get next or previous Pokemon by ID (uses base ID for navigation)"""
        try:
            # Get base ID (remove 'f' suffix if present)
            base_id = current_id.split('f')[0] if 'f' in current_id else current_id
            current_id_int = int(base_id)
            next_id = str(current_id_int + direction)
            
            # Check if Pokemon exists (prefer base form, but return any form if base doesn't exist)
            next_pokemon = session.query(Pokemon).filter(Pokemon.id == next_id).first()
            if next_pokemon:
                return next_pokemon
            
            # If base form doesn't exist, try to find any form with that base ID
            # This handles cases where the next Pokemon only has forms
            form_index = 2
            while True:
                form_id = f"{next_id}f{form_index}"
                form_pokemon = session.query(Pokemon).filter(Pokemon.id == form_id).first()
                if form_pokemon:
                    return form_pokemon
                form_index += 1
                if form_index > 10:  # Safety limit
                    break
        except:
            pass
        return None
    
    @error_handling
    async def get_next_evolution(self, current_name, evolution_chain, direction=1):
        """Get next or previous Pokemon in evolution chain"""
        try:
            # Build list of all Pokemon in evolution chain in order
            evolution_list = []
            
            if evolution_chain.get('first'):
                evolution_list.append(evolution_chain['first']['name'])
            
            if evolution_chain.get('middle'):
                for mon in evolution_chain['middle']:
                    evolution_list.append(mon['name'])
            
            if evolution_chain.get('last'):
                for mon in evolution_chain['last']:
                    evolution_list.append(mon['name'])
            
            # Find current Pokemon index
            try:
                current_index = evolution_list.index(current_name)
                next_index = current_index + direction
                
                # Check if next index is valid
                if 0 <= next_index < len(evolution_list):
                    next_name = evolution_list[next_index]
                    next_pokemon = session.query(Pokemon).filter(Pokemon.name == next_name).first()
                    return next_pokemon
            except ValueError:
                pass
        except:
            pass
        return None
    
    @error_handling
    async def button_next_pokemon(self, interaction: discord.Interaction):
        """Button callback for next Pokemon by ID"""
        await interaction.response.defer()
        next_pokemon = await self.get_next_pokemon_by_id(self.pokemon_data.id, 1)
        if next_pokemon:
            # Create new view with updated pokemon data
            new_view = PokemonNavigationView(next_pokemon)
            await pokemon_embed(next_pokemon, interaction, interaction.message, new_view)
        else:
            await interaction.followup.send("No next Pokemon found!", ephemeral=True)
    
    @error_handling
    async def button_prev_pokemon(self, interaction: discord.Interaction):
        """Button callback for previous Pokemon by ID"""
        await interaction.response.defer()
        prev_pokemon = await self.get_next_pokemon_by_id(self.pokemon_data.id, -1)
        if prev_pokemon:
            # Create new view with updated pokemon data
            new_view = PokemonNavigationView(prev_pokemon)
            await pokemon_embed(prev_pokemon, interaction, interaction.message, new_view)
        else:
            await interaction.followup.send("No previous Pokemon found!", ephemeral=True)
    
    @error_handling
    async def button_next_evolution(self, interaction: discord.Interaction):
        """Button callback for next evolution"""
        await interaction.response.defer()
        evolution_chain = self.pokemon_data.evolution_chain
        if isinstance(evolution_chain, str):
            evolution_chain = json.loads(evolution_chain)
        elif not isinstance(evolution_chain, dict):
            evolution_chain = parse_json_field(evolution_chain)
        
        next_evo = await self.get_next_evolution(self.pokemon_data.name, evolution_chain, 1)
        if next_evo:
            # Create new view with updated pokemon data
            new_view = PokemonNavigationView(next_evo)
            await pokemon_embed(next_evo, interaction, interaction.message, new_view)
        else:
            await interaction.followup.send("No next evolution found!", ephemeral=True)
    
    @error_handling
    async def button_prev_evolution(self, interaction: discord.Interaction):
        """Button callback for previous evolution"""
        await interaction.response.defer()
        evolution_chain = self.pokemon_data.evolution_chain
        if isinstance(evolution_chain, str):
            evolution_chain = json.loads(evolution_chain)
        elif not isinstance(evolution_chain, dict):
            evolution_chain = parse_json_field(evolution_chain)
        
        prev_evo = await self.get_next_evolution(self.pokemon_data.name, evolution_chain, -1)
        if prev_evo:
            # Create new view with updated pokemon data
            new_view = PokemonNavigationView(prev_evo)
            await pokemon_embed(prev_evo, interaction, interaction.message, new_view)
        else:
            await interaction.followup.send("No previous evolution found!", ephemeral=True)
    
    @error_handling
    async def get_next_form(self, direction=1):
        """Get next or previous form of the current Pokemon"""
        forms = self.get_all_forms()
        if len(forms) <= 1:
            return None
        
        # Find current form index
        try:
            current_id = str(self.pokemon_data.id)
            current_index = None
            for i, form in enumerate(forms):
                if str(form.id) == current_id:
                    current_index = i
                    break
            
            if current_index is None:
                # Current Pokemon not found in forms list, return first form
                return forms[0] if direction > 0 else forms[-1]
            
            next_index = current_index + direction
            
            # Wrap around if needed
            if next_index < 0:
                next_index = len(forms) - 1
            elif next_index >= len(forms):
                next_index = 0
            
            return forms[next_index]
        except (StopIteration, IndexError, AttributeError) as e:
            print(f"Error in get_next_form: {e}")
            return None
    
    @error_handling
    async def button_next_form(self, interaction: discord.Interaction):
        """Button callback for next form"""
        await interaction.response.defer()
        try:
            forms = self.get_all_forms()
            print(f"Debug: Found {len(forms)} forms for Pokemon {self.pokemon_data.id}")
            if len(forms) > 1:
                next_form = await self.get_next_form(1)
                if next_form:
                    print(f"Debug: Navigating to form {next_form.id}")
                    # Create new view with updated pokemon data
                    new_view = PokemonNavigationView(next_form)
                    await pokemon_embed(next_form, interaction, interaction.message, new_view)
                else:
                    await interaction.followup.send("No next form found!", ephemeral=True)
            else:
                await interaction.followup.send("This Pokemon doesn't have multiple forms!", ephemeral=True)
        except Exception as e:
            print(f"Error in button_next_form: {e}")
            traceback.print_exc()
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)
    
    @error_handling
    async def button_prev_form(self, interaction: discord.Interaction):
        """Button callback for previous form"""
        await interaction.response.defer()
        try:
            forms = self.get_all_forms()
            print(f"Debug: Found {len(forms)} forms for Pokemon {self.pokemon_data.id}")
            if len(forms) > 1:
                prev_form = await self.get_next_form(-1)
                if prev_form:
                    print(f"Debug: Navigating to form {prev_form.id}")
                    # Create new view with updated pokemon data
                    new_view = PokemonNavigationView(prev_form)
                    await pokemon_embed(prev_form, interaction, interaction.message, new_view)
                else:
                    await interaction.followup.send("No previous form found!", ephemeral=True)
            else:
                await interaction.followup.send("This Pokemon doesn't have multiple forms!", ephemeral=True)
        except Exception as e:
            print(f"Error in button_prev_form: {e}")
            traceback.print_exc()
            await interaction.followup.send(f"An error occurred: {str(e)}", ephemeral=True)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@error_handling
async def find_pokemon(pokemon):
    try:
        pokemon = int(pokemon)
        pokemon = str(pokemon)
        pokemon_data = session.query(Pokemon).filter(Pokemon.id == pokemon).first()
    except:
        pokemon_data = session.query(Pokemon).filter(Pokemon.name == pokemon.capitalize()).first()
    
    return pokemon_data

# Progress bar helper function - Circle style
# Uses max_value=15 for Pokémon stats
def create_progress_bar_circles(value, max_value=15, bar_length=10):
    """Circle-based progress bar"""
    filled = int((value / max_value) * bar_length)
    bar = "●" * filled + "○" * (bar_length - filled)
    return f"{bar}"


@bot.tree.command(name='pokedex', description='Search for a Pokémon in the Pokédex')
@app_commands.describe(pokemon="Enter a Pokémon's name or ID number")
@error_handling
async def pokedex(
    interaction: discord.Interaction, 
    pokemon: app_commands.Range[str, 1, 1300]
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

@error_handling
async def pokemon_embed(pokemon_data, interaction, message=None, view=None):
    
    # Parse JSON fields
    types = parse_json_field(pokemon_data.types)
    stats = parse_json_field(pokemon_data.stats)
    abilities = parse_json_field(pokemon_data.abilities)
    weaknesses_4x = parse_json_field(pokemon_data.weaknesses_4X)
    weaknesses_2x = parse_json_field(pokemon_data.weaknesses_2X)
    evolution_chain = parse_json_field(pokemon_data.evolution_chain)
    
    # Get type colors
    type_colors = {
        "Grass": 0x7CFC00, "Fire": 0xFF4500, "Water": 0x0000FF, "Electric": 0xFFFF00,
        "Psychic": 0x9370DB, "Rock": 0x8B4513, "Ground": 0xD2691E, "Flying": 0x87CEEB,
        "Ice": 0x00CED1, "Ghost": 0x663399, "Normal": 0xA9A9A9, "Fighting": 0x8B0000,
        "Poison": 0x800080, "Steel": 0x708090, "Dragon": 0x4169E1, "Dark": 0x000000,
        "Fairy": 0xFFB6C1, "Bug": 0x9ACD32
    }
    
    # Determine embed color based on primary type
    embed_color = type_colors.get(types[0], discord.Color.default())
    if isinstance(embed_color, int):
        embed_color = discord.Color(embed_color)
    
    # Create embed
    embed = discord.Embed(
        title=f"{pokemon_data.id} | {pokemon_data.name}",
        description=pokemon_data.description_x if pokemon_data.description_x else "",
        color=embed_color
    )
    
    # Set thumbnail
    if pokemon_data.image:
        embed.set_image(url=pokemon_data.image)
    
    # Type emojis
    type_emojis = {
        "Grass": "🌿", "Fire": "🔥", "Water": "💧", "Electric": "⚡", "Psychic": "🔮",
        "Rock": "🪨", "Ground": "🌍", "Flying": "🪽", "Ice": "❄️", "Ghost": "👻",
        "Normal": "⚪", "Fighting": "👊", "Poison": "☠️", "Steel": "⚙️", "Dragon": "🐉",
        "Dark": "🌑", "Fairy": "✨", "Bug": "🐛"
    }
    # Weaknesses
    if weaknesses_4x or weaknesses_2x:
        weaknesses_text = []
        if weaknesses_4x:
            weaknesses_formatted = [f"{type_emojis.get(w, '🌐')} {w}" for w in weaknesses_4x]
            weaknesses_text.append("**4×:** " + "\n".join(weaknesses_formatted))
        if weaknesses_2x:
            weaknesses_formatted = [f"{type_emojis.get(w, '🌐')} {w}" for w in weaknesses_2x]
            weaknesses_text.append("**2×:** " + "\n".join(weaknesses_formatted))
        embed.add_field(name="💥 Weaknesses", value="\n".join(weaknesses_text), inline=True)
    # Types field
    types_display = "\n".join([type_emojis.get(t, "🌐") + f" {t}" for t in types])
    embed.add_field(name="Type(s)", value=types_display, inline=True)
    
    
    embed.add_field(name="ㅤ", value="ㅤ", inline=False)
    # Gender
    gender = pokemon_data.gender
    gender_list = gender.split(" ")
    if "Male" in gender_list:
        gender_list[0] = gender_list[0] + " :male_sign:"
    if "Female" in gender_list:
        for i, genero in enumerate(gender_list):
            if genero == "Female":
                gender_list[i] = gender_list[i] + " :female_sign:"
    elif "Unknown" in gender_list:
        gender_list[0] = gender_list[0] + " :grey_question:"

    embed.add_field(name="Gender", value="\n".join(gender_list) or "Unknown :grey_question:", inline=True)
    # Height and Weight
    embed.add_field(name="Height", value=f"{pokemon_data.height}", inline=True)
    embed.add_field(name="Weight", value=f"{pokemon_data.weight}", inline=True)
    
    # Base Stats with Progress Bars (Circle style)
    progress_bar_func = create_progress_bar_circles
    
    def format_stat(stat_name, stat_value):
        if stat_value == 'N/A' or stat_value is None:
            return f"**{stat_name}:** N/A"
        try:
            stat_value = int(stat_value)
            return f"**{stat_name}:** {progress_bar_func(stat_value, max_value=15)}"
        except:
            return f"**{stat_name}:** {stat_value}"
    
    stats_text = (
        f"{format_stat('HP', stats.get('HP', 'N/A'))}\n"
        f"{format_stat('ATK', stats.get('Attack', 'N/A'))}\n"
        f"{format_stat('DEF', stats.get('Defense', 'N/A'))}\n"
        f"{format_stat('Sp.ATK', stats.get('Sp. Attack', 'N/A'))}\n"
        f"{format_stat('Sp.DEF', stats.get('Sp. Defense', 'N/A'))}\n"
        f"{format_stat('SPE', stats.get('Speed', 'N/A'))}"
    )
    embed.add_field(name="📊 Base Stats", value=stats_text, inline=False)
    
    # Abilities - Deduplicate by name
    seen_abilities = {}
    unique_abilities = []
    for ab in abilities:
        ability_name = ab.get('name', '')
        if ability_name and ability_name not in seen_abilities:
            seen_abilities[ability_name] = True
            unique_abilities.append(ab)
    
    abilities_text = "\n".join([f"• **{ab['name']}** - {ab['description']}" for ab in unique_abilities])
    embed.add_field(name="🌟 Abilities", value=abilities_text[:1024], inline=False)
    
    # Evolution Chain
    evol_text_parts = []
    if evolution_chain.get('first'):
        if pokemon_data.name == evolution_chain['first']['name']:
            evol_text_parts.append(f"**{evolution_chain['first']['name']}**")
        else:
            evol_text_parts.append(evolution_chain['first']['name'])
    if evolution_chain.get('middle'):
        for mon in evolution_chain['middle']:
            if pokemon_data.name == mon['name']:
                evol_text_parts.append(f"**{mon['name']}**")
            else:
                evol_text_parts.append(mon['name'])
    if evolution_chain.get('last'):
        for mon in evolution_chain['last']:
            if pokemon_data.name == mon['name']:
                evol_text_parts.append(f"**{mon['name']}**")
            else:
                evol_text_parts.append(mon['name'])
    
    if evol_text_parts:
        # Use a faded/greyed out appearance for the field name
        # Using a lighter emoji and text styling to create faded effect
        # The field name will appear lighter in Discord embeds
        embed.add_field(name="🚀Evolution Line", value=" → ".join(evol_text_parts), inline=False)
    
    # Footer
    embed.set_footer(text="Pokédex Data")
    embed.timestamp = datetime.now()
    
    # Create view if not provided
    if view is None:
        view = PokemonNavigationView(pokemon_data)
    
    # Send embed
    if message is None:
        await interaction.response.send_message(embed=embed, view=view)
    else:
        await message.edit(embed=embed, view=view)


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}')


bot.run('')