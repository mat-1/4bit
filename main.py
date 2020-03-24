import os
import sys
import time
import discord
import asyncio
import logging
import aiohttp
import website
import traceback
import importlib
import commands.fun
import commands.games
import commands.image
import commands.debug
import commands.shorten
import commands.utility
import commands.general
import commands.currency
import commands.moderation

from database import db
from types import ModuleType
from utilities import antiping
from static import dbltoken, defaultprefix, dev_mode, votelink, owners, \
	help_parsed, command_list, website_link

print('Initializing from', __name__)

if dev_mode:
	big_logo_colored = '\033[91m\033[91m\033[33m    d888\033[91m8\033[33m  888888\
b\033[91m.\033[33m   d8\033[91mb\033[33m 88\033[91m8\033[33m\n   d8P88\033[91m\
8\033[33m  88\033[91m8\033[33m  "88\033[91mb\033[33m  Y8\033[91mP\033[33m 88\
\033[91m8\033[33m\n  d8\033[91mP\033[33m 88\033[91m8\033[33m  88\033[91m8\033\
[33m  .88\033[91mP\033[33m      88\033[91m8\033[33m\n d8\033[91mP\033[33m  88\
\033[91m8\033[33m  8888888K\033[91m.\033[33m  88\033[91m8\033[33m 88888\
\033[91m8  \033[107m\033[30m\033[1m DEV MODE \033[m\033[33m\nd8\033[91m8\
\033[33m   88\033[91m8\033[33m  88\033[91m8\033[33m  "Y88\033[91mb\033[33m 88\
\033[91m8\033[33m 88\033[91m8\033[33m\n888888888\033[91m8\033[33m 88\033[91m8\
\033[33m    88\033[91m8\033[33m 88\033[91m8\033[33m 88\033[91m8\033[33m\
\n      88\033[91m8\033[33m  88\033[91m8\033[33m   d88\033[91mP\033[33m 88\
\033[91m8\033[33m Y88b\033[91m.\033[33m\n      88\033[91m8\033[33m  8888888P\
\033[91m"\033[33m  88\033[91m8\033[33m  "Y88\033[91m8\033[33m\033[m'
else:
	big_logo_colored = '\033[36m\033[36m\033[96m    d888\033[36m8\033[96m  888888\
b\033[36m.\033[96m   d8\033[36mb\033[96m 88\033[36m8\033[96m\n   d8P88\033[36m\
8\033[96m  88\033[36m8\033[96m  "88\033[36mb\033[96m  Y8\033[36mP\033[96m 88\
\033[36m8\033[96m\n  d8\033[36mP\033[96m 88\033[36m8\033[96m  88\033[36m8\
\033[96m  .88\033[36mP\033[96m      88\033[36m8\033[96m\n d8\033[36mP\
\033[96m  88\033[36m8\033[96m  8888888K\033[36m.\033[96m  88\033[36m8\033[96m \
88888\033[36m8\033[96m\nd8\033[36m8\033[96m   88\033[36m8\033[96m  88\033[36m8\
\033[96m  "Y88\033[36mb\033[96m 88\033[36m8\033[96m 88\033[36m8\033[96m\n88888\
8888\033[36m8\033[96m 88\033[36m8\033[96m    88\033[36m8\033[96m 88\033[36m8\
\033[96m 88\033[36m8\033[96m\n      88\033[36m8\033[96m  88\033[36m8\
\033[96m   d88\033[36mP\033[96m 88\033[36m8\033[96m Y88b\033[36m.\033[96m\
\n      88\033[36m8\033[96m  8888888P\033[36m"\033[96m  88\033[36m8\033[96m  "\
Y88\033[36m8\033[96m\033[m'

client = discord.AutoShardedClient()
# client = discord.Client()

werkzeuglogger = logging.getLogger('werkzeug')
werkzeuglogger.setLevel(logging.ERROR)

logger = logging.getLogger('4bit')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('4bit.log')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

logger.info('Loading...')

prefixcache = {}


def get_command_dict():
	return {
		'ping': commands.general.ping,
		'kill': commands.debug.kill,
		'say': commands.debug.say,
		'todo': commands.general.todo,
		'prefix': commands.general.prefix,
		'test': commands.general.test,
		'simonsays': commands.games.simonsays,
		'cookieclicker': commands.games.cookieclicker,
		'uno': commands.games.uno,
		# 'givecard': commands.games.givecard,
		'ask': commands.games.ask,
		'ban': commands.moderation.ban,
		'kick': commands.moderation.kick,
		'help': commands.general.helplist,
		'hangman': commands.games.hangman,
		'exec': commands.utility.execute,
		'eval': commands.utility.execute,
		'random': commands.utility.choose,
		'choice': commands.utility.choose,
		'choose': commands.utility.choose,
		'cash': commands.currency.cash,
		'bal': commands.currency.cash,
		'money': commands.currency.cash,
		'g': commands.currency.cash,
		'dollars': commands.currency.cash,
		'gold': commands.currency.cash,
		'wikipedia': commands.utility.wikipedia,
		'xkcd': commands.fun.xkcd,
		'timchen': commands.fun.timchen,
		'pingspoof': commands.general.pingspoof,
		'8ball': commands.fun.eightball,
		'vote': commands.general.vote,
		'pewdiepie': commands.fun.pewdiepie,
		'tseries': commands.fun.pewdiepie,
		'source': commands.general.source,
		'src': commands.general.source,
		'repl': commands.general.source,
		'hack': commands.fun.hackermode,
		'hacker': commands.fun.hackermode,
		'execute': commands.debug.evaluate,
		'evaluate': commands.debug.evaluate,
		'uptime': commands.general.uptime,
		'programmerhumor': commands.fun.programmerhumor,
		'tinyurl': commands.shorten.tinyurl,
		'four_h': commands.shorten.four_h,
		'4h': commands.shorten.four_h,
		'fourh': commands.shorten.four_h,
		'cuturl': commands.shorten.cuturl,
		'shorte': commands.shorten.shorte,
		'shortest': commands.shorten.shorte,
		'qr': commands.shorten.qr,
		'qrcode': commands.shorten.qr,
		'duck': commands.fun.random_duck,
		'ship': commands.fun.ship,
		'trigger': commands.image.triggered,
		'daily': commands.currency.daily,
		'impersonate': commands.image.impersonate,
		'error': commands.debug.raise_error,
		'website': commands.general.website,
		'memory': commands.debug.get_usage,
		'usage': commands.debug.get_usage,
		'giphy': commands.utility.giphy,
		'tenor': commands.utility.tenor,
		'youtube': commands.utility.youtube,
		'widget': commands.general.widget,
		'coinflip': commands.currency.coinflip,
		'token': commands.fun.token,
		# 'reddit': commands.fun.reddit,
	}


class cached:
	command_dict = get_command_dict()


async def updateservers():
	while True:
		async with aiohttp.ClientSession() as s:
			data = {
				'server_count': len(client.guilds)
			}
			r = await s.post(
				'https://discordbots.org/api/bots/386333909362933772/stats',
				json=data,
				headers={
					'Authorization': dbltoken
				})
			print(await r.text(), r.status)
		await asyncio.sleep(1800)


@client.event
async def on_ready():
	bot_start_time = time.time()

	for line in big_logo_colored.splitlines():
		print(line)
		await asyncio.sleep(0.2)
	server_count = len(client.guilds)
	website.jinja_env.globals['server_count'] = server_count

	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('-' * 6)
	game = discord.Game(name=f'Prefix: {defaultprefix}')
	await client.change_presence(activity=game)

	for i in commands.__dir__():
		m = getattr(commands, i)
		if isinstance(m, ModuleType):
			if hasattr(m, 'init'):
				print('Initializing', m.__name__)
				asyncio.ensure_future(m.init())
			if hasattr(m, 'background_task'):
				print('Running background task for', m.__name__)
				asyncio.ensure_future(m.background_task(client))

	if not dev_mode:
		asyncio.ensure_future(updateservers())

	asyncio.ensure_future(check_vote_queue())

	print('Took', bot_start_time - run_start_time, 'seconds for bot to start.')


async def check_vote_queue():
	while True:
		if len(db.voted_dm_queue) > 0:
			voted_id = int(db.voted_dm_queue.pop())
			voted_user = client.get_user(voted_id)
			await voted_user.send('Thank you for voting! You earned **$100**')
		await asyncio.sleep(1)


@client.event
async def on_guild_join(guild):
	server_count = len(client.guilds)
	website.jinja_env.globals['server_count'] = server_count


@client.event
async def on_member_join(member):
	serverdata = await db.get_server(member.guild.id)
	if 'autorole' in serverdata:
		therole = member.guild.get_role(serverdata['autorole'])
		member.add_roles([therole], reason='Auto role')
	else:
		pass

# loop.run_until_complete(db.init())


async def getprefix(guild):
	if guild is None:
		return defaultprefix
	if guild.id in prefixcache:
		return prefixcache[guild.id]
	else:
		serverdata = await db.get_server(guild.id)
		if 'prefix' in serverdata:
			return serverdata['prefix']
		else:
			return defaultprefix


async def has_voted(userid):
	return await db.has_voted(userid)


async def one_time_money(message, key, amount, content):
	print('one time money')
	userid = message.author.id
	if not await db.get_user_value(userid, key, False):
		print('yay')
		await db.set_userinfo(userid, {key: True})
		await db.give_cash(userid, amount)
		embed = discord.Embed(description=content)
		await message.channel.send(embed=embed)
	else:
		print('big sad')


@client.event
async def on_message(message):
	prefix = await getprefix(message.guild)
	if not message.content.startswith(prefix):
		if client.user in message.mentions:
			await message.channel.send(f'My prefix is `{prefix}`')
		return
	if message.author.bot:
		return
	raw_content = message.content[len(prefix):]
	content = antiping(raw_content).strip()
	args = content.split(' ')
	try:
		_, args1 = raw_content.split(' ', 1)
	except ValueError:
		args1 = ''
	cmd = args[0].lower().strip()
	args = args[1:]
	raw_content = args1
	content = antiping(args1).strip()
	prefix_escaped = prefix.encode('unicode_escape').decode()
	messagedata = {
		'client': client,
		'args': args,
		'message': message,
		'prefix': prefix,
		'db': db,
		'content': content,
		'has_voted': has_voted,
		'votelink': votelink,
		'bot_owners': owners,
		'get_cash': db.get_cash,
		'raw_content': raw_content,
		'helpparsed': help_parsed,
		'commandlist': command_list,
		'website': website_link,
		'prefix_escaped': prefix_escaped,
		'command': cmd,
		'guild': message.guild,
		'one_time_money': one_time_money
	}

	if cmd in cached.command_dict:
		cmd_func = cached.command_dict[cmd]
		try:
			await cmd_func(messagedata)
		except Exception as e:
			tb = '\n'.join(traceback.format_tb(e.__traceback__))
			print(prefix.encode())
			module_name = cmd_func.__module__ + '.' + cmd_func.__name__
			error_info = (
				'Something went wrong :(\n'
				'Here\'s some error info for you:\n'
				f'Occured while executing {prefix_escaped}**{cmd}** in *{module_name}*\n'
				'```py\n'
				f'{tb}\n'
				f'{type(e).__name__}: {e}'
				'```'
			)
			embed = discord.Embed(
				title='Error!',
				description=error_info
			)
			return await message.channel.send(embed=embed)
	elif cmd == 'reload':
		if message.author.id in owners:
			if len(args) > 0:
				try:
					file_name = getattr(commands, args[0])
				except AttributeError:
					return await message.channel.send('Invalid module')
				reloading_msg = f'Reloading `commands.{args[0]}`...'
				reloading_msg = await message.channel.send(reloading_msg)
				print('reloading', args[0])
				importlib.reload(
					file_name
				)
				cached.command_dict = get_command_dict()
				await reloading_msg.edit(
					content=f'Reloaded `commands.{args[0]}`.'
				)
			else:
				print(dir(commands))
				print(getattr(commands, dir(commands)[-1]))
				print(type(dir(commands)[-1]))
				command_types_raw = map(
					(lambda a: getattr(commands, a)),
					dir(commands)
				)
				command_types = [c for c in command_types_raw if hasattr(c, '__file__')]
				reloading_msg = await message.channel.send(
					f'Reloading `{len(command_types)}` modules'
				)
				start_time = time.time()
				for i, c in enumerate(command_types):
					importlib.reload(c)
				end_time = time.time()
				await reloading_msg.edit(
					content=(
						f'Reloaded `{len(command_types)}` modules '
						f'in `{int((end_time - start_time) * 1000)}`ms'
					)
				)
				cached.command_dict = get_command_dict()
				# print(list(command_types))
				# for i in map((lambda a: getattr(commands, a))dir(commands)) if isinstance(i, )
				# await message.channel.send('Please enter a command file to reload.')
		else:
			await message.channel.send('You must be a bot owner to use this command')
	else:
		pass  # Invalid command


async def bg_tasks(*args):
	print('started yeet')

print('starting')
website.start_server(
	client.loop
)

run_start_time = time.time()

client.run(os.getenv('token'))

print('closed')
