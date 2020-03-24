import discord
import re
from config import getConfig
from scores import getScores
from scores import setScores

global scores
client = discord.Client()
config = getConfig('config.json')
scores = getScores()

def formatScores(d):
    """Makes the scores look pretty so we can print them in the embed"""
    d = {k: v for k, v in sorted(scores.items(), key=lambda item: item[1], reverse=True)}
    string = ''
    topUser = True
    for k, v in d.items():
        try:
            name = client.get_user(int(k)).name
            if topUser:
                userlen = len(name) + len(str(v)) + 4 
                topUser = False
            else:
                userlen = len(name) + len(str(v)) + 2
            string += name + ':' + ' ' + '-'*(28-userlen) + ' ' + str(v) + ' ' + config['scoreName']  + '\n\n'
        except AttributeError:
            continue
    string.strip()
    return string

def addScore(authorid, score):
    if authorid in scores:
        scores[authorid] += score 
    else:
        scores[authorid] = score

@client.event
async def on_ready():
    print('Bot started')

@client.event
async def on_message(message):
    if message.author == client.user:
        return #if it's the bot's message, do nothing
    if message.attachments != []: #if the message has an attachment
        await message.add_reaction(config["upvoteEmoji"])
        await message.add_reaction(config["downvoteEmoji"])
    elif re.match(r"https?:\/\/(www\.)?(youtube\.com|youtu\.be)\/watch\?v=.+", message.content):
        await message.add_reaction(config["upvoteEmoji"])
        await message.add_reaction(config["downvoteEmoji"])
    elif message.author.id == 302050872383242240: #disboard bot id
        if "wait" not in message.embeds[0].description:
            lastMessages = await message.channel.history(limit=2).flatten()
            authorid = str(lastMessages[1].author.id)
            addScore(authorid, config["bumpScore"])
            await message.channel.send(lastMessages[1].mention + " thanks for the bump. Have "+config["bumpScore"] + " karma!")
            setScores(scores)
    elif message.content.startswith(config['prefix']+config['scoresCommand']):
        scoreBoard = discord.Embed()
        scoreBoard.add_field(name='Top '+config['scoreName']+' for **'+message.channel.guild.name+'**', value='```'+config['topEmoji']+" "+formatScores(scores)+'```')
        await message.channel.send(embed=scoreBoard) 

@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.author == user:
        return #if someone upvotes themselves, do nothing
    if reaction.message.author == client.user:
        return #if someone upvotes the bot, do nothing
    if user == client.user:
        return #if the bot made the reaction, do nothing
    #otherwise, we know it is a genuine reaction

    authorid = str(reaction.message.author.id)
    if reaction.emoji == config['upvoteEmoji']:
        addScore(authorid, 1)
    elif reaction.emoji == config['downvoteEmoji']:
        addScore(authorid, -1)
    
    setScores(scores)

client.run(config['token'])
