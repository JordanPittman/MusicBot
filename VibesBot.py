# imports
from Secrets import DISCORD_TOKEN, YOUTUBE_API_KEY
from discord.ext import commands
import discord
from pytube import YouTube  # This line imports the YouTube class from the pytube library,
# which lets us interact with YouTube videos and get the info from them.
import asyncio  # Required for async sleep and loop control

CHANNEL_ID = 1216170695986384907
MUSIC_CHANNEL_ID = 1224486311449329696

# this makes it so the bot commands are recognized as starting with '!'
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Initialize YouTube API client (Didn't end up needing this with the direct streaming method.
# Downloading the YouTube songs took too much time before the song would play.)
# youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Initialize an empty list to store the playlist
playlist = []

# Variable to keep track of whether a song is currently playing
is_playing = False

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


# Command for playing music and functionality for the queue/playlist
@bot.command()
async def play(ctx, url: str):
    global is_playing

    # Check if the user is in a voice channel
    if ctx.author.voice and ctx.author.voice.channel:
        voice_channel = ctx.author.voice.channel

        # Connect to the voice channel if the bot is not already connected
        if voice_channel not in [vc.channel for vc in bot.voice_clients]:
            voice_client = await voice_channel.connect()
        else:
            voice_client = discord.utils.get(bot.voice_clients, channel=voice_channel)

        # Fetch the YouTube video
        video = YouTube(url)

        # Get the audio stream URL
        audio_url = video.streams.filter(only_audio=True).first().url

        # Get the title of the song
        title = video.title

        # Add the song to the playlist
        playlist.append((title, audio_url))

        # If no song is currently playing, play the first song in the playlist
        if not is_playing:
            await play_next(ctx, voice_client)

        # Send a message to Discord saying the song is being added to the queue
        await ctx.send(f"Added to the queue: {title}")

    else:
        await ctx.send("You need to be in a voice channel to play music.")

async def play_next(ctx, voice_client):
    global is_playing

    if not voice_client or not voice_client.is_connected():
        is_playing = False
        return
    # Attempt to try and keep the music playing if it gets interrupted (may need some tweaking)
    if playlist:
        is_playing = True
        title, audio_url = playlist.pop(0)


# Command for playing music
@bot.command()
async def play(ctx, url: str):
    if ctx.author.voice and ctx.author.voice.channel:
        voice_channel = ctx.author.voice.channel
        voice_client = discord.utils.get(bot.voice_clients, channel=voice_channel)
        if voice_client is None:
            voice_client = await voice_channel.connect()

        # Fetch the YouTube video
        video = YouTube(url)
        # Get the audio stream URL
        audio_url = video.streams.filter(only_audio=True).first().url
        # Attempt to try and keep the music playing if it gets interrupted (may need some tweaking)
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }
        source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)

        transformed_source = discord.PCMVolumeTransformer(source)

        def after_playing(error):
            fut = asyncio.run_coroutine_threadsafe(play_next(ctx, voice_client), bot.loop)
            try:
                fut.result()
            except:
                # Handle errors if needed
                pass

        voice_client.play(transformed_source, after=after_playing)
        await ctx.send(f"Now playing: {title}")
    else:
        is_playing = False
        await ctx.send("There are no more songs in the queue.")

        voice_client.play(source)
        await ctx.send(f"Now playing: {video.title}")
    else:
        await ctx.send("You need to be in a voice channel to play music.")



# gets discord token from untracked Secrets file for security
bot.run(DISCORD_TOKEN)