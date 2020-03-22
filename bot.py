import discord
from config import getConfig
from scores import getScores
from scores import setScores

client = discord.Client()
config = getConfig('config.json')
scores = getScores()

def formatScores(d):
    """Makes the scores look pretty so we can print them in the embed"""
    d = {k: v for k, v in sorted(scores.items(), key=lambda item: item[1], reverse=True)}
    string = ''
    for k, v in d.items():
        string += client.get_user(k).name + ': ' + str(v) + ' '  + config['scoreName']  + '\n'
    string.strip('\n')
    return string

@client.event
async def on_ready():
    print('Bot started')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    elif message.content.startswith(config['prefix']+config['upvoteCommand']):
        lastMessage = await message.channel.history(limit=2).flatten()
        lastMessage = lastMessage[1]
        if lastMessage.author == message.author:
            return
        
        if lastMessage.author.id in scores:
            scores[lastMessage.author.id] += 1
        else:
            scores[lastMessage.author.id] = 1

        await message.channel.send(message.author.mention + ' upvoted ' + lastMessage.author.mention + '!') 
        setScores(scores)

    elif message.content.startswith(config['prefix']+config['downvoteCommand']):
        lastMessage = await message.channel.history(limit=2).flatten()
        lastMessage = lastMessage[1]
        if lastMessage.author == message.author:
            return

        if lastMessage.author.id in scores:
            scores[lastMessage.author.id] -= 1
        else:
            scores[lastMessage.author.id] = -1

        await message.channel.send(message.author.mention + ' downvoted ' + lastMessage.author.mention + '!')
        setScores(scores)

    elif message.content.startswith(config['prefix']+config['scoresCommand']):
        scoreBoard = discord.Embed()
        scoreBoard.add_field(name='Top '+config['scoreName']+' for **'+message.channel.guild.name+'**', value='```🏆 '+formatScores(scores)+'```')
        await message.channel.send(embed=scoreBoard)
@client.event
async def on_reaction_add(reaction, user):
    #if reaction.message.author == user:
     #   return # if someone upvotes themselves, do nothing

    user = reaction.message.author
    if reaction.emoji == config['upvoteEmoji']:
        if user.id in scores:
            scores[user.id] += 1
        else:
            scores[user.id] = 1
    elif reaction.emoji == config['downvoteEmoji']:
        if user.id in scores:
            scores[user.id] -= 1
        else:
            scores[user.id] = -1
    setScores(scores)

client.run(config['token'])
