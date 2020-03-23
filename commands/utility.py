import re
import logging
import sys
import static
import aiohttp
import json
import string
import random
import discord
import traceback
import websockets
from utilities import antiping
from base64 import b64encode, b64decode


logger = logging.getLogger('utilcommands')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('4bit.log')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

execsessions = {}

lang_repls = {
	'python3': 'e665a239-d3f1-48f5-b40a-6da112787602',
	'ruby': '1f6b2014-68cf-4d97-8a44-018f794e9142',
	'nodejs': 'd52aca21-5c5e-4cbd-8d84-ef4b91426dea',
	'bash': 'ab78c56d-c632-47fe-89e2-550f085ea838',
	'java': '0f8a116c-0bda-47f5-a5da-316c4edc18c3',
	'c': '2b99debe-640f-4ac4-90e0-88cfcfd28641',
	'lua': '2b99debe-640f-4ac4-90e0-88cfcfd28641',
	'go': '3445f53e-f690-4236-b899-fd5d19d0dcfe',

	'polygott': '4844baca-4830-4fe4-bf91-579cc9378f43'
	# polygott still wip
}

langs = {
	'py': 'python3',
	'python': 'python3',
	'python3': 'python3',
	'python2': 'python',

	'polygott': 'polygott',

	'ruby': 'ruby',
	'rb': 'ruby',

	'js': 'nodejs',
	'node': 'nodejs',
	'nodejs': 'nodejs',

	'shell': 'bash',
	'bash': 'bash',
	'console': 'bash',

	'java': 'java',

	'c': 'c',

	'lua': 'lua',

	'golang': 'go',
	'go': 'go'
}


eval_url = 'wss://eval.repl.it/ws'

env_b64 = 'aSdtIG5vdCBhIGduZWxmCmknbSBub3QgYSBnbm9ibGluCmknbSBhIGdub21lLCBhbm'\
	'QgeW91J3ZlIGJlZW4gR05PTUVEISEhIQ=='

env_meme = json.dumps(
	{
		'name': '.env',
		'content': env_b64,
		'encoding': 'base64'
	}
)

wikipedia_rest = 'https://en.wikipedia.org/api/rest_v1/page/summary/'
wikipedia_not_found_url = 'https://mediawiki.org/wiki/HyperSwitch/'\
	'errors/not_found'

number_emojis = [
	'1\u20e3',
	'2\u20e3',
	'3\u20e3',
	'4\u20e3',
	'5\u20e3',
	'6\u20e3',
	'7\u20e3',
	'8\u20e3',
	'9\u20e3',
	'\U0001f51f'
]

polygott_python = '''.PHONY:r
r:
	run-project python3 main.py'''


async def sandboxexec(code, language='python3', userid=None):
	try:
		actual_lang = language
		repl_id = lang_repls[language]
		gen_token_url = (
			f'https://repl.it/data/repls/{repl_id}/gen_repl_token'
		)
		async with aiohttp.ClientSession() as s:
			replittoken = await s.post(
				gen_token_url,
				headers={
					'referer': 'https://repl.it/@4bit'
				}
			)
			replittoken = await replittoken.json()

		async with websockets.connect(eval_url) as ws:
			await ws.send(json.dumps({'command': 'auth', 'data': replittoken}))
			await ws.recv()
			await ws.recv()
			if actual_lang == 'polygott':
				await ws.send(json.dumps({
					'command': 'write',
					'data': json.dumps({
						'name': 'main.py',
						'content': b64encode(code.encode()).decode(),
						'encoding': 'base64'
					})
				}))
				await ws.recv()
				await ws.recv()

				await ws.recv()

			await ws.send(json.dumps({'command': 'write', 'data': env_meme}))
			await ws.recv()
			await ws.recv()
			if actual_lang == 'polygott':
				await ws.send(json.dumps({'command': 'eval', 'data': polygott_python}))
			else:
				await ws.send(json.dumps({'command': 'eval', 'data': code}))
			while True:
				data = json.loads(await ws.recv())
				print(data)
				if data['command'] == 'output':
					yield data['data'].encode().decode('unicode_escape')
				elif data['command'] == 'result':
					try:
						yield data['error']
					except KeyError:
						if data['data'] != 'None':
							yield '> ' + data['data']
					return
				elif data['command'] == 'event:packageInstallOutput':
					yield data['data']
				elif data['command'] == 'event:packageInstallEnd':
					yield '\033[J'
	except Exception as e:
		print('foobar', e, type(e))
		traceback.print_tb(e.__traceback__)
		yield 'Something went wrong ._.\nThis should never ever ever *ever* happen'
		return


async def execute(msgdata):
	message = msgdata['message']
	content = msgdata['raw_content']
	has_voted = msgdata['has_voted']
	prefix = msgdata['prefix']

	if not await has_voted(message.author.id):
		votestring = 'You must vote for 4bit on [discordbots.org]'\
			'(https://discordbots.org/bot/386333909362933772/vote)'\
			' in order to gain access to this command'
		embed = discord.Embed(title='Vote', description=votestring)
		await message.channel.send(embed=embed)
		return
	try:
		if content.startswith('```') and content.endswith('```'):
			lang = content.splitlines()[0][3:].lower()
			code = content[len(lang) + 3:-3]
		else:
			lang, code = content.split(None, 1)
			lang = lang.lower()
	except Exception as e:
		print('reeeeee', type(e))
		template_error = 'Please enter a language and some code.\nExample: '\
			f'`{prefix}exec py print(\'hi\')`'
		await message.channel.send(template_error)
		return

	if lang in langs:
		lang = langs[lang]
		outputdata = ''
		waiting_msg = 'Waiting for output..'
		requested_msg = f'Requested by {message.author}'
		embed = discord.Embed(title=requested_msg, description=waiting_msg)
		outputmsg = await message.channel.send(embed=embed)
		lines = 0
		async for out in sandboxexec(code, language=lang, userid=message.author.id):
			in_escape = False
			escape_chars = ''
			for c in out:
				if c == '\033':
					in_escape = True
					escape_chars = ''
				else:
					if in_escape:
						if c in string.ascii_letters:
							if c == 'J':
								if escape_chars == '2':
									outputdata = ''
								else:
									outputdata = ''
								lines = 0
							in_escape = False
						else:
							escape_chars += c
					else:
						outputdata += c
						if c == '\n':
							lines += 1
			if len(outputdata) < 2000 and lines < 100:
				in_progress_msg = f'(In progress) Requested by {message.author}'
				embed = discord.Embed(title=in_progress_msg, description=outputdata)
				await outputmsg.edit(embed=embed)
			else:
				too_long_msg = 'Output too long'
				requested_by_msg = f'Requested by {message.author}'
				embed = discord.Embed(title=requested_by_msg, description=too_long_msg)
				await outputmsg.edit(embed=embed)
				return
		requested_by_msg = f'Requested by {message.author}'
		await outputmsg.edit(
			embed=discord.Embed(title=requested_by_msg, description=outputdata)
		)
	else:
		await message.channel.send(f'Unknown language "{antiping(lang)}"')
		return


async def choose(msgdata):
	message = msgdata['message']
	content = msgdata['content']
	if '|' in content:
		choices = content.split('|')
	elif ',' in content:
		choices = content.split(',')
	else:
		choices = content.split()
	if len(choices) < 2:
		two_choices = 'Please enter at least two choices to choose from'
		await message.channel.send(two_choices)
		return
	chosen = random.choice(choices).strip()
	i_chose_msg = f'I chose {chosen}!'
	await message.channel.send(embed=discord.Embed(description=i_chose_msg))


async def wikipedia(msgdata):
	client = msgdata['client']
	message = msgdata['message']
	content = msgdata['content']
	args = msgdata['args']
	checkedpages = []
	title = content
	if content == '':
		article_name = 'Please enter the name of a Wikipedia article to search for'
		return await message.channel.send(article_name)
	async with aiohttp.ClientSession() as s:
		while True:
			r = await s.get(wikipedia_rest + title)
			data = await r.json()
			if data['type'] == wikipedia_not_found_url:
				return await message.channel.send(embed=discord.Embed(title=data['title']))
			checkedpages.append(data['pageid'])
			if data['type'] == 'disambiguation':
				datatmp = data
				params = {
					'action': 'query',
					'list': 'search',
					'srlimit': 10,
					'srsearch': content,
					'format': 'json',
					'srprop': ''
				}
				r = await s.get(f'https://en.wikipedia.org/w/api.php', params=params)
				data = await r.json()
				title = None
				choices = []
				for page in data['query']['search']:
					if page['pageid'] not in checkedpages:
						checkedpages.append(page['pageid'])
						choices.append((page['title'], page))
						title = page['title']
				description = ['Please choose one of the following:']
				for i, c in enumerate(choices):
					description.append(f'{i+1}) {c[0]}')
				embed = discord.Embed(
					title=datatmp['title'],
					description='\n'.join(description)
				)
				msg = await message.channel.send(embed=embed)

				def wikipediareact(reaction, user):
					if user == message.author:
						if reaction.emoji in number_emojis:
							return True
						else:
							return False
					else:
						return False
				for i, c in enumerate(choices):
					await msg.add_reaction(number_emojis[i])
				reaction, user = await client.wait_for(
					'reaction_add',
					check=wikipediareact
				)
				chosennum = number_emojis.index(reaction.emoji)
				data = choices[chosennum][1]
				r = await s.get(wikipedia_rest + data['title'])
				data = await r.json()
				break
			else:
				break

		params = {
			'action': 'query',
			'pageids': data['pageid'],
			'prop': 'pageimages',
			'format': 'json',
			'pithumbsize': 100
		}
		r = await s.get(f'https://en.wikipedia.org/w/api.php', params=params)
		imgdata = await r.json()
		imgdata = list(
			imgdata['query']['pages'].values()
		)[0]
		print(imgdata)
		embed = discord.Embed(
			title=data['title'],
			description=data['extract']
		)
		if 'thumbnail' in imgdata:
			imgsrc = imgdata['thumbnail']['source']
			embed.set_thumbnail(
				url=imgsrc
			)
		else:
			imgsrc = None
		await message.channel.send(embed=embed)


async def tenor(msgdata):
	message = msgdata['message']
	content = msgdata['content']
	provider = 'tenor'
	async with aiohttp.ClientSession() as s:
		r = await s.get(
			'https://discordapp.com/api/v6/gifs/search',
			params={'q': content, 'media_format': 'gif', 'provider': provider}
		)
		data = await r.json()
	i = 0
	gif = data[i]
	embed = discord.Embed(
		title=gif['title'],
		url=gif['url']
	)
	embed.set_image(url=gif['src'])
	await message.channel.send(embed=embed)


async def giphy(msgdata):
	message = msgdata['message']
	content = msgdata['content']
	provider = 'giphy'
	async with aiohttp.ClientSession() as s:
		r = await s.get(
			'https://discordapp.com/api/v6/gifs/search',
			params={'q': content, 'media_format': 'gif', 'provider': provider}
		)
		data = await r.json()
	i = 0
	gif = data[i]
	embed = discord.Embed(
		title=gif['title'],
		url=gif['url']
	)
	embed.set_image(url=gif['src'])
	await message.channel.send(embed=embed)


async def youtube(msgdata):
	message = msgdata['message']
	content = msgdata['content']
	headers = static.yt_headers
	r = await static.yt_session.get(
		'https://www.youtube.com/results',
		params={'search_query': content, 'pbj': '1'},
		headers=headers
	)
	r = await r.json()
	# tmp is so pep8 doesnt get mad
	tmp = r[1]['response']['contents']['twoColumnSearchResultsRenderer']
	tmp = tmp['primaryContents']['sectionListRenderer']['contents'][0]
	videos = tmp['itemSectionRenderer']['contents']
	for v in videos:
		if 'videoRenderer' in v:
			video = v['videoRenderer']
			video_metadata = video['navigationEndpoint']['commandMetadata']
			video_url = video_metadata['webCommandMetadata']['url']
			return await message.channel.send(f'https://youtube.com{video_url}')
		elif 'channelRenderer' in v:
			channel = v['channelRenderer']
			channel_metadata = channel['navigationEndpoint']['commandMetadata']
			channel_url = channel_metadata['webCommandMetadata']['url']
			return await message.channel.send(f'https://youtube.com{channel_url}')
		elif 'playlistRenderer' in v:
			playlist = v['playlistRenderer']
			playlist_metadata = playlist['navigationEndpoint']['commandMetadata']
			playlist_url = playlist_metadata['webCommandMetadata']['url']
			return await message.channel.send(f'https://youtube.com{playlist_url}')
		elif 'searchPyvRenderer' in v: # ad
			continue
		elif 'backgroundPromoRenderer' in v: # also ad
			continue
		else:
			return await message.channel.send(
				'oof error unexpected key ' + tuple(v.keys())[0]
			)
	return await message.channel.send('Video not found :(')


async def background_task(client):
	# ytcfg.set\(({[{}"a-zA-Z_:\\/.0-9?=,\- %;\[\]]+)}\);
	static.yt_session = aiohttp.ClientSession(
		headers={
			'user-agent': static.yt_ua
		}
	)
	r = await static.yt_session.get(
		'https://www.youtube.com'
	)
	r = await r.text()
	ytcfg = static.ytcfg_re.findall(r)[0]
	static.ytcfg = json.loads(ytcfg)
	static.yt_headers = {
		'User-Agent': static.yt_ua,
		'X-YouTube-Client-Name': static.ytcfg['INNERTUBE_CONTEXT_CLIENT_NAME'],
		'X-YouTube-Client-Version': static.ytcfg['INNERTUBE_CONTEXT_CLIENT_VERSION'],
		'X-YouTube-Page-CL': static.ytcfg['PAGE_CL'],
		'X-YouTube-Page-Label': static.ytcfg['PAGE_BUILD_LABEL'],
		'X-YouTube-Variants-Checksum': static.ytcfg['VARIANTS_CHECKSUM']
	}
	for h in static.yt_headers:
		static.yt_headers[h] = str(static.yt_headers[h])
	print('gotten youtube client session')
