import logging
import sys
import aiohttp
import async_timeout
import discord
import os
import re
import traceback
import urllib.parse

logger = logging.getLogger('linkcommands')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('4bit.log')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

bitly_token = os.getenv('BITLY_TOKEN')


async def gen_shorten_embed(url: str, shortened: str) -> discord.Embed:
	dif = (int(len(url)) - int(len(shortened)))
	word = 'shorter'
	if dif < 0:
		word = 'longer'
		dif = abs(dif)
	description = f'Link shortened!\n\nOriginal URL: {url}\nShortened'\
		f'URL: {shortened}\n\nShortened URL is {dif} characters {word}.'
	return discord.Embed(
		title=shortened,
		colour=discord.Colour(0xd0021b),
		url=shortened,
		description=description
	)


async def error(msg, ctx):
	logger.error(msg)
	# TODO send to channel here

ip_middle_octet = r'(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5]))'
ip_last_octet = r'(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))'

regex = re.compile(
	'https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{2,256}\\.[a-z]{2,6}\\b\
([-a-zA-Z0-9@:%_\\+.~#?&//=]*)'
)
pattern = re.compile(regex)


def valid_url(value):
	return pattern.match(value) is not None


async def bitly(msgdata):
	'''Generates a Bit.ly Shortlink.	'''
	message = msgdata['message']
	args = msgdata['args']
	if not bitly_token:
		return message.channel.send('`BITLY_TOKEN` not found in .env file')
	ctx = message.channel
	if len(args) == 0:
		message.channel.send('Please specify a URL to shorten.	')
		return
	if not valid_url(args[0]):
		ctx.send('Please specify a valid URL.	')
		return
	url = args[0]

	async with ctx.typing():
		async with async_timeout.timeout(10):
			async with aiohttp.ClientSession() as session:
				async with session.get('https://api-ssl.bitly.com/v3/shorten?access_token=' 
					+ bitly_token + '&longurl=' + url) as res:
					if res.status != 200:
						text = await res.text()
						await error('Error in bitly request\
			Status code %s Text dump: \n%s' % (res.staus, text))
						return
					try:
						json = await res.json()
					except Exception:
						text = await res.text()
						await error('Error in jsonifying response: `%s`' % (text), ctx)
						return
					if json['status_txt'] != 'OK':
						await error('Bitly reported error status: %s' % json['status_txt'], ctx)
						return
					shortened = str(json['data']['url'])
					embed = await gen_shorten_embed(url, shortened)
					await ctx.send(embed=embed)
					return


async def tinyurl(msgdata):
	print('adfasdfasdfsafd')
	'''Generates a tinyurl.com shortlink. '''
	message = msgdata['message']
	args = msgdata['args']
	if len(args) == 0:
		await message.channel.send('Please specify a URL to shorten.	')
		return
	if not valid_url(args[0]):
		await message.channel.send('Please specify a valid URL.	')
		return
	url = args[0]

	async with message.channel.typing():
		with async_timeout.timeout(10):
			async with aiohttp.ClientSession() as s:
				async with s.get('https://tinyurl.com/api-create.php?url=' + url) as r:
					status = r.status
					text = await r.text()
					if status != 200:
						await error(
							'Please contact error: \nError in tinyurl request: '
							f'Status code {status} Text dump: \n```{text}```',
							message.channel
						)
						return
					embed = await gen_shorten_embed(url, text)
					await message.channel.send(embed=embed)

async def four_h(msgdata): # command is actually 4h
	'''Generates a 4h.net shortlink. '''
	message = msgdata['message']
	args = msgdata['args']
	ctx = message.channel
	if len(args) == 0:
		message.channel.send('Please specify a URL to shorten.	')
		return
	if not valid_url(args[0]):
		ctx.send('Please specify a valid URL.	')
		return
	url = args[0]
	try: 
		async with ctx.typing():
			async with async_timeout.timeout(10):
				async with aiohttp.ClientSession() as session:
					async with session.get('https://4h.net/api.php?url=' + url) as res:
						text = await res.text()
						embed = await gen_shorten_embed(text, url)
						await ctx.send(embed=embed)
	except:
		ctx.send('An error occurred while running that command.	')
		exc_type, exc_value, exc_traceback = sys.exc_info()
		lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
		logger.error(''.join('!! ' + line for line in lines))

async def cuturl(msgdata):
	'''Generates a CutUrls shortlink. '''
	message = msgdata['message']
	args = msgdata['args']
	ctx = message.channel
	if len(args) == 0:
		message.channel.send('Please specify a URL to shorten.	')
		return
	if not valid_url(args[0]):
		ctx.send('Please specify a valid URL.	')
		return
	url = args[0]

	async with ctx.typing():
		with async_timeout.timeout(10):
			async with aiohttp.ClientSession() as session:
				async with session.get(
						'https://cut-urls.com/api?api=' + os.environ.get('CUTURLS_TOKEN') + '&url=' + url) as res:
					try:
						r = await res.json()
					except Exception:
						await error('Error in jsonifying response: ```%s```\
						\nText Dump: ```%s```' % (traceback.format_exc(), res.text), ctx)
						return
					if res.status != 200:
						await error('Error: could not connect to CutUrls. Status code was ' + str(r.status_code),
									ctx)
						return
					elif r['status'] == 'success':
						shortened = r['shortenedUrl']
						embed = await gen_shorten_embed(url, shortened)
						await ctx.send(embed=embed)
						return

					elif r['status'] == 'error':
						await error(f'An error occurred. The message is: {r["message"]}')
						return
					else:
						await error('Error: unknown status. \n' + str(r))
						return

async def shorte(msgdata):
	'''
	Generates a shorte.st shortlink.
	Arguments:
	The URL to be shortened.
	'''
	message = msgdata['message']
	args = msgdata['args']
	ctx = message.channel
	if len(args) == 0:
		message.channel.send('Please specify a URL to shorten.	')
		return
	if not valid_url(args[0]):
		ctx.send('Please specify a valid URL.	')
		return
	url = args[0]
	with async_timeout.timeout(10):
		async with aiohttp.ClientSession() as s:
			headers = {'public-api-token': '92a73b54f0b7b18cc9799a96f8d7b0e0'}
			async with s.put('https://api.shorte.st/v1/data/url',
				data={'urlToShorten': url}, headers=headers) as res:
				status = res.status
				if status != 200:
					text = await res.text()
					await error('Please contact error: \nError in tinyurl request: \
Status code %s Text dump: \n```%s```' % (status, text), ctx)
					return
				try:
					r = await res.json()
				except Exception:
					await error('Error in jsonifying response: ```%s```\
					\nText Dump: ```%s```' % (traceback.format_exc(), res.text), ctx)
					return
				if r['status'] == 'ok':
					shortened = r['shortenedUrl']
					embed = await gen_shorten_embed(url, shortened)
					await ctx.send(embed=embed)
					return
				else:
					text = await res.text()
					await ctx.send('Error in shorte.st request: ```%s```' % text)


async def qr(msgdata):
	'''Generates a QR code using the data.	'''
	message = msgdata['message']
	args = msgdata['args']
	if len(args) == 0:
		message.channel.send('Please specify a data to encode.	')
		return
	data = args[0]

	async with message.channel.typing():
		embed = discord.Embed()
		image_url = 'https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=' + urllib.parse.quote_plus(data)
		embed.set_image(url=image_url)
		await message.channel.send(embed=embed)
		return
