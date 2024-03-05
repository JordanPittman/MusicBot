#Bare Bones Bot implementation

#imports
from Secrets import DISCORD_TOKEN
import discord #will need more from this application
from discord.ext import commands
import youtube_dl #will need this when we get to youtube implementation

#this makes it so the bot commands are recognized as starting with '!'
bot = commands.Bot(command_prefix='!')

#event handler that outputs when the bot is online
@bot.event
async def on_ready(): #overrides on_ready in discord program 
    print(f'{bot.user.name} is ready to create a mood')

#gets discord token from untracked Secrets file for security
bot.run(DISCORD_TOKEN)
