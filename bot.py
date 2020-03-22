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
        string += client.get_user(int(k)).name + ': ' + str(v) + ' '  + config['scoreName']  + '\n'
    string.strip('\n')
    return string

@client.event
async def on_ready():
    print('Bot started')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    elif message.content.startswith(config['prefix']+config['scoresCommand']):
        scoreBoard = discord.Embed()
        scoreBoard.add_field(name='Top '+config['scoreName']+' for **'+message.channel.guild.name+'**', value='```🏆 '+formatScores(scores)+'```')
        await message.channel.send(embed=scoreBoard)
@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.author == user:
        return #if someone upvotes themselves, do nothing
    
    elif reaction.message.author == client.user:
        return #if someone upvotes the but, do nothing

    userid = str(reaction.message.author.id)
    if reaction.emoji == config['upvoteEmoji']:
        if userid in scores:
            scores[userid] += 1
        else:
            scores[userid] = 1
    elif reaction.emoji == config['downvoteEmoji']:
        if userid in scores:
            scores[userid] -= 1
        else:
            scores[userid] = -1
    setScores(scores)

client.run(config['token'])
