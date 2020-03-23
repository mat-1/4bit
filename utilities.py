def antiping(msg):
	return msg.replace('@', '@​')  # 0 width space to prevent @everyone from working


def get_userid(msg):
	return get_id_from_mention(msg)

	# msg = msg.replace('@​', '@')  # reverts the 0 width space
	# assert msg[0] == '<'
	# assert msg[-1] == '>'
	# assert msg[1] == '@'
	# msg = msg[2:-1]
	# if msg[0] == '!':
	# 	msg = msg[1:]
	# try:
	# 	return int(msg)
	# except ValueError:
	# 	raise AssertionError('Invalid user id')


def get_id_from_mention(message):
	message = message.replace('@​', '@')  # remove 0 width space

	if message.startswith('<@') and message[-1] == '>':
		message = message[2:-1]
		if message[0] == '!':
			message = message[1:]
		try:
			user_id = int(message)
			return user_id
		except ValueError:
			raise ValueError('Invalid user id')
	raise ValueError('Invalid mention')
