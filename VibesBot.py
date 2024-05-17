# imports
from Secrets_template import DISCORD_TOKEN, YOUTUBE_API_KEY
from discord.ext import commands
from pytube.exceptions import RegexMatchError
import discord
import urllib.request
import re
import random
import yt_dlp
import asyncio

# Set the path to the ffmpeg binary
ffmpeg_path = '/app/vendor/ffmpeg/ffmpeg'
CHANNEL_ID = 882840879130353705
MUSIC_CHANNEL_ID = 560323369988521988

# this makes it so the bot commands are recognized as starting with '!'
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

# Initialize an empty list to store the playlist
playlist = []

# Variables to keep track of the current state
is_playing = False
current_song_url = None
current_song_name = None
current_song_requester = None

# event handler that outputs when the bot is online
@bot.event
async def on_ready():
    print('SlugBeats is ready to play music')
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send('SlugBeats is ready to play music')

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        v_channel = ctx.author.voice.channel
        await v_channel.connect()
        await ctx.send("Joined the voice channel")
    else:
        await ctx.send("You are not in a voice channel")

@bot.command(aliases=['queue'])
async def list(ctx):
    global current_song_name, is_playing, current_song_requester
    voice_client = ctx.guild.voice_client
    if voice_client is None:
        await ctx.send("The bot is not in a voice channel")
        await ctx.send("Use the command !play and add songs then call !list again")
    elif playlist:
        await ctx.send(f"Currently Playing: {current_song_name}")
        await ctx.send(f"Requested By: {current_song_requester}")
        await ctx.send("---------------------------------------")
        for n, title in enumerate(playlist, start=1):
            await ctx.send(f"{n}: {title[0]}")
            await ctx.send(f"Requested By: {title[2]}")
        await ctx.send("---------------------------------------")
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

@bot.command()
async def play(ctx, url: str = None):
    global is_playing
    voice_client = ctx.guild.voice_client

    if ctx.author.voice and ctx.author.voice.channel:
        voice_channel = ctx.author.voice.channel

        if voice_channel not in [vc.channel for vc in bot.voice_clients]:
            voice_client = await voice_channel.connect()
        else:
            voice_client = discord.utils.get(bot.voice_clients, channel=voice_channel)

        if voice_client.is_paused():
            voice_client.resume()
            await ctx.send("Resumed the song")
            return

        if url:
            try:
                # Use yt-dlp to fetch the audio stream URL
                ydl_opts = {'format': 'bestaudio/best'}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(url, download=False)
                    audio_url = info_dict['url']
                    title = info_dict.get('title', 'Unknown title')
                    requester = ctx.author.name

                playlist.append((title, audio_url, requester))

                if not is_playing:
                    await play_next(ctx, voice_client)

                await ctx.send(f"Added to the queue: {title}")
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
        else:
            await ctx.send("Please provide a YouTube URL to play.")
    else:
        await ctx.send("You need to be in a voice channel to play music.")

@bot.command()
async def qplay(ctx, *url: str):
    global is_playing

    if ctx.author.voice and ctx.author.voice.channel:
        voice_channel = ctx.author.voice.channel

        if voice_channel not in [vc.channel for vc in bot.voice_clients]:
            voice_client = await voice_channel.connect()
        else:
            voice_client = discord.utils.get(bot.voice_clients, channel=voice_channel)

        nospaceurl = '+'.join(url)
        html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + nospaceurl)
        vlink = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        newurl = ("https://www.youtube.com/watch?v=" + vlink[0])

        try:
            ydl_opts = {'format': 'bestaudio/best'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(newurl, download=False)
                audio_url = info_dict['url']
                title = info_dict.get('title', 'Unknown title')
                requester = ctx.author.name

            playlist.append((title, audio_url, requester))

            if not is_playing:
                await play_next(ctx, voice_client)

            await ctx.send(f"Added to the queue: {title}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
    else:
        await ctx.send("You need to be in a voice channel to play music.")

@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client
    if not voice_client or not voice_client.is_playing():
        await ctx.send("No song to be stopped")
    else:
        voice_client.stop()

async def play_next(ctx, voice_client):
    global is_playing, current_song_url, current_song_name, current_song_requester

    if not voice_client or not voice_client.is_connected():
        is_playing = False
        return

    if playlist:
        is_playing = True
        title, audio_url, requester = playlist.pop(0)

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }

        print(f"Executing ffmpeg command with URL: {audio_url}")

        try:
            source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options, executable=ffmpeg_path)
            transformed_source = discord.PCMVolumeTransformer(source)

            def after_playing(error):
                fut = asyncio.run_coroutine_threadsafe(play_next(ctx, voice_client), bot.loop)
                try:
                    fut.result()
                except Exception as e:
                    print(f"Error in after_playing: {e}")

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

@bot.command()
async def skip(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
    else:
        await ctx.send("There's no song currently playing.")

@bot.command()
async def pause(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Your song is now paused")
    elif voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Your song has resumed playing")

@bot.command()
async def clear(ctx):
    global playlist, is_playing
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        playlist = []
        is_playing = False
        await ctx.send("Playback stopped and the queue has been cleared.")
    elif playlist:
        playlist = []
        is_playing = False
        await ctx.send("The queue has been cleared.")
    else:
        await ctx.send("The queue is already empty.")

@bot.command()
async def repeat(ctx):
    global current_song_url, current_song_name, is_playing
    if is_playing:
        playlist.insert(0, (current_song_name, current_song_url, current_song_requester))
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
    await ctx.send("!stop - stops the current song")
    await ctx.send("!skip - skips the current song")
    await ctx.send("!pause - pauses or resumes the current song")
    await ctx.send("!clear - clears the song queue")
    await ctx.send("!repeat - repeats the current song")

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
