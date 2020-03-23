import logging
import sys
import time
from utilities import antiping
import discord
import aiohttp
import os
import asyncio


logger = logging.getLogger('generalcommands')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('4bit.log')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

pingspoofedusers = []


async def test(msgdata):
	message = msgdata['message']
	await message.channel.send('test')


async def ping(msgdata):
	message = msgdata['message']
	start = time.time()
	pongmsg = await message.channel.send('Pong!')
	end = time.time()
	if message.author.id in pingspoofedusers:
		pingms = int((end - start) * 10000)
	else:
		pingms = int((end - start) * 1000)
	await pongmsg.edit(content=f'Pong! `{pingms} ms`')


async def todo(msgdata):
	message = msgdata['message']
	prefix = msgdata['prefix']
	db = msgdata['db']
	content = msgdata['content']
	args = msgdata['args']
	if len(args) == 0:
		try:
			userinfo = await db.get_user(message.author.id)
			assert userinfo['todos'] != []
		except AssertionError:
			await message.channel.send(
				':no_entry_sign: You have nothing in your TODO list.'
				f'Use `{prefix}todo add something` to add something to your todo list'
			)
		else:
			tosend = []
			i2 = 0
			for i in userinfo['todos']:
				i2 += 1
				tosend.append(f'{i2}) {antiping(i)}')
			embed = discord.Embed(
				title=f'{message.author}\'s todo list',
				description='\n'.join(tosend)
			)
			await message.channel.send(embed=embed)
	else:
		if args[0] == 'add':
			todomsg = content.split(' ', 1)[1]
			if len(todomsg) > 100:
				await message.channel.send(':no_entry_sign: That message is too long.')
				return
			userinfo = await db.get_user(message.author.id)
			try:
				todos = userinfo['todos']
			except Exception as e:
				print('ree iuewrhteiotubyey', type(e))
				todos = []
			todos.append(todomsg)
			if len(todos) > 20:
				await message.channel.send(
					':no_entry_sign: You have too many items in your TODO list'
				)
				return
			await db.edit_user(message.author.id, 'todos', todos)
			await message.channel.send(
				f':thumbsup: Added `{antiping(todomsg)}` to your TODO list'
			)
		elif args[0] == 'remove':
			userinfo = await db.get_user(message.author.id)
			try:
				removenum = int(args[1])
			except Exception as e:
				print('euiyhtlrty', type(e))
				await message.channel.send(
					'Please enter a valid number to remove from your TODO list'
				)
			try:
				todos = userinfo['todos']
				assert todos != []
			except Exception as e:
				print('euwrgytb', type(e))
				await message.channel.send(
					'You have nothing in your TODO list.'
					f'Use `{prefix}todo add something` to add something to your todo list'
				)
				return
			try:
				del todos[removenum - 1]
			except Exception as e:
				print('iasdfoasfgethy', type(e))
				await message.channel.send(
					':no_entry_sign: Error: '
					f'You only have {len(todos)} items in your TODO list'
				)
				return
			await db.edit_user(message.author.id, 'todos', todos)
			await message.channel.send(
				f'Removed #{removenum} from your todo list :thumbsup:'
			)
		else:
			await message.channel.send(f'Invalid argument `{args[0]}`.')


async def prefix(msgdata):
	message = msgdata['message']
	prefix = msgdata['prefix']
	db = msgdata['db']
	content = msgdata['content']
	args = msgdata['args']
	bot_owners = msgdata['bot_owners']
	perms = message.channel.permissions_for(message.author)
	if len(args) == 0:
		if perms.manage_guild or message.author.id in bot_owners:
			await message.channel.send(
				f'Server prefix is `{prefix}`.'
				f'You can do `{prefix}prefix NEW PREFIX` to change it.'
			)
		else:
			await message.channel.send(f'Server prefix is `{prefix}`.')
	else:
		if perms.manage_guild or message.author.id in bot_owners:
			newprefix = content.strip('​')
			await message.channel.send(f'Server prefix has been set to `{newprefix}`')
			await db.edit_server(message.guild.id, 'prefix', newprefix)
		else:
			await message.channel.send(
				'You don\'t have permission to use this command.'
			)


async def get_help_msg_embed(help_parsed, cmdname, prefix, commandlist):
	helpparsedtmp = {}
	for section in help_parsed:
		helpparsedtmp[section.lower()] = help_parsed[section]
	if cmdname in helpparsedtmp:
		commands = helpparsedtmp[cmdname]
		embed = discord.Embed()
		embed.title = cmdname.capitalize()
		cmds = []
		prefix = prefix.replace('\\', '\\\\')
		for cmd in commands:
			usagetmp = cmd['usage']
			if usagetmp != '':
				usagetmp = f' **{usagetmp}**'
			cmds.append(f'{prefix}**{cmd["name"]}**{usagetmp}: {cmd["desc"]}')
		embed.description = '\n'.join(cmds)
		return embed
	elif cmdname in commandlist:
		cmdinfo = commandlist[cmdname]
		embed = discord.Embed()
		embed.title = cmdinfo['name'] + ' ' + cmdinfo['usage']
		embed.description = cmdinfo['longdesc'].replace('{prefix}', prefix)
	else:
		embed = discord.Embed(title='Unknown command or category')
		return embed



async def helplist(msgdata):
	message = msgdata['message']
	prefix = msgdata['prefix']
	args = msgdata['args']
	help_parsed = msgdata['helpparsed']
	client = msgdata['client']
	commandlist = msgdata['commandlist']
	guild = msgdata['guild']
	if len(args) == 0:
		categories_msg = 'Please choose one of the categories \
to list the commands from:\n'
		number_emojis = (
			'1\u20e3', '2\u20e3', '3\u20e3',
			'4\u20e3', '5\u20e3', '6\u20e3',
			'7\u20e3', '8\u20e3', '9\u20e3'
		)
		add_emojis = []
		for i, h in enumerate(help_parsed):
			categories_msg += f'{i+1}) **{h}**\n'
			add_emojis.append(number_emojis[i])
		embed = discord.Embed(
			title='Help categories',
			description=categories_msg
		)
		m = await message.channel.send(
			embed=embed
		)
		for e in add_emojis:
			await m.add_reaction(e)
		try:
			def check(reaction, user):
				if user != message.author:
					return False
				return reaction.emoji in add_emojis
			reaction, user = await client.wait_for(
				'reaction_add', timeout=60.0, check=check
			)
			reaction_index = add_emojis.index(reaction.emoji)
			categories = list(help_parsed)
			category_name = categories[reaction_index].lower()
			print(category_name)
			embed = await get_help_msg_embed(help_parsed, category_name, prefix, commandlist)
			await m.edit(embed=embed)
		except asyncio.TimeoutError:
			pass
		for r in add_emojis:
			await m.remove_reaction(r, guild.me)
	else:
		cmdname = args[0].lower()
		embed = await get_help_msg_embed(help_parsed, cmdname, prefix, commandlist)
		await message.channel.send(embed=embed)


async def pingspoof(msgdata):
	message = msgdata['message']
	prefix_escaped = msgdata['prefix_escaped']
	one_time_money = msgdata['one_time_money']
	if message.author.id in pingspoofedusers:
		await message.channel.send('You are no longer being ping spoofed.')
		pingspoofedusers.remove(message.author.id)
	else:
		await message.channel.send(
			f'You are now being ping spoofed. Run {prefix_escaped}pingspoof again to disable this.'
		)
		pingspoofedusers.append(message.author.id)

	await one_time_money(message, 'pingspoof', 35, 'Your pingspoofing earned you **$35**!')



async def vote(msgdata):
	message = msgdata['message']
	prefix = msgdata['prefix']
	votelink = msgdata['votelink']
	await message.channel.send(
		f'You can vote for 4bit at {votelink} to gain access to `{prefix}exec`'
		'and earn 100 gold'
	)


async def source(msgdata):
	message = msgdata['message']
	await message.channel.send(
		'Here is my source code: https://repl.it/@mat1/4bit'
	)


async def uptime(msgdata):
	message = msgdata['message']
	uptime_api = os.getenv('uptimeapi')

	url = "https://api.uptimerobot.com/v2/getMonitors"

	headers = {
		'content-type': 'application/x-www-form-urlencoded',
		'cache-control': 'no-cache'
	}

	uptime_percent_1 = '???'
	uptime_percent_7 = '???'
	uptime_percent_30 = '???'

	for uptime_ratio in (1, 7, 30):
		payload = f'api_key={uptime_api}&'\
			'format=json&'\
			f'custom_uptime_ratios={uptime_ratio}'
		async with aiohttp.ClientSession() as s:
			r = await s.post(url, data=payload, headers=headers)
			data = await r.json()
		uptime_percent = data['monitors'][0]['custom_uptime_ratio']
		if uptime_ratio == 1:
			uptime_percent_1 = uptime_percent
		elif uptime_ratio == 7:
			uptime_percent_7 = uptime_percent
		elif uptime_ratio == 30:
			uptime_percent_30 = uptime_percent

	embed = discord.Embed(
		title='4bit Uptime',
		description=f'30 days: {uptime_percent_30}%\n'
								f'7 days: {uptime_percent_7}%\n'
								f'24 hours: {uptime_percent_1}%'
	)
	await message.channel.send(embed=embed)


async def website(msgdata):
	message = msgdata['message']
	site = msgdata['website']
	await message.channel.send(f'The 4bit website is at {site}')


async def widget(msgdata):
	# print('nou')
	message = msgdata['message']
	embed = discord.Embed(title='4bit discordbots.org widget')
	widget_url = 'https://discordbots.org/api/widget/386333909362933772.png'
	# print(widget)
	embed.set_image(
		url=widget_url
	)
	await message.channel.send(embed=embed)
