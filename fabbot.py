#!/usr/bin/env python3

import discord
import asyncio
from miotoken import miotoken as miotoken
from discord import User
from discord.ext import commands


print('bella')

fabbot = commands.Bot(command_prefix='!')

@fabbot.event
async def on_ready():
    print("Client logged in")
    print(fabbot.user.name)
    print(fabbot.user.id)
    print('--------')

@fabbot.command(pass_context = True)
async def botsay(ctx, *args):
    mesg = ' '.join(args)
    await fabbot.delete_message(ctx.message)
    return await fabbot.say(mesg)

@fabbot.command()
async def hello(*args):
    print(User.display_name)
    return await fabbot.say("Hello, world!")

if __name__ == '__main__':
    fabbot.run(miotoken)

