import asyncio
import logging
import sys
import aiohttp
import discord
import random
import os
import concurrent
import ships
from utilities import antiping, get_id_from_mention
from base64 import b64encode
import time


logger = logging.getLogger('funcommands')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('4bit.log')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

tSeriesId = 'UCq-Fj5jknLsUf-MWSy4_brA'
pewdiepieId = 'UC-lHJZR3Gqxm24_Vd_AJ5Yw'

pewdiepiechannels = []

eightball_positive = [
	'It is certain.',
	'It is decidedly so.',
	'Without a doubt.',
	'Yes - definitely.',
	'You may rely on it.',
	'As I see it, yes.',
	'Most likely.',
	'Outlook good.',
	'Yes.',
	'Signs point to yes.',
]
eightball_unknown = [
	'Reply hazy, try again.',
	'Ask again later.',
	'Better not tell you now.',
	'Cannot predict now.',
	'Concentrate and ask again.',
]
eightball_negative = [
	'Don\'t count on it.',
	'My reply is no.',
	'My sources say no.',
	'Outlook not so good.',
	'Very doubtful.'
]
eightball_answers = eightball_positive + eightball_unknown + eightball_negative

pewdiepie_icon = 'https://yt3.ggpht.com/a-/'\
	'AN66SAztY6oYWZnS1Cae9o4_msEE1H83Tld5cFtl3Q=s900-mo-c-c0xffffffff-rj-k-no'
tseries_icon = 'https://upload.wikimedia.org/wikipedia/en/thumb/7/7d/'\
	'T-series-logo.svg/653px-T-series-logo.svg.png'


async def init():
	print('ok1')
	async with aiohttp.ClientSession() as s:
		print('ok2')
		r = await s.get('https://xkcd.com/info.0.json')
		print('ok3')
		data = await r.json()
		global newestxkcd
		print('ok4')
		newestxkcd = data['num']
	print('ok5')


async def getxkcd(num):
	global newestxkcd
	try:
		num = int(num)
	except ValueError:
		num = random.randint(1, newestxkcd)
	async with aiohttp.ClientSession() as s:
		if num == 0:
			r = await s.get(f'https://xkcd.com/info.0.json')
		else:
			r = await s.get(f'https://xkcd.com/{num}/info.0.json')
		if r.status == 404:
			return 404
		data = await r.json()
		if num == 0:
			num = data['num']
			newestxkcd = num
	return data


async def xkcd(msgdata):
	global newestxkcd
	client = msgdata['client']
	message = msgdata['message']
	content = msgdata['content']

	if content == 'new':
		num = newestxkcd
	else:
		num = content

	data = await getxkcd(num)
	if data == 404:
		embed = discord.Embed(title='404', description='Not found')
		await message.channel.send(embed=embed)
		return
	num = data['num']
	embed = discord.Embed(
		title=f'({num}) {data["safe_title"]}',
		description=data['alt']
	)
	embed.set_image(
		url=data['img']
	)
	msg = await message.channel.send(embed=embed)
	await msg.add_reaction('⬅')
	await msg.add_reaction('➡')

	def xkcdreact(r, u):
		try:
			if r.emoji in '⬅➡':
				if u.id == message.author.id:
					if r.message.id == msg.id:
						return True
		except Exception as e:
			print('xkcdreact', e)
		return False

	while True:
		done, pending = await asyncio.wait([
			client.wait_for('reaction_add', check=xkcdreact),
			client.wait_for('reaction_remove', check=xkcdreact)
		], return_when=asyncio.FIRST_COMPLETED)
		r, u = done.pop().result()

		for future in pending:
			future.cancel()

		if r.emoji == '➡':
			num += 1
		else:
			num -= 1
		data = await getxkcd(num)
		if data == 404:
			embed = discord.Embed(title='404', description='Not found')
			await message.channel.send(embed=embed)
			return
		num = data['num']
		embed = discord.Embed(
			title=f'({num}) {data["safe_title"]}',
			description=data['alt']
		)
		embed.set_image(
			url=data['img']
		)
		await msg.edit(embed=embed)


async def timchen(msgdata):
	message = msgdata['message']
	one_time_money = msgdata['one_time_money']
	async with aiohttp.ClientSession() as s:
		r = await s.get('https://timchen.tk/api')
		data = await r.json()
	embed = discord.Embed(
		title='Timchen',
		description=data['desc'],
		color=random.randint(0, 16777215)
	)
	embed.set_image(url=data['url'])
	await message.channel.send(embed=embed)
	if random.randint(1, 10) == 1:
		await one_time_money(message, 'timchen', 50, 'The power of Tim Chen has earned you **$50**!')


async def eightball(msgdata):
	message = msgdata['message']
	content = msgdata['content']
	one_time_money = msgdata['one_time_money']
	if content == '':
		await message.channel.send('Please ask a question.')
		return
	text = content

	text = ''.join(e for e in text.lower() if e.isalnum())
	text = hash(text)
	answer = eightball_answers[text % len(eightball_answers)]
	embed = discord.Embed(
		title=content,
		description=answer,
		color=0
	)
	await message.channel.send(embed=embed)
	if answer in eightball_positive:
		await one_time_money(message, 'eightball', 40, 'You earned **$40**!')
ytkeys = os.getenv('ytkeys').split(',')


async def get_pewdiepie_embed(triedkeys=[]):
	for _ in range(100):
		ytkey = random.choice(ytkeys)
		if ytkey not in triedkeys:
			break
	async with aiohttp.ClientSession() as s:
		pewds = await s.get(
			f'https://www.googleapis.com/youtube/v3/channels',
			params={
				'part': 'statistics',
				'id': pewdiepieId,
				'fields': 'items/statistics/subscriberCount',
				'key': ytkey
			}
		)
		tseries = await s.get(
			f'https://www.googleapis.com/youtube/v3/channels',
			params={
				'part': 'statistics',
				'id': tSeriesId,
				'fields': 'items/statistics/subscriberCount',
				'key': ytkey
			}
		)
	pewds = await pewds.json()
	tseries = await tseries.json()
	try:
		pewds = int(pewds['items'][0]['statistics']['subscriberCount'])
		tseries = int(tseries['items'][0]['statistics']['subscriberCount'])
	except ValueError:
		triedkeys.append(ytkey)
		if len(triedkeys) > 10:
			raise Exception
		return await get_pewdiepie_embed(triedkeys)

	embed = discord.Embed(title='Pewdiepie vs T-Series', color=0xff0000)
	embed.add_field(name='Pewdiepie', value=format(pewds, ',d'))
	embed.add_field(name='T-Series', value=format(tseries, ',d'))
	embed.add_field(name='Difference', value=format(abs(pewds - tseries), ',d'))
	rand = random.randint(0, 1)
	if rand == 0:
		embed.set_footer(
			text='Subscribe to Pewdiepie now to save YouTube!',
			icon_url=pewdiepie_icon
		)
	else:
		embed.set_footer(
			text='Unsubscribe from T-Series to save YouTube!',
			icon_url=tseries_icon
		)

	return embed


async def pewdiepie(msgdata):
	message = msgdata['message']
	has_voted = msgdata['has_voted']
	has_voted = await has_voted(message.author)

	embed = await get_pewdiepie_embed()
	msg = await message.channel.send(embed=embed)
	pewdiepiechannels.append(message.channel.id)
	while True:
		if pewdiepiechannels.count(message.channel.id) == 1:
			break
		await asyncio.sleep(1)
	count = 0
	try:
		while count < 12000:
			if pewdiepiechannels.count(message.channel.id) > 1:
				break
			await asyncio.sleep(1.5 if has_voted else 5)
			embed = await get_pewdiepie_embed()
			await msg.edit(embed=embed)
			count += 1
	except concurrent.futures._base.TimeoutError:
		pass
	pewdiepiechannels.remove(message.channel.id)
	await msg.edit(content='(No longer live)', embed=embed)


async def hackermode(msgdata):
	message = msgdata['message']
	one_time_money = msgdata['one_time_money']
	await message.channel.send(
		'**💻 Hacker mode enabled for '
		f'<@{message.author.id}>**'
	)
	if random.randint(1, 2) == 1:
		await one_time_money(message, 'hackermode', 100, 'Your hacks got you **$100**!')


async def programmerhumor(msgdata):
	message = msgdata['message']
	async with aiohttp.ClientSession() as s:
		r = await s.get('https://www.reddit.com/r/programmerhumor/random.json')
		data = await r.json()
		data_string = await r.text()
	meme_data = data[0]['data']['children'][0]['data']
	meme_title = meme_data['title']
	meme_content = None
	meme_url = None
	meme_video_url = None
	if meme_data['secure_media'] is not None:
		try:
			meme_video_url = meme_data['secure_media']['reddit_video']['fallback_url']
		except KeyError:
			pass
	if meme_video_url is None and 'url' in meme_data:
		meme_url = meme_data['url']
		extension = meme_url.rsplit('.', 1)[1]
		img_file_exts = ['png', 'jpg', 'gif']
		if extension not in img_file_exts:
			meme_content = meme_url
			if meme_url.startswith('https://youtu.be/'):
				meme_video_url = meme_url
			meme_url = None
	elif 'selftext' in meme_data:
		meme_content = meme_data['selftext']
	else:
		print('???????')

	print(meme_url)
	if meme_url is not None:
		embed = discord.Embed(title=meme_title)
		embed.set_image(url=meme_url)
	elif meme_video_url is not None:
		embed = discord.Embed(
			title=meme_title,
			description=meme_video_url
		)
	else:
		print('!!!!!!!!!', data_string)
		print(meme_content)
		embed = discord.Embed(
			title=meme_title,
			description=meme_content
		)
	await message.channel.send(embed=embed)


async def random_duck(msgdata):
	message = msgdata['message']
	one_time_money = msgdata['one_time_money']

	async with aiohttp.ClientSession() as s:
		r = await s.get('https://random-d.uk/api/v1/random')
		data = await r.json()
	url = data['url']
	msg = data['message']
	embed = discord.Embed(color=0xFFFF66)
	embed.set_image(url=url)
	embed.set_footer(text=msg)
	await message.channel.send(embed=embed)

	if random.randint(1, 5) == 1:
		await one_time_money(message, 'duck', 75, 'The duck donates **$75**!')





async def ship(msgdata):
	message = msgdata['message']
	args = msgdata['args']
	prefix = msgdata['prefix']
	client = msgdata['client']
	one_time_money = msgdata['one_time_money']
	if len(args) > 2:
		return await message.channel.send(
			f'Too many arguments. Do {prefix}help ship for '
			'an example on how to use the ship command'
		)
	elif len(args) < 2:
		return await message.channel.send(
			f'Too little arguments. Do {prefix}help ship for '
			'an example on how to use the ship command'
		)
	user1 = args[0]
	user2 = args[1]
	try:
		userid1 = get_id_from_mention(user1)
		user1 = antiping(client.get_user(userid1).name)
	except:
		pass
	try:
		userid2 = get_id_from_mention(user2)
		user2 = antiping(client.get_user(userid2).name)
	except:
		pass
		

	# if userid1 is not None:
	# 	user1 = antiping(client.get_user(userid1).name)
	# userid2 = get_id_from_mention(user2)
	# if userid2 is not None:
	# 	user2 = antiping(client.get_user(userid).name)
	user1 = user1.lower()
	user2 = user2.lower()
	invalid_ships = {('mat', 'moopy')}
	for ship in invalid_ships:
		if (user1, user2) == ship:
			return await message.channel.send('Invalid ship')
		elif (user2, user1) == ship:
			return await message.channel.send('Invalid ship')

	shipped = ships.ship(user1, user2)
	shipped = shipped.capitalize()
	user1, user2 = user1.capitalize(), user2.capitalize()
	if shipped in (user1, user2):
		output = '**No ship found**'
		if user1 in message.author.name or user2 in message.author.name:
			if random.randint(1, 2) == 1:
				await one_time_money(
					message,
					'invalidship',
					80,
					'Invalid ship :(. You earned **$80** so you aren\'t as sad'
				)
	else:
		output = f'*{user1}* + *{user2}* = **{shipped}**'
	embed = discord.Embed(
		title='Ship',
		description=output
	)
	await message.channel.send(embed=embed)
	if random.randint(1, 3) == 1:
		await one_time_money(message, 'ship', 45, 'I ship it. You got **$45**!')


def generate_token(userid):
	userid = str(userid)

	userid_part = b64encode(userid.encode()).decode()

	t = int(time.time())
	timestamp_b64 = b64encode(t.to_bytes(4, byteorder='big'))
	timestamp_part = timestamp_b64.decode().rstrip('=').replace('/', '_')

	hmac_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'
	hmac_part = ''.join([random.choice(hmac_chars) for _ in range(27)])

	return f'{userid_part}.{timestamp_part}.{hmac_part}'


def generate_token(userid):
	userid = str(userid)

	userid_part = b64encode(userid.encode()).decode()

	t = int(time.time())
	timestamp_b64 = b64encode(t.to_bytes(4, byteorder='big'))
	timestamp_part = timestamp_b64.decode()
	timestamp_part = timestamp_part.rstrip('=').replace('/', '_').replace('+', '-')

	hmac_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'
	hmac_part = ''.join([random.choice(hmac_chars) for _ in range(27)])

	return f'{userid_part}.{timestamp_part}.{hmac_part}'


async def token(msgdata):
	message = msgdata['message']
	args = msgdata['args']
	client = msgdata['client']

	if len(args) != 1:
		await message.channel.send(
			'Please mention the user you would like to generate the token for.'
		)

	user_id = get_id_from_mention(args[0])
	token = generate_token(user_id)
	embed = discord.Embed(
		description=token
	)
	embed.set_footer(
		text='Disclaimer: The token is not real and is generated randomly'
	)
	user = client.get_user(user_id)
	embed.set_author(
		name=f"{user.display_name}'s token",
		icon_url=user.avatar_url
	)
	await message.channel.send(embed=embed)
