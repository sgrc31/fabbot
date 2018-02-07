#!/usr/bin/env python3

import logging
import time
import os
import sys
import secrets
import peewee as pw
from discord.ext import commands

logging.basicConfig(level=logging.INFO)
start_time = time.time()
db = pw.SqliteDatabase('fabdb.db', pragmas=(('foreign_keys', True),))
fabbot = commands.Bot(command_prefix=commands.when_mentioned_or('!'))


def create_db_tables(tables=[]):
    with db:
        db.create_tables(tables)


class BaseModel(pw.Model):
    class Meta:
        database = db


class Tag(BaseModel):
    tag = pw.CharField(unique=True)


class Link(BaseModel):
    title = pw.CharField()
    url = pw.CharField()
    description = pw.CharField()


class LinkToTag(pw.Model):
    """A simple "through" table for many-to-many relationship."""
    link_id = pw.ForeignKeyField(Link)
    tag_id = pw.ForeignKeyField(Tag)

    class Meta:
        database = db
        primary_key = pw.CompositeKey('link_id', 'tag_id')


@fabbot.event
async def on_ready():
    print("Client logged in")
    print(fabbot.user.name)
    print(fabbot.user.id)
    print('--------')


@fabbot.command(pass_context=True, hidden=True)
async def botsay(ctx):
    mesg = ctx.message.content[8:]
    await fabbot.delete_message(ctx.message)
    return await fabbot.say(mesg)


@fabbot.command(pass_context=True, hidden=True)
async def botmock(ctx):
    mesg = ctx.message.content[9:]
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
                )
async def mcu(ctx):
    """Fornisce tutti i dati necessari alla connessione con il sistema BlueJeans
    per seguire lezioni, reviews e lectures"""
    return await fabbot.say('**NB: Limitarsi ad una connessione per lab durante lezioni e recitations**\n\n'
                            'url: {}\n\n'
                            'oppure ID: **{}** \| Pin: **{}** da utilizzare con il client bluejeans'
                            ', scaricabile da <https://www.bluejeans.com/downloads>\n\n'
                            '{}'
                            '*Regional reviews*: ID: **{}** \| pin: **{}** \| url: {}\n\n'
                            'indirizzo screensharing \(nessun limite di connessioni\):'
                            ' http://screen.academany.org/'
                            .format(secrets.bjurl, secrets.bjid, secrets.bjpin, 'ip da inserire nel sistema di videoconferenza: **{}**\n\n'
                                    if ctx.message.channel.id == '405377785176260609' else '', secrets.regionalid, secrets.regionalpin, secrets.regionalurl)
                            .format(secrets.bjip)
                            )


@fabbot.command('tagadd',
                pass_context=True,
                brief='crea una tag per archiviare i link',
                hidden=True
                )
async def tagadd(ctx, *args):
    """Aggiunge uno (o più) tag per l'archiviazione dei link."""
    if len(args) < 1:
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


@fabbot.command('linkadd',
                pass_context=False,
                brief='aggiungi un link alla raccolta'
                )
async def linkadd(url: str, title: str, description: str):
    """Aggiunge un link, provvisto di titolo e descrizione sommaria"""
    db.connect()
    try:
        x = Link(url=url, title=title, description=description)
        x.save()
    except:
        db.close()
        return await fabbot.say('qualcosa è andato storto, spiacente. Il link non è stato salvato')
    db.close()
    return await fabbot.say('link salvato')


@linkadd.error
async def linkadd_error(error, ctx):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        db.close()
        return await fabbot.send_message(ctx.message.channel, 'Argomenti mancanti. !help linkadd per l\'utilizzo corretto')
    else:
        return await fabbot.send_message(ctx.message.channel, 'Qualcosa è andato storto, ma non so esattamente cosa... Auguri a fare debug')

@fabbot.command('linklist',
                brief='mostra l\'elenco dei link salvati'
                )
async def linklist():
    return await fabbot.say('{}'.format('\n'.join(['**{}** <{}> *{}*'.format(x.title, x.url, x.description) for x in Link.select()])))


#presa pari pari da https://github.com/ZeroEpoch1969/RubyRoseBot/blob/master/bot.py
@fabbot.command('uptime',
                brief='visualizza uptime del bot'
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


@fabbot.command('desiderata',
                brief='invia richiesta per aggiungere funzionalità al bot',
                pass_context=True
                )
async def desiderata(ctx, *args):
    """Invia un suggerimento agli amministrazioni sulle funzionalità che
    vorresti vedere aggiunte al bot"""
    if len(args) == 0:
        return await fabbot.say('{} non credo di aver capito. Digita \'!help desiderata\' per maggiori informazioni'.format(ctx.message.author.mention))
    await fabbot.say('Grazie {}. La tua richiesta è stata inoltrata a chi di dovere.'.format(ctx.message.author.mention))
    destination = ctx.message.server.get_member('118482952672772103')
    return await fabbot.send_message(destination, '{} > da **{}**: {}'.format(ctx.message.timestamp, ctx.message.author, ctx.message.content))


@fabbot.command('about',
                brief='about this bot'
                )
async def about():
    """Mostra info relative a questo bot"""
    return await fabbot.say('```fabbot, a simple bot for managing fab academy discord channel.\n'
                            'made by Simone Guercio - s.guercio@gmail.com\n'
                            'code available at TODO inserire repo\n'
                            'released under the GNU Affero General Public License v3```'
                            )


if __name__ == '__main__':
    if not os.path.exists('fabdb.db'):
        logging.info('Nessun database trovato, ne creo uno e esco')
        create_db_tables([Tag, Link, LinkToTag])
        sys.exit()
    logging.info('Database trovato')
    fabbot.run(secrets.miotoken)
