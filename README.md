# Discord Pokédex Bot

A comprehensive Discord bot that provides detailed Pokémon information through an interactive Pokédex interface. Search for any Pokémon by name or ID number and get detailed stats, abilities, evolution chains, and more!

## Features

- 🔍 **Pokémon Search**: Search by name or ID number
- 📊 **Detailed Stats**: View base stats with visual progress bars
- 🌟 **Abilities**: See all abilities with descriptions
- 💥 **Type Weaknesses**: View 2× and 4× weaknesses
- ⬆️ **Evolution Chains**: Navigate through evolution lines
- 🎨 **Multiple Forms**: Support for regional forms, Mega Evolutions, Gigantamax forms, and more
- 🎮 **Interactive Navigation**: Navigate between Pokémon, evolutions, and forms with buttons
- 🖼️ **High-Quality Images**: Display Pokémon images from official sources

## Commands

### `/pokedex [pokemon]`
Search for a Pokémon by name or ID number.

**Examples:**
- `/pokedex pikachu`
- `/pokedex 25`
- `/pokedex charizard`

## Navigation Features

The bot includes interactive buttons for easy navigation:
- **◀ Previous / Next ▶**: Navigate between Pokémon by ID
- **◀ Prev Evolution / Next Evolution ▶**: Navigate through evolution chains
- **◀ Prev Form / Next Form ▶**: Switch between different forms of the same Pokémon

## Database

The bot uses SQLite to store comprehensive Pokémon data including:
- Basic information (name, ID, descriptions, height, weight)
- Types and type effectiveness
- Base stats (HP, Attack, Defense, Sp. Attack, Sp. Defense, Speed)
- Abilities with descriptions
- Evolution chains
- Multiple forms (regional variants, Mega Evolutions, Gigantamax, etc.)
- Gender information
- High-quality images

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/discord-pokedex-bot.git
cd discord-pokedex-bot
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Discord bot token:
   - **⚠️ SECURITY WARNING**: The bot token is currently hardcoded in `main.py`. 
   - Before pushing to GitHub, remove the token and use environment variables instead
   - Create a `.env` file or modify `main.py` to load the token from environment variables
   - Get your bot token from the [Discord Developer Portal](https://discord.com/developers/applications)

4. Ensure you have the `pokedex.db` database file in the project directory

5. Run the bot:
```bash
python main.py
```

## Requirements

- Python 3.7+
- discord.py
- SQLAlchemy
- tqdm

See `requirements.txt` for the complete list of dependencies.

## Project Structure

```
discord-pokedex-bot/
├── main.py              # Main bot file with commands and embed generation
├── Final_data.py        # Database models and session management
├── extract_forms.py     # Script for extracting Pokémon form data
├── pokedex.db          # SQLite database with Pokémon data
├── Pokemon_images/     # Local Pokémon image storage
├── Pokedex_html/       # HTML files for data extraction
└── Old_Stuff/          # Legacy scripts and data
```

## Features in Detail

### Pokémon Information Display
- **Type Colors**: Embed color changes based on the Pokémon's primary type
- **Type Emojis**: Visual type indicators with emojis
- **Progress Bars**: Visual representation of base stats using circle progress bars
- **Gender Icons**: Discord emoji indicators for gender
- **Evolution Highlighting**: Current Pokémon is bolded in evolution chains

### Form Support
The bot supports various Pokémon forms:
- Regional forms (Alolan, Galarian, Hisuian, Paldean)
- Mega Evolutions
- Gigantamax forms
- Primal Reversions
- Other special forms

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Pokémon data and images from [Pokémon.com](https://www.pokemon.com)
- Built with [discord.py](https://github.com/Rapptz/discord.py)

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

