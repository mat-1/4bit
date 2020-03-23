import asyncio
import logging
import sys
from utilities import antiping
import random
import discord
import concurrent.futures
import aiohttp
import os
import urllib.parse

logger = logging.getLogger('gamecommands')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('4bit.log')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

simonsays_emojis = ['🍏', '🔴', '💛', '🔵']
current_games = []

asksessions = {}
with open('words.txt') as f:
	words = f.read().splitlines()
with open('hangmans.txt') as f:
	hangmansraw = f.read()
hangmans = []
tmpHM = ''
for line in hangmansraw.splitlines():
	if line == '':
		hangmans.append(tmpHM)
		tmpHM = ''
	else:
		tmpHM += line + '\n'


unoemojis = {
	'Y2': 513177349672665130,
	'Y1': 512776994866462723,
	'Y3': 512776994870657046,
	'Y5': 512776995025977375,
	'YSKIP': 512776995038429205,
	'Y0': 512776995088891904,
	'Y4': 512776995172646922,
	'Y7': 512776995273441310,
	'YREVERSE':
	512776995281829900,
	'Y8': 512776995311058944,
	'Y6': 512776995315122186,
	'Y9': 512776995340419072,
	'YWILD': 512776995533488148,
	'YWILD_4': 512776995898261505,
	'R3': 513175645162045463,
	'R7': 513175673301630997,
	'G2': 512776563251478544,
	'R_2': 513177143274897418,
	'G_2': 513177164372377611,
	'Y_2': 513177187654828034,
	'B1': 512776562408423434,
	'B7': 512776562450497561,
	'BSKIP': 512776562828115989,
	'B3': 512776562857345056,
	'B0': 512776562886836228,
	'G0': 512776562978848780,
	'B8': 512776563025248257,
	'B5': 512776563029442571,
	'G6': 512776563058671617,
	'G4': 512776563108872193,
	'BWILD_4': 512776563130105878,
	'BWILD': 512776563167723554,
	'G9': 512776563218055169,
	'B_2': 512776563226574858,
	'R2': 513177237365719044,
	'B9': 512776563259998248,
	'R1': 512776563297746965,
	'GWILD_4': 512776563310198795,
	'GREVERSE': 512776563360792579,
	'G1': 512776563377569792,
	'G5': 512776563398410240,
	'G8': 512776563410993162,
	'R0': 512776563423576074,
	'R4': 512776563444416522,
	'R5': 512776563482165271,
	'R9': 512776563561857034,
	'R6': 512776563562119188,
	'GWILD': 512776563578896384,
	'R8': 512776563599605795,
	'WILD': 512776563746668558,
	'RWILD': 512776563763314693,
	'RREVERSE': 512776563780091916,
	'RWILD_4': 512776563901595658,
	'B4': 512776563930955776,
	'G7': 513175762774261786,
	'WILD_4': 513174119890681871,
	'RSKIP': 513175705643778051,
	'G3': 513175732998897675,
	'GSKIP': 513175794994905098,
	'B6': 513175811243900938,
	'BREVERSE': 513175845129551872,
	'B2': 513177253845401620,
	'DRAW': 513198318474756116,
	'drawcards': 550812643120906251
}


async def simonsays(msgdata):
	client = msgdata['client']
	message = msgdata['message']
	db = msgdata['db']
	if message.channel.id in current_games:
		await message.channel.send(f'A game is already in progress in this channel.')
		return
	current_games.append(message.channel.id)
	await message.channel.send(
		f'<@{message.author.id}> has started a game of '
		'Simon Says in this channel.'
	)
	await asyncio.sleep(1)
	pattern = []
	emojimsg = await message.channel.send(f'Watch closely')
	while True:
		pattern.append(random.choice(simonsays_emojis))
		for emoji in pattern:
			await asyncio.sleep(0.5)
			await emojimsg.edit(content=f'Watch closely [{emoji}]')
			await asyncio.sleep(1.5)
			await emojimsg.edit(content=f'Watch closely')
		for emoji in simonsays_emojis:
			await emojimsg.add_reaction(emoji)
		await emojimsg.edit(
			content='Now react to this message with the emojis you saw (in order)'
		)
		userpattern = []
		while True:
			try:
				timeout = 5 + len(pattern) * 3
				done, pending = await asyncio.wait([
					client.wait_for('reaction_add', timeout=timeout),
					client.wait_for('reaction_remove', timeout=timeout)
				], return_when=asyncio.FIRST_COMPLETED)
				reaction, user = done.pop().result()
			except concurrent.futures._base.TimeoutError:
				if message.channel.id in current_games:
					await emojimsg.edit(content='Timed out')
					current_games.remove(message.channel.id)
				return
			for future in pending:
				future.cancel()
			is_same_user = user.id == message.author.id
			is_same_emoji = reaction.message.id == emojimsg.id
			is_valid_emoji = reaction.emoji in simonsays_emojis
			if is_same_user and is_same_emoji and is_valid_emoji:
				userpattern.append(reaction.emoji)
				await emojimsg.edit(
					content='Now react to this message with the emojis you saw '
					f'[{"".join(userpattern)}]'
				)
				if len(userpattern) == len(pattern):
					break
			else:
				appinfo = await client.application_info()
				if appinfo.id == user.id:
					pass
				else:
					try:
						await emojimsg.remove_reaction(reaction, user)
					except Exception as e:
						print('GAMES.p 0u8egt', e)
		if userpattern == pattern:
			await emojimsg.edit(content='Correct. 👍')
			try:
				await emojimsg.clear_reactions()
			except discord.errors.Forbidden:
				# if it can't clear reactions then just delete the message
				await asyncio.sleep(1)
				await emojimsg.delete()
				emojimsg = await message.channel.send(f'Watch closely')
			await asyncio.sleep(1)
		else:
			final_pattern = ''.join(pattern)
			cash_amount = ((4 - len(pattern)) * 10) + random.randint(-10, 10)
			cash_win_msg = ''

			if cash_amount > 0:
				await db.give_cash(message.author.id, cash_amount)
				cash_win_msg = f'You won **${cash_amount}**'



			await emojimsg.edit(
				content=f'Incorrect, you lose. Final pattern: [{final_pattern}].\n{cash_win_msg}'
			)

			try:
				await emojimsg.clear_reactions()
			except discord.errors.Forbidden:
				pass
			current_games.remove(message.channel.id)
			return


async def ask(msgdata):
	appid = os.getenv('wolframalpha')
	message = msgdata['message']
	q = msgdata['content']
	timeout = aiohttp.ClientTimeout(total=10)
	async with message.channel.typing():
		print(q)
		async with aiohttp.ClientSession(timeout=timeout) as s:
			r = await s.get(
				'https://api.wolframalpha.com/v1/result',
				params={
					'appid': appid,
					'i': q
				}
			)
		result = await r.text()
	result = result.replace(
		'Wolfram|Alpha', '4bit'
	).replace(
		'Wolfram Alpha', '4bit'
	)
	result_embed = discord.Embed(
		title=q.capitalize(),
		description=result,
		color=random.randint(0x000000, 0xFFFFFF)
	)
	result_embed.set_footer(text='Powered by Wolfram Alpha')

	await message.channel.send(
		embed=result_embed
	)



async def uno(msgdata):
	message = msgdata['message']
	client = msgdata['client']
	db = msgdata['db']
	if message.channel.id in current_games:
		await message.channel.send(f'A game is already in progress in this channel.')
		return
	current_games.append(message.channel.id)
	unomsg = await message.channel.send(
		'React to this message with 🎮 to play '
		f'UNO with <@{message.author.id}>'
	)
	appinfo = await client.application_info()
	await unomsg.add_reaction('🎮')

	def checkuno(reaction, user):
		is_game_emoji = reaction.emoji == '🎮'
		is_same_user = user != message.author
		is_not_bot = appinfo.id != user.id
		is_same_message = reaction.message.id == unomsg.id
		return is_game_emoji and is_same_user and is_not_bot and is_same_message
	# author is already joined by default
	joinedusers = [message.author]
	timedouttimes = 0
	game_ready = False
	while not game_ready:
		try:
			reaction, user = await client.wait_for(
				'reaction_add', check=checkuno, timeout=15
			)  # uno timeout
			print('oof timed out')
			if user not in joinedusers:
				joinedusers.append(user)
		except concurrent.futures._base.TimeoutError:
			if len(joinedusers) > 1:
				game_ready = True
			else:
				print(timedouttimes)
				timedouttimes += 1
				if timedouttimes > 4:
					if message.channel.id in current_games:
						await message.channel.send('UNO timed out.')
						print(current_games)
						current_games.remove(message.channel.id)
						return
		else:
			joinedusers_count = len(joinedusers)
			await message.channel.send(
				f'<@{user.id}> has joined ({joinedusers_count}/5)'
			)

	colors = 'RGBY'
	specialcards = [
		'0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
		'0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
		'_2', 'REVERSE', 'SKIP'
	]
	# this gets added to in the next couple lines
	cards = [
		'WILD', 'WILD', 'WILD', 'WILD',
		'WILD_4', 'WILD_4', 'WILD_4', 'WILD_4',
		'drawcards'
	]
	for color in colors:
		for special in specialcards:
			cards.append(color + special)
	await message.channel.send(
		'Giving random cards to users (will be shown in dm)'
	)
	userscards = []

	for u in range(len(joinedusers)):
		cardstmp = []
		for _ in range(7):
			card = random.choice(cards)
			while card == "drawcards":
				card = random.choice(cards)
			cardstmp.append(random.choice(cards))
		userscards.append(cardstmp)
	turnnum = -1

	prevcard = None  # previously chosen card (doesn't include skip)
	chosencard = None  # previously chosen card (includes skip)
	unoreversed = False
	while True:  # main game loop
		if unoreversed:
			turnnum -= 1
		else:
			turnnum += 1

		whos_turn_id = turnnum % len(joinedusers)
		print('whosturnid', whos_turn_id)
		whos_turn = joinedusers[whos_turn_id]
		whos_turn_message_content = f'It is <@{whos_turn.id}>\'s turn'
		embed = discord.Embed(description=whos_turn_message_content)
		whos_turn_message = await message.channel.send(embed=embed)

		for (u, usercards) in zip(joinedusers, userscards):
			if u != whos_turn:
				print(f'dming {u}')
				await u.send(
					embed=discord.Embed(
						description=f'It is <@{whos_turn.id}>\'s turn'
					)
				)
			else:
				try:
					chosencard.name
				except Exception as e:
					print('games.py n ewrhyu etuhyeioryhuurehyb', e)
				else:
					if chosencard.name.endswith('_2'):
						await u.send(content=f'<@{prevuser.id}> used a +2 card on you.')
						randomcard1 = random.choice(cards)
						userscards[whos_turn_id].append(randomcard1)
						randomcard2 = random.choice(cards)
						userscards[whos_turn_id].append(randomcard2)
						randcard2_emoji = client.get_emoji(unoemojis[randomcard2])
						randcard1_emoji = client.get_emoji(unoemojis[randomcard1])
						await u.send(
							discord.Embed(
								description=f'You got {randcard1_emoji} and {randcard2_emoji}'
							)
						)
					elif chosencard.name.endswith('_4'):
						await u.send(
							discord.Embed(
								description=f'<@{prevuser.id}> used a +4 card on you.'
							)
						)
						randomcard1 = random.choice(cards)
						userscards[whos_turn_id].append(randomcard1)
						randomcard2 = random.choice(cards)
						userscards[whos_turn_id].append(randomcard2)
						randomcard3 = random.choice(cards)
						userscards[whos_turn_id].append(randomcard3)
						randomcard4 = random.choice(cards)
						userscards[whos_turn_id].append(randomcard4)

						randcard1_emoji = client.get_emoji(unoemojis[randomcard1])
						randcard2_emoji = client.get_emoji(unoemojis[randomcard2])
						randcard3_emoji = client.get_emoji(unoemojis[randomcard3])
						randcard4_emoji = client.get_emoji(unoemojis[randomcard4])
						await u.send(
							discord.Embed(
								description=f'You got {randcard1_emoji}, {randcard2_emoji}, '
								f'{randcard3_emoji} and {randcard4_emoji}'
							)
						)
		print('userscards!!', userscards)
		for (u, usercards) in zip(joinedusers, userscards):
			# tell users what their cards are
			if u == whos_turn:
				print(u, usercards)
				cardsemojis = []
				for e in usercards:
					e = unoemojis[e]
					e = client.get_emoji(e)
					cardsemojis.append(str(e))
				await u.send(f'Your cards: {"".join(cardsemojis)}')

		for (u, usercards) in zip(joinedusers, userscards):
			# turn number
			if u == whos_turn:  # user is choosing card
				cardmsg = await u.send('...')
				r = []
				print('userscards', userscards[whos_turn_id])
				for e in userscards[whos_turn_id]:
					if e not in r:  # check if card is valid
						if (prevcard is not None) and ('WILD' not in e):
							# not first turn and not wild card
							if len(e) == 2:  # check if normal card
								print('prevcard, e', prevcard, e)
								if prevcard.name[0] == e[0] or prevcard.name[1:] == e[1:]:
									# color or number or symbol matches
									pass
								else:
									continue
							else:
								if prevcard.name[0] == e[0] or prevcard.name[1:] == e[1:]:
									pass
								else:
									if len(prevcard.name) == 7:
										if prevcard.name[1:-2] == 'WILD' and prevcard.name[0] == e[0]:
											pass
										else:
											continue
									elif len(prevcard.name) == 5:
										if prevcard.name[1:] == 'WILD' and prevcard.name[0] == e[0]:
											pass
										else:
											continue
									else:
										continue
						e = unoemojis[e]
						print(e)
						print('adding', client.get_emoji(e).name)
						await cardmsg.add_reaction(client.get_emoji(e))
						r.append(e)
				await cardmsg.add_reaction(client.get_emoji(unoemojis['DRAW']))  # draw

				def validcard(reaction, user):
					usercardsids = []
					for card in userscards[whos_turn_id]:
						usercardsids.append(unoemojis[card])
					try:
						is_same_user = user.id == u.id
						is_same_message = reaction.message.id == cardmsg.id
						is_valid_emoji = reaction.emoji.id in usercardsids
						if is_same_user and is_same_message and is_valid_emoji:
							print('yay')
							return True
						else:
							is_draw = reaction.emoji.id == unoemojis['DRAW']
							is_same_user = user.id == u.id
							is_same_message = reaction.message.id == cardmsg.id
							if is_draw and is_same_user and is_same_message:
								print('detected draw')
								return True
							return False
					except Exception as e:
						print('gamespy ebtybhuerwetiyriueeeeeeee', type(e))
						return False

				if prevcard is None:
					await cardmsg.edit(content=f'It is your turn. Choose any card you want')
				else:
					await cardmsg.edit(content=f'It is your turn. Previous card: {prevcard}')
				print('waiting for reaction')
				try:
					reaction, user = await client.wait_for(
						'reaction_add', check=validcard, timeout=120
					)
				except concurrent.futures._base.TimeoutError:
					await message.channel.send('Uno timed out')
					current_games.remove(message.channel.id)
					return
				print('User reacted with', reaction.emoji.id, reaction.emoji.name)
				chosencard = reaction.emoji
				if reaction.emoji.name != 'DRAW':
					prevcard = reaction.emoji
					print(userscards[whos_turn_id])
					userscards[whos_turn_id].remove(prevcard.name)
					if reaction.emoji.name[1:] == 'REVERSE':
						embed = discord.Embed(description='You chose **REVERSE CARD**')
						await u.send(embed=embed)
						oldpattern = list(f'<@{usertmp.id}>' for usertmp in joinedusers)
						unoreversed = not unoreversed
						newpattern = reversed(oldpattern)
						embed = discord.Embed(
							description=f'Old pattern: {", ".join(oldpattern)}\n'
							f'New pattern: {", ".join(newpattern)}'
						)
						await u.send(embed=embed)
					elif reaction.emoji.name[1:] == 'SKIP':
						# the actual skipping
						await u.send(embed=discord.Embed(description='You chose **SKIP CARD**'))
						if unoreversed:
							for n in range(0, len(usercards[turnnum - 1])):
								if usercards[turnnum - 1[n]].emoji.name[1:] == '_2':

									print("User has a +2 card")

							for n in range(0, len(usercards[turnnum])):
								before_is_adding_2 = usercards[turnnum - 1[1:]] == '_2'
								now_is_adding_2 = usercards[turnnum[1:]] == '_2'
								if before_is_adding_2 and now_is_adding_2:
									no_skip = True
								if usercards[turnnum - 1[1:]] == '_4':
									no_skip = True
								if not no_skip:
									# if it's in reverse then go backwards
									turnnum -= 1

						else:
							# forward if its not in reverse
							turnnum += 1
					elif reaction.emoji.name[1:] == '_2':
						await u.send(embed=discord.Embed(description='You chose **+2 CARD**'))
					elif 'WILD' in reaction.emoji.name:
						if reaction.emoji.name.endswith('_4'):
							embed = discord.Embed(description='You chose **WILD +4 CARD**')
							await u.send(embed=embed)
						else:
							await u.send(embed=discord.Embed(description='You chose **WILD CARD**'))
						embed = discord.Embed(description='Choose a color')
						wildcolors = await u.send(embed=embed)
						if reaction.emoji.name.endswith('_4'):
							coloremojinames = ['RWILD_4', 'GWILD_4', 'BWILD_4', 'YWILD_4']
						else:
							coloremojinames = ['RWILD', 'GWILD', 'BWILD', 'YWILD']
						coloremojis = []
						for c in coloremojinames:
							emojitmp = client.get_emoji(unoemojis[c])
							coloremojis.append(emojitmp)
						for c in coloremojis:
							await wildcolors.add_reaction(c)

						def choosecolor(reaction, user) -> bool:
							user_id_matches = user.id == u.id
							emoji_is_valid = reaction.emoji in coloremojis
							is_correct_message = reaction.message.id == wildcolors.id
							return user_id_matches and emoji_is_valid and is_correct_message
						try:
							reaction, user = await client.wait_for(
								'reaction_add',
								check=choosecolor,
								timeout=120
							)
						except concurrent.futures._base.TimeoutError:
							await message.channel.send(
								embed=discord.Embed(description='Uno timed out')
							)
							current_games.remove(message.channel.id)
							return
						print(reaction.emoji.name)
						prevcard = reaction.emoji
						chosencard = reaction.emoji

					else:
						await u.send(f'You chose **{str(prevcard)}**')

				else:
					random_card_msg = 'Drawing a random card from the deck...'
					drawing1 = await u.send(embed=discord.Embed(description=random_card_msg))
					await asyncio.sleep(0.5)
					randomcard = random.choice(cards)
					userscards[whos_turn_id].append(randomcard)
					added_card_msg = (
						f'Added {client.get_emoji(unoemojis[randomcard])} '
						'to your cards'
					)
					await drawing1.edit(embed=discord.Embed(description=added_card_msg))
			prevuser = u

		embed = discord.Embed(
			description=f'{whos_turn_message_content}\nThey chose {chosencard}'
		)
		await whos_turn_message.edit(embed=embed)
		if len(userscards[whos_turn_id]) == 1:
			await message.channel.send(
				f'**:warning: <@{whos_turn.id}>: UNO :warning:**'
			)
			for u2 in joinedusers:
				await u2.send(f'**:warning: <@{whos_turn.id}>: UNO :warning:**')
		elif len(userscards[whos_turn_id]) == 0:
			await message.channel.send(f'**🎉 <@{whos_turn.id}> WINS 🎉**')
			for user in joinedusers:
				if user == whos_turn:
					give_cash = len(joinedusers) * 20
					await whos_turn.send(f'**🎉 YOU WIN 🎉**\nYou earned **${give_cash}**')
					await db.give_cash(whos_turn.id, give_cash)
				else:
					await user.send(f'**🎉 <@{whos_turn.id}> WINS 🎉**')
					

			current_games.remove(message.channel.id)
			return
			# whos turn it is = turnnum % len(joinedusers)
# UNO end #


async def hangman(msgdata):
	client = msgdata['client']
	prefix = msgdata['prefix']
	message = msgdata['message']
	db = msgdata['db']
	try:
		if msgdata[0] == 'exit':
			return
	except KeyError:
		pass
	except IndexError:
		pass
	word = random.choice(words)
	if message.channel.id in current_games:
		await message.channel.send(f'A game is already in progress in this channel.')
		return
	await message.channel.send(
		'A game of Hangman has been started in this channel'
	)
	await asyncio.sleep(0.5)
	defaultmsg = 'Generated random word, start guessing! (send letters in chat)'
	hmmsg = await message.channel.send(defaultmsg)
	guessed = [' ']
	incorrect = 0
	print(word)
	current_games.append(message.channel.id)

	def checkhangman(msg):
		if msg.channel == message.channel and msg.author == message.author:
			return True
		return False
	wascorrect = ''
	extra = ''
	while True:
		letters_display = ''
		currentcorrect = 0
		for l in word:
			if l in guessed:
				letters_display += l + ' '
				currentcorrect += 1
			else:
				letters_display += '\\_ '
		currenthangman = hangmans[incorrect]
		displayable = currenthangman + '\n' + extra +  '\n' + letters_display
		await hmmsg.edit(content=defaultmsg+'\n'+displayable)
		try:
			msg = await client.wait_for('message',check=checkhangman, timeout=60)
		except concurrent.futures._base.TimeoutError:
			await message.channel.send('Hangman timed out')
			current_games.remove(message.channel.id)
			return
		extra = ''
		letter = msg.content.lower().strip()
		if len(letter) == 1:
			print(guessed)
			if letter in guessed:
				extra = 'You already guessed this letter'
			else:
				if letter in word:
					wascorrect = 'Correct'
					print(len(word) - 1, currentcorrect)
					if len(word) - 1 == currentcorrect:
						multiply_cash = random.randint(100, 1000) / 100
						cash_amount = int(len(word) * multiply_cash)
						await db.give_cash(message.author.id, cash_amount)
						await message.channel.send(f'You win!\nYou earned **${cash_amount}** cash')
						currenthangman = hangmans[incorrect]
						displayable = currenthangman + '\n' + extra + letters_display
						await hmmsg.edit(content=defaultmsg + '\n' + displayable)
						current_games.remove(message.channel.id)
						return
				else:
					wascorrect = 'Incorrect'
					incorrect += 1
					if len(hangmans) - 1 == incorrect:
						await message.channel.send('You lose!')
						current_games.remove(message.channel.id)
						return
				guessed.append(letter)
		elif message.content.lower() == f'{prefix}hangman exit':
			await message.channel.send('Game has ended')
			current_games.remove(message.channel.id)
			return
		else:
			extra = f'You can only guess one letter at a time. \
Do `{prefix}hangman exit` if you wish to exit the game.'

async def cookieclicker(msgdata):
	message = msgdata['message']
	await message.channel.send('Cookie clicker coming Soon™')
async def connect4(msgdata): # coming soon:tm:
	message = msgdata['message']
	await message.channel.send(f'<@{message.author.id}> has started a game of Connect 4 in this channel.')
	emptyline = [0 for _ in range(7)]
	board = [emptyline for _ in range(6)]
	def renderboard():
		renderedboard = ''
		for line in board:
			for char in line:
				if char == 0:
					renderedboard += '🔴'
				elif char == 1:
					renderedboard += '🔵'
				elif char == 2:
					renderedboard += '⚫'
				else:
					renderedboard += '?'
			renderedboard += '\n'
		return renderedboard
	await message.channel.send(renderboard())

async def explodingkittens(msgdata):
	pass  # coming soon
