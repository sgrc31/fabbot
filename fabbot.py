#!/usr/bin/env python3

import logging
import discord
import datetime
import asyncio
import time
import os
import sys
import peewee as pw
from discord import User
from discord.ext import commands
from miotoken import miotoken as miotoken


logging.basicConfig(level=logging.INFO)
start_time = time.time()
db = pw.SqliteDatabase('fabsqlite.db', pragmas=(('foreign_keys', True),))
fabbot = commands.Bot(command_prefix=commands.when_mentioned_or('!'))

def create_db_tables(tables=[]):
    with db:
        db.create_tables(tables)

class BaseModel(pw.Model):
    class Meta:
        database = db

class Tag(BaseModel):
    tag = pw.CharField(unique=True)

#class LinkToTag(pw.Model):
#    """A simple "through" table for many-to-many relationship."""
#    blog = ForeignKeyField(Blog)
#    tag = ForeignKeyField(Tag)
#
#    class Meta:
#        primary_key = CompositeKey('blog', 'tag')

@fabbot.event
async def on_ready():
    print("Client logged in")
    print(fabbot.user.name)
    print(fabbot.user.id)
    print('--------')


@fabbot.command(pass_context=True, hidden=True)
async def botsay(ctx, *args):
    mesg = ' '.join(args)
    await fabbot.delete_message(ctx.message)
    return await fabbot.say(mesg)


@fabbot.command(pass_context=True, hidden=True)
async def botmock(ctx, *args):
    mesg = ' '.join(args)
    mockmsg = ''.join([y.lower() if x % 2 else y.upper() for (x, y) in enumerate(mesg)])
    await fabbot.delete_message(ctx.message)
    return await fabbot.say(mockmsg)


@fabbot.command('roulette', pass_context=True, hidden=True)
async def sfiga(ctx):
    if str(ctx.message.channel) == 'santachiarafablab':
        return await fabbot.say('bella li')
    else:
        return await fabbot.say('non è una stringa')


@fabbot.command('listato', pass_context=True, hidden=True)
async def listato(ctx):
    lista_membri = ctx.message.server.members
    for membro in lista_membri:
        print('{}, {}, {}'.format(membro.display_name, membro.name, membro.nick))
    return await fabbot.say('listato printato')


@fabbot.command('videoconferenza',
                pass_context=True,
                brief='dati di accesso al sistema di videoconferenza per lezioni, reviews e lectures',
                help='dati di accesso al sistema di videoconferenza per lezioni, reviews e lectures'
                )
async def mcu(ctx):
    """Fornisce tutti i dati necessari alla connessione con il sistema BlueJeans
    per seguire lezioni, reviews e lectures"""
    await fabbot.say('**NB: Limitarsi ad una connessione per lab durante lezioni e recitations**')
    await fabbot.say('url: https://bluejeans.com/academany/6294')
    await fabbot.say('oppure ID: **448190928** \| Pin: **6294** da utilizzare con il client bluejeans, scaricabile da https://www.bluejeans.com/downloads')
    if str(ctx.message.channel) == 'santachiarafablab':
        await fabbot.say('ip da inserire nel sistema di videoconferenza: **199.48.152.152**')
    await fabbot.say('indirizzo screensharing \(nessun limite di connessioni\): http://screen.academany.org/')


#@fabbot.before_invoke(open_db_connection)
#@fabbot.after_invoke(close_db_connection)
@fabbot.command('addtag',
                pass_context=True,
                brief='crea una tag per archiviare i link'
                )
async def addtag(ctx, *args):
    """Aggiunge uno (o più) tag per l'archiviazione dei link."""
    if len(args) < 1 :
        return await fabbot.say('Inserisci almeno una tag. Per maggiori informazioni digita !help addtag')
    db.connect()
    for x in args:
        try:
            x = Tag(tag=x)
            x.save()
        except:
            await fabbot.say('Impossibile salvare il tag {}: tag già presente'.format(x.tag))
    db.close()
    return await fabbot.say('operazione terminata')
    

# presa pari pari da https://github.com/ZeroEpoch1969/RubyRoseBot/blob/master/bot.py 
@fabbot.command('uptime',
                brief='visualizza uptime del bot',
                )
async def uptime():
    """Visualizza il tempo di uptime del bot"""
    second = time.time() - start_time
    minute, second = divmod(second, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)
    week, day = divmod(day, 7)
    return await fabbot.say('Uptime: {} settimane, {} giorni, {} ore, {} minuti, {} secondi'.format(int(round(week)),
                                                                                                    int(round(day)),
                                                                                                    int(round(hour)),
                                                                                                    int(round(minute)),
                                                                                                    int(round(second))
                                                                                                    ))

if __name__ == '__main__':
    if not os.path.exists('fabsqlite.db'):
        logging.info('Nessun database trovato, ne creo uno e esco')
        create_db_tables([Tag])
        sys.exit()
    logging.info('Database trovato')
    fabbot.run(miotoken)

