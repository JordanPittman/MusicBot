# Bare Bones Bot implementation

# imports
from Secrets import DISCORD_TOKEN, YOUTUBE_API_KEY
from googleapiclient.discovery import build
from discord.ext import commands
import discord  # will need more from this application
# import youtube_dl
# will need above when we get to youtube implementation

CHANNEL_ID = 1216170695986384907
MUSIC_CHANNEL_ID = 1224486311449329696

# this makes it so the bot commands are recognized as starting with '!'
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Initialize YouTube API client
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# event handler that outputs when the bot is online
@bot.event
async def on_ready():  # overrides on_ready in discord program
    print('VibesBot is ready to create a mood')
    print('VibesBot is ready to play music')
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send('VibesBot is ready to create a mood')
    await channel.send('VibesBot is ready to play music')


@bot.command()
async def hello(ctx):
    await ctx.send("Hello")

@bot.command()
async def join(ctx):
    v_channel = bot.get_channel(MUSIC_CHANNEL_ID)
    if ctx.author.voice:
        v_channel = ctx.author.voice.channel
        await v_channel.connect()
        await ctx.send("Joined the voice channel")
    else:
        await ctx.send("You are not in a voice channel")


# gets discord token from untracked Secrets file for security
bot.run(DISCORD_TOKEN)
