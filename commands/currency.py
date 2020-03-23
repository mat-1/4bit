import sys
import random
import logging

logger = logging.getLogger('currencycommands')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('4bit.log')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

def get_money_emoji(amount):
	emoji = ''
	if amount == 0:
		emoji = ':grimacing:'
	elif amount >= 10000:
		emoji = ':gem::gem::gem:'
	elif amount >= 7500:
		emoji = ':gem::gem:'
	elif amount >= 5000:
		emoji = ':gem:'
	elif amount >= 5000:
		emoji = ':gem:'
	elif amount >= 4000:
		emoji = ':moneybag::moneybag::moneybag:'
	elif amount >= 2500:
		emoji = ':moneybag::moneybag:'
	elif amount >= 1000:
		emoji = ':moneybag:'
	elif amount >= 500:
		emoji = ':money_with_wings:'
	elif amount >= 200:
		emoji = ':money_mouth:'
	elif amount >= 100:
		emoji = ':dollar:'
	elif amount >= 50:
		emoji = ':heavy_dollar_sign:'
	return emoji

async def cash(msgdata):
	message = msgdata['message']
	db = msgdata['db']
	cash = await db.get_cash(message.author.id)
	emoji = get_money_emoji(cash)

	if cash <= 20:
		emoji = 'You can money by playing games.'

	await message.channel.send(f'You have **${cash}**. {emoji}')


heads = """
        \_------\_
     /                 \\
    |   HEADS    |
     \\                 /
        '''------'''
"""
tails = """
        \_------\_
     /                 \\
    |     TAILS     |
     \\                 /
        '''------'''
"""


async def coinflip(msgdata):
	message = msgdata['message']
	db = msgdata['db']
	try:
		chosen = msgdata['args'][0].lower()
	except:
		chosen = None
	if chosen not in {'heads', 'tails'}:
		return await message.channel.send('You must choose either heads or tails, and then the amount of money you would like to gamble.')
	try:
		amount = abs(int(msgdata['args'][1]))
	except:
		return await message.channel.send('You must choose either heads or tails, and then the amount of money you would like to gamble.')


	cash = await db.get_cash(message.author.id)
	if amount > cash:
		return await message.channel.send('You don\'t have enough money to do this coinflip.')


	coinflipmsg = await message.channel.send(f'Flipping coin for **${cash}**...')

	# await db.edit_user(message.author.id, 'cash', 20)

	# chosen = 'heads'
	facing = random.choice(['heads', 'tails'])

	if facing == 'heads':
		ascii_art = heads
	else:
		ascii_art = tails

	if facing == chosen:
		display_message = f'You got {facing}! You won **${amount}**'
		await db.give_cash(message.author.id, amount)
		new_cash = cash + amount

	else:
		display_message = f'You got {facing}. You lost **${amount}**'
		await db.give_cash(message.author.id, -amount)
		new_cash = cash - amount

	emoji = get_money_emoji(cash)
	new_cash_display = f'\nYou now have **${new_cash}** {emoji}'

	await coinflipmsg.edit(content=display_message + ascii_art + new_cash_display)


async def daily(msgdata):
	message = msgdata['message']
	db = msgdata['db']
