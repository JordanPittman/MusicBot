# imports
from Secrets_template import DISCORD_TOKEN, YOUTUBE_API_KEY
from discord.ext import commands
from pytube.exceptions import RegexMatchError
import discord
import urllib.request
import re
import random
from pytube import YouTube  # This line imports the YouTube class from the pytube library,
# which lets us interact with YouTube videos and get the info from them.
import asyncio  # Required for async sleep and loop control

CHANNEL_ID = 882840879130353705
MUSIC_CHANNEL_ID = 560323369988521988

# this makes it so the bot commands are recognized as starting with '!'
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Initialize YouTube API client (Didn't end up needing this with the direct streaming method.
# Downloading the YouTube songs took too much time before the song would play.)
# youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Initialize an empty list to store the playlist
playlist = []

# Variable to keep track of whether a song is currently playing
is_playing = False

# Variable to keep track of what song is currently playing to be repeated
current_song_url = None

# Variable to keep track of the name of the currently playing song
current_song_name = None

# Variable to keep track of the  current song's requester name
current_song_requester = None

# Variable to keep track of the requester name
requester = None


# event handler that outputs when the bot is online
@bot.event
async def on_ready():  # overrides on_ready in discord program
    print('VibesBot is ready to create a mood')
    print('VibesBot is ready to play music')
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send('VibesBot is ready to create a mood')
    await channel.send('VibesBot is ready to play music')


@bot.command()
async def join(ctx):
    v_channel = bot.get_channel(MUSIC_CHANNEL_ID)
    if ctx.author.voice:
        v_channel = ctx.author.voice.channel
        await v_channel.connect()
        await ctx.send("Joined the voice channel")
    else:
        await ctx.send("You are not in a voice channel")


# lists the songs in the playlist
@bot.command(aliases=['queue'])
async def list(ctx):
    global current_song_name, is_playing, current_song_requester
    voice_client = ctx.guild.voice_client
    # error message if bot is not in voice
    if voice_client is None:
        await ctx.send("The bot is not in a voice channel")
        await ctx.send("Use the command !play and add songs then call !list again")
    elif playlist:
        await ctx.send(f"Currently Playing: {current_song_name}")
        await ctx.send(f"Requested By: {current_song_requester}")
        await ctx.send("---------------------------------------")
        n = 0
        for title in playlist:
            n += 1
            await ctx.send(f"{n}: {title[0]}")
            await ctx.send(f"Requested By: {title[2]}")
        await ctx.send("---------------------------------------")
    # error message if list is empty plus instructions
    else:
        if is_playing:
            await ctx.send(f"Currently Playing: {current_song_name}")
            await ctx.send(f"Requested By: {current_song_requester}")
            await ctx.send("---------------------------------------")
            await ctx.send("*There are no more songs in the playlist*")
            await ctx.send("Use the command !play and add songs then call !list again")
            await ctx.send("---------------------------------------")
        else:
            await ctx.send("*There are no more songs in the playlist*")
            await ctx.send("Use the command !play and add songs then call !list again")


# Command for playing music and functionality for the queue/playlist
@bot.command()
async def play(ctx, url: str = None):
    global is_playing

    voice_client = ctx.guild.voice_client

    # Check if the user is in a voice channel
    if ctx.author.voice and ctx.author.voice.channel:
        voice_channel = ctx.author.voice.channel

        # Connect to the voice channel if the bot is not already connected
        if voice_channel not in [vc.channel for vc in bot.voice_clients]:
            voice_client = await voice_channel.connect()
        else:
            voice_client = discord.utils.get(bot.voice_clients, channel=voice_channel)

        # Check if the voice client is paused
        if voice_client.is_paused():
            voice_client.resume()
            await ctx.send("Resumed the song")
            return

        # If URL is provided, play a new song
        if url:
            try:
                # Fetch the YouTube video
                video = YouTube(url)

                # Get the audio stream URL
                audio_url = video.streams.filter(only_audio=True).first().url

                # Get the title of the song
                title = video.title

                # Store the requestor name
                requester = ctx.author.name

                # Add the song to the playlist
                playlist.append((title, audio_url, requester))

                # If no song is currently playing, play the first song in the playlist
                if not is_playing:
                    await play_next(ctx, voice_client)

                # Send a message to Discord saying the song is being added to the queue
                await ctx.send(f"Added to the queue: {title}")
            except RegexMatchError:
                await ctx.send("Invalid YouTube URL. Please provide a valid YouTube video URL.")
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
        else:
            await ctx.send("Please provide a YouTube URL to play.")
    else:
        await ctx.send("You need to be in a voice channel to play music.")



@bot.command()
async def qplay(ctx, *url: str):
    global is_playing

    # Check if the user is in a voice channel
    if ctx.author.voice and ctx.author.voice.channel:
        voice_channel = ctx.author.voice.channel

        # Connect to the voice channel if the bot is not already connected
        if voice_channel not in [vc.channel for vc in bot.voice_clients]:
            voice_client = await voice_channel.connect()
        else:
            voice_client = discord.utils.get(bot.voice_clients, channel=voice_channel)

        # searches the youtube url with + instead of spaces to fit the url format
        nospaceurl = '+'.join(url)
        # inserting youtube search here
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + nospaceurl)
        vlink = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        newurl = ("https://www.youtube.com/watch?v=" + vlink[0])

        # Fetch the YouTube video
        video = YouTube(newurl)

        # Get the audio stream URL
        audio_url = video.streams.filter(only_audio=True).first().url

        # Get the title of the song
        title = video.title

        # Store the requestor name
        requester = ctx.author.name

        # Add the song to the playlist
        playlist.append((title, audio_url, requester))

        # If no song is currently playing, play the first song in the playlist
        if not is_playing:
            await play_next(ctx, voice_client)

        # Send a message to Discord saying the song is being added to the queue
        await ctx.send(f"Added to the queue: {title}")

    else:
        await ctx.send("You need to be in a voice channel to play music.")


# Stop the current song
@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client
    # if the bot is not connected to a voice channel or it is not playing a song
    if not voice_client or not voice_client.is_playing():
        # send a bot error message
        await ctx.send("No song to be stopped")
    else:
        # stop the song
        voice_client.stop()


async def play_next(ctx, voice_client):
    global is_playing, current_song_url, current_song_name, current_song_requester

    if not voice_client or not voice_client.is_connected():
        is_playing = False
        return
    # Attempt to try and keep the music playing if it gets interrupted (may need some tweaking)
    if playlist:
        is_playing = True
        title, audio_url, requester = playlist.pop(0)

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }

        # Log before executing ffmpeg command
        print(f"Executing ffmpeg command with URL: {audio_url}")

        try:
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
            current_song_url = audio_url
            current_song_name = title
            current_song_requester = requester

            await ctx.send(f"Now playing: {title}")
            await ctx.send(f"Requested by: {current_song_requester}")

        except discord.errors.ClientException as e:
            print(f"ClientException: {e}")
            await ctx.send(f"Error playing {title}: {e}")
    else:
        is_playing = False
        await ctx.send("There are no more songs in the queue.")



# Skip a song
@bot.command()
async def skip(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()  # This stops the current song and triggers the after callback
    else:
        await ctx.send("There's no song currently playing.")


# Pause a song
@bot.command()
async def pause(ctx):
    voice_client = ctx.voice_client;
    if voice_client and voice_client.is_playing():
        voice_client.pause()  # Pauses song
        await ctx.send("Your song is now paused")
    elif voice_client and voice_client.is_paused():
        voice_client.resume()  # Resumes again
        await ctx.send("Your song has resumed playing")



# Clear song queue
@bot.command()
async def clear(ctx):
    global playlist, is_playing
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()  # Stop the currently playing song
        playlist = []  # Clear the playlist
        is_playing = False
        await ctx.send("Playback stopped and the queue has been cleared.")
    elif playlist:
        playlist = []  # Clear the playlist if there's no song currently playing but the queue is not empty
        is_playing = False
        await ctx.send("The queue has been cleared.")
    else:
        await ctx.send("The queue is already empty.")


@bot.command()
async def repeat(ctx):
    global current_song_url, current_song_name, is_playing
    if is_playing:
        # Add the currently playing song back to the playlist
        playlist.insert(0, (current_song_name, current_song_url))
        await ctx.send(f"{current_song_name} added to the top of the list")
    else:
        await ctx.send("There's no song currently playing.")


@bot.command()
async def shuffle(ctx):
    voice_client = ctx.guild.voice_client
    if not voice_client or not voice_client.is_connected():
        await ctx.send("I need to be in a voice channel to shuffle the playlist.")
        return

    if len(playlist) > 1:  # Check if there are at least two songs to shuffle
        random.shuffle(playlist)
        await ctx.send("Shuffled the playlist!")
    else:
        await ctx.send("Not enough songs in the playlist to shuffle.")


@bot.command()
async def volume(ctx, volume: int):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.source.volume = volume / 100
        await ctx.send(f"Volume set to {volume}%")
    else:
        await ctx.send("Nothing is playing right now.")


@bot.command()
async def plz_help(ctx):
    await ctx.send("!join - joins voice channel")
    await ctx.send("!play [insert desired song] - will play a song or add to the queue")
    await ctx.send("!leave - leaves voice channel")
    await ctx.send("!qplay [song title] - adds to the queue")
    await ctx.send("!shuffle - shuffles the song queue if there are 2 or more songs")
    await ctx.send("!volume [0-100] - sets the volume to a specified level")


@bot.command()
async def leave(ctx):
    voice_client = ctx.guild.voice_client

    if voice_client is not None:
        await voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not connected to a voice channel.")


# gets discord token from untracked Secrets file for security
bot.run(DISCORD_TOKEN)
