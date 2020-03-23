import json
alphabet = 'abcdefghijklmnopqrstuvwxyz'

letter_pairs = json.loads(open('letter-pairs.json').read())

similar_letters = {
	('a', 'o'),
	('o', 'u'),
	('i', 'e')
}

vowels = 'aeiou'

def split_word(word):
	word = word.lower()
	output = []
	tmp = ''
	for i in range(len(word)):
		in_letter_pairs = False
		for letter_pair in letter_pairs:
			pair_matches = True
			for l in range(len(letter_pair)):
				try:
					if word[i + l] != letter_pair[l]:
						pair_matches = False
				except IndexError:
					pass
			if pair_matches:
				in_letter_pairs = True
		if in_letter_pairs or word[i] not in alphabet:
			tmp += word[i]
		else:
			tmp += word[i]
			output.append(tmp)
			tmp = ''
	output.append(tmp)

	output_tmp = []
	for o in output:
		if o.strip() != '' and not o.isdigit():
			output_tmp.append(o.strip())
	return output_tmp


def ship_names(user1, user2):
	user1, user2 = user1.lower(), user2.lower()
	if user1 == user2:
		return user1
	if len(user2) < len(user1):
		_user1 = user1
		user1 = user2
		user2 = _user1

	user1_split = split_word(user1)
	user2_split = split_word(user2)

	if len(user2_split) < len(user1_split):
		_user1_split = user1_split
		user1_split = user2_split
		user2_split = _user1_split

	print(user1_split, user2_split)

	if len(user1_split) == 2 and len(user2_split) == 2:
		print('Perfect match found, combining...')
		shipped_1 = user1_split[0] + user2_split[1]
		shipped_2 = user2_split[0] + user1_split[1]
		check_1 = len(shipped_1) <= len(shipped_2)
		check_2 = len(user1_split[0]) >= len(user2_split[0])-1
		print(shipped_1, shipped_2)
		print(check_1, check_2)
		print(user1_split[0], user2_split[0])
		if check_1 and check_2:
			return shipped_1
		else:
			return shipped_2
	if len(user1_split) == 1 and len(user2_split) == 2:
		if len(user1_split[0]) > len(user2_split[0]):
			return user1_split[0] + user2_split[1]
		else:
			return user2_split[0] + user1_split[0]

	if len(user2) // 1.5 > len(user1):
		user1_half = len(user1) // 2
		found = False
		for v in vowels:
			found_pos = user2[1:-1].find(v)
			if found_pos != -1:
				user2_half = found_pos
				found = True
		if not found:
			user2_half = int((len(user2) / 2) - 0.6)
			user2_edited = user2_half + user1_half
			user2_half = user2_edited
		shipped = user1 + user2[user2_half:]
		return shipped

	lowest_diff = 999
	lowest_diff_loc = (-1, -1)
	for i, letter in enumerate(user1):
		for i2, letter2 in enumerate(user2):
			similar = False
			if letter == letter2:
				similar = True
			else:
				for s in similar_letters:
					if letter in s and letter2 in s:
						similar = True
						break
			if similar:
				diff = abs(i - i2)
				if diff < lowest_diff:
					lowest_diff = diff
					lowest_diff_loc = (i, i2)
	if lowest_diff != 999:
		try:
			print('huh', lowest_diff, lowest_diff_loc)
			idek = user2[lowest_diff_loc[0]] == user1[lowest_diff_loc[1]]
			print(idek)
			if idek:
				shipped = (
					user2[:lowest_diff_loc[0]] + user1[lowest_diff_loc[1]:]
				)
			else:
				shipped = (
					user2[:lowest_diff_loc[0] + 1] + user1[lowest_diff_loc[1]:]
				)

			return shipped
		except IndexError:
			pass # ok

	print(user1, user2)
	if len(user1) > 3:
		user1_half = len(user1) // 2
	else:
		user1_half = 0
	user2_half = int((len(user2) / 2) - 0.6)
	print('foo', user1_half, user2_half)
	shipped = user2[:user2_half] + user1[user1_half:]
	return shipped


def ship(user1, user2):
	user1_split = user1.split()
	user2_split = user2.split()
	if len(user1_split) == len(user2_split):
		output = []
		for u1, u2 in zip(user1_split, user2_split):
			output.append(ship_names(u1, u2))
		return ' '.join(output)
	else:
		return ship_names(user1, user2)
