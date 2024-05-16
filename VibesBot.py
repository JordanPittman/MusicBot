from Secrets_template import DISCORD_TOKEN
from discord.ext import commands
import discord
import random
from pytube import YouTube
import asyncio

CHANNEL_ID = 882840879130353705
MUSIC_CHANNEL_ID = 560323369988521988

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

playlist = []
is_playing = False
current_song_url = None
current_song_name = None
current_song_requester = None

@bot.event
async def on_ready():
    print('VibesBot is ready to create a mood')
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send('VibesBot is ready to create a mood')

@bot.command()
async def join(ctx):
    v_channel = ctx.author.voice.channel if ctx.author.voice else None
    if v_channel:
        await v_channel.connect()
        await ctx.send("Joined the voice channel")
    else:
        await ctx.send("You are not in a voice channel")

@bot.command(aliases=['queue'])
async def list(ctx):
    if playlist:
        await ctx.send(f"Currently Playing: {current_song_name}\nRequested By: {current_song_requester}\n" + 
                       "\n".join(f"{i+1}: {title[0]} (Requested By: {title[2]})" for i, title in enumerate(playlist)))
    else:
        await ctx.send("The playlist is empty.")

@bot.command()
async def play(ctx, url: str = None):
    global is_playing

    if ctx.author.voice and ctx.author.voice.channel:
        voice_channel = ctx.author.voice.channel
        if voice_channel not in [vc.channel for vc in bot.voice_clients]:
            await voice_channel.connect()

        if url:
            video = YouTube(url)
            audio_url = video.streams.filter(only_audio=True).first().url
            title = video.title
            requester = ctx.author.name
            playlist.append((title, audio_url, requester))

            if not is_playing:
                await play_next(ctx)
            await ctx.send(f"Added to the queue: {title}")
        else:
            await ctx.send("Please provide a YouTube URL to play.")
    else:
        await ctx.send("You need to be in a voice channel to play music.")

async def play_next(ctx):
    global is_playing, current_song_url, current_song_name, current_song_requester

    voice_client = ctx.guild.voice_client

    if not playlist:
        is_playing = False
        return

    is_playing = True
    title, audio_url, requester = playlist.pop(0)
    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    def after_playing(error):
        fut = asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
        try:
            fut.result()
        except Exception as e:
            print(f"Error in after_playing: {e}")

    source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
    transformed_source = discord.PCMVolumeTransformer(source)

    voice_client.play(transformed_source, after=after_playing)
    current_song_url = audio_url
    current_song_name = title
    current_song_requester = requester

    await ctx.send(f"Now playing: {title}\nRequested by: {requester}")

@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
    else:
        await ctx.send("No song to be stopped")

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
    if len(playlist) > 1:
        random.shuffle(playlist)
        await ctx.send("Shuffled the playlist!")
    else:
        await ctx.send("Not enough songs in the playlist to shuffle.")

@bot.command()
async def volume(ctx, volume: int):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.source.volume = volume / 100
        await ctx.send(f"Volume set to {volume}%")
    else:
        await ctx.send("Nothing is playing right now.")

@bot.command()
async def leave(ctx):
    voice_client = ctx.voice_client
    if voice_client:
        await voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not connected to a voice channel.")

bot.run(DISCORD_TOKEN)
