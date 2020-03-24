import discord
import re
from config import get_config
from scores import get_scores
from scores import set_scores

global scores
client = discord.Client()
config = get_config("config.json")
scores = get_scores()

yt_pattern = r"https?:\/\/(www\.)?(youtube\.com|youtu\.be)\/watch\?v=.+"


def format_scores(d):
    """Makes the scores look pretty so we can print them in the embed"""
    d = {
        k: v for k, v in sorted(scores.items(), key=lambda item: item[1], reverse=True)
    }
    string = ""
    topUser = True
    for k, v in d.items():
        try:
            name = client.get_user(int(k)).name
            if topUser:
                userlen = len(name) + len(str(v)) + 4
                topUser = False
            else:
                userlen = len(name) + len(str(v)) + 2
            string += (
                name
                + ": "
                + "-" * (28 - userlen)
                + " "
                + str(v)
                + " "
                + config["score_name"]
                + "\n\n"
            )
        except AttributeError:
            continue
    string.strip()
    return string


def add_score(author_id, score):
    if author_id in scores:
        scores[author_id] += score
    else:
        scores[author_id] = score


@client.event
async def on_ready():
    print("started")


@client.event
async def on_message(message):
    if message.author == client.user:
        return  # if it's the bot's message, do nothing
    if message.attachments != []:  # if the message has an attachment
        await message.add_reaction(config["upvote_emoji"])
        await message.add_reaction(config["downvote_emoji"])
    elif re.match(yt_pattern, message.content):
        await message.add_reaction(config["upvote_emoji"])
        await message.add_reaction(config["downvote_emoji"])
    elif message.author.id == 302050872383242240:  # disboard bot id
        if "wait" not in message.embeds[0].description:
            last_messages = await message.channel.history(limit=2).flatten()
            author_id = str(last_messages[1].author.id)
            add_score(author_id, config["bump_score"])
            await message.channel.send(
                last_messages[1].author.mention
                + " thanks for the bump. Have "
                + config["bump_score"]
                + " "
                + config["score_name"]
                + "!"
            )
            set_scores(scores)
    elif message.content.startswith(config["prefix"] + config["scores_command"]):
        score_board = discord.Embed()
        score_board.add_field(
            name="Top "
            + config["score_name"]
            + " for **"
            + message.channel.guild.name
            + "**",
            value="```" + config["top_emoji"] + " " + format_scores(scores) + "```",
        )
        await message.channel.send(embed=score_board)


@client.event
async def on_reaction_add(reaction, user):
    if reaction.message.author == user:
        return  # if someone upvotes themselves, do nothing
    if reaction.message.author == client.user:
        return  # if someone upvotes the bot, do nothing
    if user == client.user:
        return  # if the bot made the reaction, do nothing
    # otherwise, we know it is a genuine reaction

    author_id = str(reaction.message.author.id)
    if reaction.emoji == config["upvote_emoji"]:
        add_score(author_id, 1)
    elif reaction.emoji == config["downvote_emoji"]:
        add_score(author_id, -1)

    set_scores(scores)


client.run(config["token"])
