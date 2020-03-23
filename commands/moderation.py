import logging
import sys

logger = logging.getLogger('modcommands')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('4bit.log')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


def getMember(username, guild, client):
	try:
		userid = int(username)
		member = guild.get_member(userid)
		return member
	except ValueError:
		try:
			user = guild.get_member_named(username)
			assert user is not None
			return user
		except AssertionError:
			if username.startswith('<@') and username.endswith('>'):
				username = username[2:-1]
				if username[0] == '!':
					username = username[1:]
				userid = int(username)
				member = guild.get_member(userid)
				return member
			else:
				raise Exception(f'Invalid user {username}')


async def ban(msgdata):
	client = msgdata['client']
	message = msgdata['message']
	bot_owners = msgdata['bot_owners']
	args = msgdata['args']
	perms = message.channel.permissions_for(message.author)
	if perms.ban_members or message.author.id in bot_owners:
		member = getMember(args[0], message.guild, client)
		if args[1:] == []:
			reason = f'Banned by {message.author}'
		else:
			reason = ' '.join(args[1:])
		await member.ban(reason=reason)
		await message.channel.send(f'{member} ({member.id}) has been banned')
	else:
		await message.channel.send('You don\'t have permission to do that')


async def kick(msgdata):
	client = msgdata['client']
	message = msgdata['message']
	args = msgdata['args']
	bot_owners = msgdata['bot_owners']
	perms = message.channel.permissions_for(message.author)
	if perms.kick_members or message.author.id in bot_owners:
		member = getMember(args[0], message.guild, client)
		if args[1:] == []:
			reason = f'Kicked by {message.author}'
		else:
			reason = ' '.join(args[1:])
		await member.ban(reason=reason)
		await message.channel.send(f'{member} ({member.id}) has been banned')
	else:
		await message.channel.send('You don\'t have permission to do that')


async def autorole(msgdata):  # coming soon:tm:
	client = msgdata['client']
	args = msgdata['args']
	message = msgdata['message']
	prefix = msgdata['prefix']
	db = msgdata['db']
	content = msgdata['content']
	pass
