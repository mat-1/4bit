import io
import os
import sys
import psutil
import asyncio
import logging
import discord
from contextlib import redirect_stdout

logger = logging.getLogger('debugcommands')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('4bit.log')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

p = psutil.Process(os.getpid())


def get_memory_usage():
	mem = p.memory_info().rss
	return mem / 1024 / 1024


def get_cpu_usage(interval=None):
	cpu = p.cpu_percent()
	return cpu


def execute(_code, loc):  # Executes code asynchronously
	_code = _code.replace('\n', '\n ')
	globs = globals()
	globs.update(loc)
	exec(
		'async def __ex():\n ' + _code,
		globs
	)
	return globs['__ex']()


async def kill(msgdata):
	client = msgdata['client']
	message = msgdata['message']
	bot_owners = msgdata['bot_owners']
	# serverprocess = msgdata['serverprocess']

	if message.author.id not in bot_owners:
		return await message.channel.send(
			'You don\'t have permission to use this command'
		)
	await message.channel.send(
		'4bit has been temporarily disabled for maintenance.'
	)
	logger.info('4bit has been temporarily disabled for maintenance.')
	await client.close()
	# serverprocess.terminate()


async def say(msgdata):
	message = msgdata['message']
	content = msgdata['content']
	bot_owners = msgdata['bot_owners']

	if message.author.id not in bot_owners:
		return await message.channel.send(
			'You don\'t have permission to use this command'
		)
	await message.channel.send(content)


async def evaluate(msgdata):
	message = msgdata['message']
	content = msgdata['content']
	bot_owners = msgdata['bot_owners']
	prefix = msgdata['prefix']
	client = msgdata['client']

	if message.author.id not in bot_owners:
		return await message.channel.send(
			f'''You don\'t have permission to use this command.
			You probably meant `{prefix}exec`'''
		)

	f = io.StringIO()
	with redirect_stdout(f):
		await execute(content, locals())
	out = f.getvalue()
	if out == '':
		out = 'No output.'
	await message.channel.send(
		embed=discord.Embed(
			title='Unsafe Eval',
			description=out
		)
	)


async def raise_error(msgdata):
	raise Exception('raise_error called')


async def get_usage(msgdata):
	message = msgdata['message']
	embed = await get_usage_embed()
	await message.channel.send(embed=embed)


async def get_usage_embed():
	mem_usage = get_memory_usage()
	mem_percent = mem_usage / 10.24
	mem_string = f'{round(mem_usage)}mb/1024mb ({round(mem_percent)}%)'
	mem_percent_10 = int((mem_percent / 10) + 0.9)
	print(mem_percent_10)
	mem_progress_bar = ('█' * mem_percent_10)
	mem_progress_bar += (' ' * (10 - mem_percent_10))

	cpu_percent = get_cpu_usage()

	if mem_percent < 10:
		embed_color = 0x04f919
	elif mem_percent < 20:
		embed_color = 0x73f904
	elif mem_percent < 50:
		embed_color = 0xeeff02
	elif mem_percent < 70:
		embed_color = 0xffb702
	elif mem_percent < 80:
		embed_color = 0xff5202
	elif mem_percent < 90:
		embed_color = 0xff2100
	else:
		embed_color = 0xff0000
	embed = discord.Embed(
		title='Monitor process resources',
		description=(
			f'{mem_string}\n'
			f'`[ {mem_progress_bar} ]`\n\n'
			f'{cpu_percent}% cpu usage'
		),
		color=embed_color
	)
	return embed


async def background_task(client):
	while True:
		await asyncio.sleep(30)
		get_cpu_usage()
