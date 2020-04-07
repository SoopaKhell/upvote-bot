from discord import Embed
from discord.ext import commands
from config import get_config
from scores import get_scores
from scores import set_scores
from re import match
import asyncio
from jishaku.paginators import PaginatorEmbedInterface

config = get_config("config.json")
scores = get_scores()
users_to_notify = []  # Users to notify when they can bump again.
bot = commands.Bot(command_prefix=config["prefix"])

yt_pattern = r"https?:\/\/(www\.)?(youtube\.com|youtu\.be)\/watch\?v=.+"


def format_scores():
    """Makes the scores look pretty so we can print them in the embed"""
    global scores

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
    global scores

    if author_id in scores:
        scores[author_id] += score
    else:
        scores[author_id] = score


async def notify_users_task():
    global users_to_notify

    await asyncio.sleep(7200)  # two hours
    channel = bot.get_channel(config["bump_notify_channel"])

    # Ping all users and empty the list
    await channel.send(
        f"You can bump now!\n\n{', '.join([user.mention for user in users_to_notify])}"
    )
    users_to_notify = []


def task_done_callback(task: asyncio.Task):
    if task.exception() and not isinstance(task.exception(), asyncio.CancelledError):
        task.print_stack()


@bot.listen()
async def on_ready():
    print(
        "Started on {}#{} ({})".format(
            bot.user.name, bot.user.discriminator, bot.user.id
        )
    )


@bot.listen()
async def on_message(message):
    global scores

    if message.author == bot.user:
        return  # if it's the bot's message, do nothing
    if message.attachments != [] or match(yt_pattern, message.content):
        await message.add_reaction(config["upvote_emoji"])
        await message.add_reaction(config["downvote_emoji"])

    # TODO: make this not use a history call
    elif message.author.id == 302050872383242240:  # disboard bot id
        last_messages = await message.channel.history(limit=2).flatten()
        user = last_messages[1].author

        if "wait" not in message.embeds[0].description:
            author_id = str(user.id)
            add_score(author_id, config["bump_score"])
            await message.channel.send(
                user.mention
                + " thanks for the bump. Have "
                + str(config["bump_score"])
                + " "
                + config["score_name"]
                + "!"
            )
            await set_scores(scores)

            # create/recreate reminder task:
            task = asyncio.create_task(notify_users_task())
            task.add_done_callback(task_done_callback)
        else:  # disboard gave a wait message
            if user not in users_to_notify:
                users_to_notify.append(user)
                await message.channel.send(
                    f"{user.mention} I will notify you when you can bump the server."
                )
                return
            await message.channel.send(
                f"{user.mention} You're already on the list to be notified!"
            )


@bot.listen()
async def on_reaction_add(reaction, user):
    global scores

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
    global scores

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
    score_board = Embed(
        description="Top "
        + config["score_name"]
        + " for **"
        + context.guild.name
        + "**"
    )

    paginator = commands.Paginator()
    for index, line in enumerate(format_scores()):
        if index == 0:
            line = f"{config['top_emoji']} {line}"
        paginator.add_line(line)

    interface = PaginatorEmbedInterface(paginator=paginator, embed=score_board)
    await interface.send_to(context)


bot.run(config["token"])
