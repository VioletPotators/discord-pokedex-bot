import discord
from discord.ext import commands

# Create a bot instance
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
# Define a command to send the image
@bot.command(name='send_image')
async def send_image(ctx):
    image_path = r'Pokemon_images\374.png'

    # Open the image file
    with open(image_path, 'rb') as f:
        # Create a discord.File object
        file = discord.File(f, filename='image.png')

        # Create an embed
        embed = discord.Embed(title="Here's an image!")

        # Set the image URL to the attachment's URL
        embed.set_image(url="attachment://image.png")

        # Send the embed with the file
        await ctx.send(file=file, embed=embed)
# Run the bot with your token

bot.run('')
