# Bare Bones Bot implementation

# imports
from Secrets import DISCORD_TOKEN, YOUTUBE_API_KEY
from discord.ext import commands
import discord  # will need more from this application
# import youtube_dl
# will need above when we get to youtube implementation

CHANNEL_ID = 1216170695986384907

# this makes it so the bot commands are recognized as starting with '!'
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())


# event handler that outputs when the bot is online
@bot.event
async def on_ready():  # overrides on_ready in discord program
    print('VibesBot is ready to create a mood')
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send('VibesBot is ready to create a mood')


@bot.command()
async def hello(ctx):
    await ctx.send("Hello")


# gets discord token from untracked Secrets file for security
bot.run(DISCORD_TOKEN)
