import discord
from discord.ext import commands, tasks
from discord.voice_client import VoiceClient
import youtube_dl
from random import choice
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import random
import time
import os
import logging

logging.basicConfig(filename = 'bot.log', level = logging.INFO)

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


client = commands.Bot(command_prefix='-')
token = token  #This is where you put the bots token

txt = open('beats.txt', 'r')
list_lines = txt.readlines()
beats = []
for i in list_lines:
    beats.append(i)

status = ['Listening to music', '-help']
candle_songs = ["", "lose me pt. 1 (nikki's song).mp3", "insanity defense freestyle.mp3", "dead feelings freestyle.mp3", "alter ego (prod. pythoN).mp3"]

@client.event
async def on_ready():
    change_status.start()
    print('Bot is online')
    logging.info('Bot is online')

@client.command(name='beat', help='play a random beat')
async def beat(ctx):
    server = ctx.message.guild

    if not ctx.message.author.voice:
        await ctx.send('User is not in a channel.')
        return

    else:
        try:
            channel = ctx.message.author.voice.channel
        
            await channel.connect()

            server = ctx.message.guild
            voice_channel = server.voice_client
            url = random.choice(beats)

            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=client.loop)
                voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

            await ctx.send('**Now playing:** {}'.format(player.title))
            print(str(server) + " [" + str(ctx.message.author) + "] = " + '**Now playing:** {}'.format(player.title))
            logging.info(str(server) + " [" + str(ctx.message.author) + "] = " + '**Now playing:** {}'.format(player.title))


        except:

            await ctx.send('Already playing')
            print(str(server) + " [" + str(ctx.message.author) + "] = " + 'Already Playing')
            logging.info(str(server) + " [" + str(ctx.message.author) + "] = " + 'Already Playing')

@client.command(name='play', help='plays one of candlesticks songs, ex: -play 1')
async def play(ctx, songnum):

    server = ctx.message.guild
    voice_channel = server.voice_client
    channel = ctx.message.author=voice_channel
    print(str(server) + " [" + str(ctx.message.author) + "] = " + 'play ' + songnum)
    logging.info(str(server) + " [" + str(ctx.message.author) + "] = " + 'play ' + songnum)
    # only play music if user is in a voice channel
    if channel!= None:
        try:
            vc = await channel.connect()
            async with ctx.typing():
                int_songnum = int(songnum)
                vc.play(discord.FFmpegPCMAudio(candle_songs[int_songnum]))
        except:
            await ctx.send('Already playing')
            logging.info(str(server) + " [" + str(ctx.message.author) + "] = " + 'Already playing')
    else:
        await ctx.send('User is not in a channel.')
        logging.info(str(server) + " [" + str(ctx.message.author) + "] = " + 'User is not in a channel')

@client.command(name='songs', help='lists songs from candlestick')
async def songs(ctx):
    server = ctx.message.guild
    print(str(server) + " [" + str(ctx.message.author) + "] = " + 'songs')
    logging.info(str(server) + " [" + str(ctx.message.author) + "] = " + 'songs')
    await ctx.send(' lose me pt. 1 [1] \n insanity defense freestyle [2] \n dead feelings freestyle [3] \n alter ego [4]')

@client.command(name='ping', help='returns the latency')
async def ping(ctx):

    late = await ctx.send(f'**** Latency: {round(client.latency * 1000)}ms')
    server = ctx.message.guild
    print(str(server) + " [" + str(ctx.message.author) + "] = " + str(f'**** Latency: {round(client.latency * 1000)}ms'))
    logging.info(str(server) + " [" + str(ctx.message.author) + "] = " + str(f'**** Latency: {round(client.latency * 1000)}ms'))


@client.command(name='sr', help='outputs a players sr from a battletag ex: -sr Ryujiro#11204')
async def sr(ctx, bt):

    #url and requesting
    tag = bt.replace('#', '-')
    url = 'https://playoverwatch.com/en-us/career/pc/' + tag + '/'
    content = urlopen(Request(url, headers={'User-Agent': 'Mozilla'}))
    soup = BeautifulSoup(content.read(),"lxml")

    #gets the image 
    try:
        sr1 = soup.find('img', class_='competitive-rank-role-icon')
        sr = str(sr1)
        sr2 = sr.replace('"/>', '')
        sr3 = sr2.replace('[<img class="competitive-rank-role-icon" src="', '')
        sr4 = sr3.replace('<img class="competitive-rank-role-icon" src="', '')
    except:

        sr4 = 'none'
        include_tank = 'UNRATED'

    try:

        te1 = soup.find_all('img', class_='competitive-rank-role-icon')[1]
        te = str(te1)
        te2 = te.replace('"/>', '')
        te3 = te2.replace('[<img class="competitive-rank-role-icon" src="', '')
        te4 = te3.replace('<img class="competitive-rank-role-icon" src="', '')
    except:

        te4 = 'none'
        include_dps = 'UNRATED'
    try:

        ko1 = soup.find_all('img', class_='competitive-rank-role-icon')[2]
        ko = str(ko1)
        ko2 = ko.replace('"/>', '')
        ko3 = ko2.replace('[<img class="competitive-rank-role-icon" src="', '')
        ko4 = ko3.replace('<img class="competitive-rank-role-icon" src="', '')
    except:
        ko4 = 'none'
        include_support = 'UNRATED'

    #find what roles are played and get sr
    include_support = ' SUPPORT: [UNRATED] '
    include_dps = ' DPS: [UNRATED] '
    include_tank = 'TANK: [UNRATED]'
    server = ctx.message.guild

    if sr4 == 'https://static.playoverwatch.com/img/pages/career/icon-tank-8a52daaf01.png':

        tank = soup.find_all('div', class_='competitive-rank-level')[0].text
        include_tank = 'TANK: [' + tank + '] '

    if te4 == 'https://static.playoverwatch.com/img/pages/career/icon-offense-6267addd52.png':
        
        dps = soup.find_all('div', class_='competitive-rank-level')[1].text
        include_dps = ' DPS: [' + dps + '] '

    if ko4 == 'https://static.playoverwatch.com/img/pages/career/icon-support-46311a4210.png':

        support = soup.find_all('div', class_='competitive-rank-level')[2].text
        include_support = 'SUPPORT: [' + support + '] '

    #output
    if include_tank == 'TANK: [UNRATED]' and include_dps == ' DPS: [UNRATED] ' and include_support == ' SUPPORT: [UNRATED] ':
        await ctx.send("Couldn't find skill rating, player either has a privite profile, unrated, or you didnt capitalize a letter.")
        print(str(server) + " [" + str(ctx.message.author) + "] = " + "Couldn't find skill rating, player either has a privite profile, unrated, or you didnt capitalize a letter.")
        logging.info(str(server) + " [" + str(ctx.message.author) + "] = " + "Couldn't find skill rating, player either has a privite profile, unrated, or you didnt capitalize a letter.")

    else:
        await ctx.send("`" + include_tank + include_dps + include_support + "`")
        print(str(server) + " [" + str(ctx.message.author) + "] = " + "`" + include_tank + include_dps + include_support + "`")
        logging.info(str(server) + " [" + str(ctx.message.author) + "] = " + "`" + include_tank + include_dps + include_support + "`")

@client.command(name='request', help='plays music from a url')
async def request(ctx, url):

    server = ctx.message.guild
    if not ctx.message.author.voice:
        await ctx.send('User is not in a channel.')
        print(str(server) + " [" + str(ctx.message.author) + "] = " + 'User is not in a channel.')
        logging.info(str(server) + " [" + str(ctx.message.author) + "] = " + 'User is not in a channel.')

        return

    else:
        try:
            urltest = url[0:30]

            if urltest == 'https://www.youtube.com/watch?':

                channel = ctx.message.author.voice.channel
        
                await channel.connect()

                server = ctx.message.guild
                voice_channel = server.voice_client

                async with ctx.typing():
                    player = await YTDLSource.from_url(url, loop=client.loop)
                    voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

                await ctx.send('**Now playing:** {}'.format(player.title))
                print(str(server) + " [" + str(ctx.message.author) + "] = " + '**Now playing:** {}'.format(player.title))
                logging.info(str(server) + " [" + str(ctx.message.author) + "] = " + '**Now playing:** {}'.format(player.title))

            else:

                await ctx.send("Can't play that link")
                print(str(server) + " [" + str(ctx.message.author) + "] = " + "Can't play that link")
                logging.info(str(server) + " [" + str(ctx.message.author) + "] = " + "Can't play that link")

        except:

             await ctx.send('Already playing')
             print(str(server) + " [" + str(ctx.message.author) + "] = " + "Already playing")
             logging.info(str(server) + " [" + str(ctx.message.author) + "] = " + 'Already playing')


@client.command(name='stop', help='stops all music')
async def stop(ctx):
    server = ctx.message.guild
    try:
       server = ctx.message.guild.voice_client
       await server.disconnect()
       print(str(server) + " [" + str(ctx.message.author) + "] = " + 'stop')
       logging.info(str(server) + " [" + str(ctx.message.author) + "] = " + 'stop')
    
    except:

        await ctx.send('Error')
        print(str(server) + " [" + str(ctx.message.author) + "] = " + 'stop: error')
        logging.info(str(server) + " [" + str(ctx.message.author) + "] = " + 'stop: error')

@tasks.loop(seconds=20)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))

client.run(token)