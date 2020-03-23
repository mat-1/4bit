import logging
import sys
from PIL import Image, ImageDraw, ImageFont
import random
import io
import aiohttp
import discord
import utilities
from datetime import datetime, timezone, timedelta
import concurrent
import time
import os

logger = logging.getLogger('examplecommands')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('4bit.log')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

ratelimited = {}

ratelimit = 1 if os.getenv('dev') else 60
ratelimitmsg = 'You are being ratelimited for image commands. \
You can use this command again in {}s'


async def init():
	global whitney_normal
	global whitney_book
	global whitney_small
	global whitney_book_hd
	global whitney_small_hd
	whitney_book_url = 'https://discordapp.com/assets/e8acd7d9bf6207f99350ca9f9e23b168.woff'
	whitney_normal_url = 'https://discordapp.com/assets/3bdef1251a424500c1b3a78dea9b7e57.woff'
	async with aiohttp.ClientSession() as s:
		r = await s.get(whitney_book_url)
		whitney_book_data = await r.read()
		r = await s.get(whitney_normal_url)
		whitney_normal_data = await r.read()

		whitney_book_raw = io.BytesIO(whitney_book_data)
		whitney_book_raw_2 = io.BytesIO(whitney_book_data)
		whitney_book_raw_3 = io.BytesIO(whitney_book_data)
		whitney_book_raw_4 = io.BytesIO(whitney_book_data)

		whitney_normal_raw = io.BytesIO(whitney_normal_data)
		whitney_normal_raw = io.BytesIO(whitney_normal_data)

		whitney_normal = ImageFont.truetype(whitney_normal_raw, 16)
		whitney_book = ImageFont.truetype(whitney_book_raw, 16)

		whitney_small = ImageFont.truetype(whitney_book_raw_2, 12)

		whitney_book_hd = ImageFont.truetype(whitney_book_raw_3, 32)
		whitney_small_hd = ImageFont.truetype(whitney_book_raw_4, 24)
	print('gotten fonts')


def triggerify(original):
	im = Image.open(original)
	triggered_im = Image.open('assets/triggered.png').convert('RGBA')

	def image_overlay(src, color, alpha):
		overlay = Image.new(src.mode, src.size, color)
		return Image.blend(src, overlay, alpha)

	im = image_overlay(im, "#ff0000", 0.3)
	x, y = im.size
	trig_x, trig_y = im.size
	triggered_im.thumbnail((x,y), Image.ANTIALIAS)
	# triggered_im.save('triggered_edited.png')
	imgs = []
	for _ in range(10):
		imgs.append(im.copy())
	shake_amount = 3
	img_shake_amount = 10
	for i in range(len(imgs)):

		text_move_y = random.randint(-shake_amount, shake_amount)
		text_move_x = random.randint((y - y // 5.12) - shake_amount, (y - y // 5.12) + shake_amount)

		img_move_y = random.randint(-img_shake_amount, img_shake_amount)
		img_move_x = random.randint(-img_shake_amount, img_shake_amount)

		im = imgs[i]
		zoom_x = 1 - (img_shake_amount / x)
		zoom_y = 1 - (img_shake_amount / y)
		im = im.transform(im.size, Image.AFFINE, (zoom_x, 0, img_move_x + img_shake_amount//2, 0, zoom_y, img_move_y + img_shake_amount))

		im.paste(triggered_im, (text_move_y, text_move_x), triggered_im)
		imgs[i] = im
	# im = Image.alpha_composite(im, triggered_im)
	with io.BytesIO() as output:
		imgs[0].save(
			output,
			format='GIF',
			save_all=True,
			append_images=imgs[1:],
			duration=0,
			loop=0
		)
		output.seek(0)
		value = output.getvalue()
	del im
	del triggered_im
	return value


def impersonate_user(pfp, username, message, hd=False):
	inc_size = 2 if hd else 1

	pfp = Image.open(pfp).convert('RGBA')
	pfp_size = 40 * inc_size
	pfp.thumbnail((pfp_size, pfp_size), Image.ANTIALIAS)
	bg_color = (54, 57, 63)
	font = whitney_book_hd if hd else whitney_book
	msg_font_size = font.getsize(message)
	msg_width, msg_height = msg_font_size
	if msg_width < 200:
		msg_width = 200

	im_width = (100 + msg_width) * inc_size
	im_height = (80) * inc_size
	im = Image.new('RGBA', (im_width, im_height), bg_color)

	bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
	mask = Image.new('L', bigsize, 0)
	draw = ImageDraw.Draw(mask) 
	draw.ellipse((0, 0) + bigsize, fill=255)
	mask = mask.resize(pfp.size, Image.ANTIALIAS)
	# pfp.putalpha(mask)
	pfp_tmp = pfp
	pfp = Image.new('RGBA', pfp.size)
	# pfp = Image.new('RGBA',pfp.size,bg_color)
	pfp.paste(pfp_tmp, mask=mask)
	pfp_tmp = Image.new('RGBA',pfp.size)
	pfp_tmp.paste(pfp,mask=pfp)
	pfp = pfp_tmp

	draw = ImageDraw.Draw(im)

	draw.text((70, 40), message, (220, 221, 222), font=whitney_book)
	draw.text((70, 18), username, (255, 255, 255), font=whitney_normal)
	now = datetime.now(tz=timezone(-timedelta(hours=5)))
	hour = ((now.hour - 1) % 12) + 1
	minute = str(now.minute)
	if len(minute) == 1:
		minute = '0' + minute
	ampm = 'PM' if now.hour >= 12 else 'AM'
	time_formatted = f'{hour}:{minute} {ampm}'
	font_size = whitney_small.getsize(username)

	draw.text(
		(75 + font_size[0] * 1.33, 21),
		f'Today at {time_formatted}',
		(94, 96, 101),
		font=whitney_small
	)
	print(pfp.size)

	im.paste(pfp, (12, 20), pfp)
	# im.paste(pfp, (12, 20))

	with io.BytesIO() as output:
		im.save(
			output,
			format='PNG'
		)
		output.seek(0)
		value = output.getvalue()
	del im
	del draw
	del mask
	del pfp
	return value


async def triggered(msgdata):
	message = msgdata['message']
	args = msgdata['args']
	client = msgdata['client']
	one_time_money = msgdata['one_time_money']
	has_voted = await msgdata['has_voted'](message.author.id)

	if message.author.id in ratelimited:
		rlimit_t = time.time() - ratelimited[message.author.id]
		if rlimit_t < ratelimit:
			return await message.channel.send(
				ratelimitmsg.format(int(ratelimit - rlimit_t))
			)
	ratelimited[message.author.id] = time.time()

	if len(args) == 0:
		userid = message.author.id
	else:
		try:
			print(args[0])
			userid = utilities.get_userid(args[0])
		except AssertionError:
			return await message.channel.send('Invalid user')
	async with message.channel.typing():
		async with aiohttp.ClientSession() as s:
			img_size = 128
			user = client.get_user(userid)
			with io.BytesIO() as output:
				await user.avatar_url_as(static_format='png', size=img_size).save(output)
				output.seek(0)
				img_bytes = output.getvalue()

			with concurrent.futures.ThreadPoolExecutor() as pool:
				img = await client.loop.run_in_executor(pool, triggerify, io.BytesIO(img_bytes))
	filename = f'triggered.gif'
	img_file = discord.File(fp=io.BytesIO(img), filename=filename)
	await message.channel.send(file=img_file)

	if message.author.id == userid:
		await one_time_money(message, 'triggered', 50, 'Don\'t be triggered. Here, have **$50**.')



async def impersonate(msgdata):
	message = msgdata['message']
	args = msgdata['args']
	client = msgdata['client']
	content = msgdata['content']

	if message.guild.id == 437048931827056642:
		return await message.channel.send(
			'This command has been disabled in this server due to me (mat#6207) being '
			'blackmailed by timchen and katya'
			'Proof: https://discordapp.com/'
			'channels/437048931827056642/437067256049172491/567887292211920930\n'
			'If you\'d like to use the impersonate command, you can just do it in '
			'another server or in a dm, or you can literally just inspect element.'
		)

	if message.author.id in ratelimited:
		rlimit_t = time.time() - ratelimited[message.author.id]
		if rlimit_t < ratelimit:
			return await message.channel.send(
				ratelimitmsg.format(int(ratelimit - rlimit_t))
			)
	ratelimited[message.author.id] = time.time()

	if len(args) == 0:
		userid = message.author.id
	else:
		try:
			userid = utilities.get_userid(args[0])
			print(content)
			content = content.split(' ', 1)[1]
			print(content)
		except AssertionError:
			userid = message.author.id
		except IndexError:
			return await message.channel.send(
				'Please enter some text to impersonate that user with'
			)
	if content.strip() == '':
		return await message.channel.send(
			'Please enter a user and some text to impersonate a user with'
		)
	user = client.get_user(userid)
	if user is None:
		return await message.channel.send('Invalid user')
	async with message.channel.typing():
		with io.BytesIO() as output:
			await user.avatar_url_as(static_format='png', size=128).save(output)
			output.seek(0)
			img_bytes = output.getvalue()
		with concurrent.futures.ThreadPoolExecutor() as pool: # user.name
			# prefix_len = len(msgdata['prefix'])
			# cmd_len = len(msgdata['command'])
			# message_content = message.clean_content[prefix_len + cmd_len:].strip()
			img = await client.loop.run_in_executor(
				pool,
				impersonate_user,
				io.BytesIO(img_bytes),
				user.name,
				content,
				False
			)
			
	filename = f'{user.name}_impersonate.png'
	img_file = discord.File(fp=io.BytesIO(img), filename=filename)
	await message.channel.send(file=img_file)

