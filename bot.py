from discord import Embed
from discord.ext import commands
from config import get_config
from scores import get_scores
from scores import set_scores
from re import match
from re import findall
import asyncio

global scores

config = get_config("config.json")
scores = get_scores()
bot = commands.Bot(command_prefix=config["prefix"])

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
            name = bot.get_user(int(k)).name
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
    """Add score to to a user by id"""
    if author_id in scores:
        scores[author_id] += score
    else:
        scores[author_id] = score


@bot.listen()
async def on_ready():
    print(
        "Started on {}#{} ({})".format(
            bot.user.name, bot.user.discriminator, bot.user.id
        )
    )


@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return  # if it's the bot's message, do nothing
    if message.attachments != [] or match(yt_pattern, message.content):
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
                + str(config["bump_score"])
                + " "
                + config["score_name"]
                + "!"
            )
            await set_scores(scores)
        else:  # disboard gave a wait message
            last_messages = await message.channel.history(limit=2).flatten()
            time_to_wait = int(findall("\d+", message.embeds[0].description)[1])
            await message.channel.send(
                last_messages[1].author.mention
                + " I will notify you when you can bump the server."
            )
            await asyncio.sleep(60 * time_to_wait)
            await message.channel.send(
                last_messages[1].author.mention + " You can now bump the server!"
            )


@bot.listen()
async def on_reaction_add(reaction, user):
    if reaction.message.author == user:
        return  # if someone upvotes themselves, do nothing
    if reaction.message.author == bot.user:
        return  # if someone upvotes the bot, do nothing
    if user == bot.user:
        return  # if the bot made the reaction, do nothing
    # otherwise, we know it is a genuine reaction

    author_id = str(reaction.message.author.id)
    if reaction.emoji == config["upvote_emoji"]:
        add_score(author_id, 1)
    elif reaction.emoji == config["downvote_emoji"]:
        add_score(author_id, -1)

    await set_scores(scores)


@bot.listen()
async def on_reaction_remove(reaction, user):
    if reaction.message.author == user:
        return  # if someone removes a reaction from themselves, do nothing
    if reaction.message.author == bot.user:
        return  # if someone removes a reaction from the bot, do nothing
    if user == bot.user:
        return  # if the bot removed the reaction, do nothing
    # otherwise, we know it is a genuine reaction

    author_id = str(reaction.message.author.id)
    if reaction.emoji == config["upvote_emoji"]:
        add_score(author_id, -1)
    elif reaction.emoji == config["downvote_emoji"]:
        add_score(author_id, 1)

    await set_scores(scores)


@bot.command(name=config["scores_command"])
async def _scores(context):
    score_board = Embed()
    score_board.add_field(
        name="Top " + config["score_name"] + " for **" + context.guild.name + "**",
        value="```" + config["top_emoji"] + " " + format_scores(scores) + "```",
    )
    await context.send(embed=score_board)


bot.run(config["token"])
