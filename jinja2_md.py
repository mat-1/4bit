# yeah i had to learn the jinja2 api just for this
# feel free to use but please give credit to me (@mat1)
# it is missing **a lot** of features by the way, but i'm too lazy to add them
from jinja2 import nodes
from jinja2.ext import Extension


class MarkdownExtension(Extension):
	tags = set(['markdown'])

	def __init__(self, environment):
		super(MarkdownExtension, self).__init__(environment)

	def parse(self, parser):
		lineno = next(parser.stream).lineno

		body = parser.parse_statements(['name:endmarkdown'], drop_needle=True)

		return nodes.CallBlock(
			self.call_method('_parse_markdown'),
			[], [], body
		).set_lineno(lineno)

	async def _parse_markdown(self, caller):
		url_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'\
			'abcdefghijklmnopqrstuvwxyz'\
			'0123456789'\
			'$-_.+!*\'(),~#'
		content = await caller()
		output = ''
		things = ['']
		https_progress = 0
		in_url = False
		url_tmp = ''
		hyperlink_progress = 0
		link_title = ''
		link_url = ''
		for i, char in enumerate(content):

			if hyperlink_progress > 0:
				if hyperlink_progress == 1:
					if char == ']':
						hyperlink_progress = 2
					else:
						link_title += char
				elif hyperlink_progress == 2:
					if char == '(':
						hyperlink_progress = 3
					else:
						output += '['+link_title+']'+char
						hyperlink_progress = 0
				elif hyperlink_progress == 3:
					if char == ')':
						hyperlink_progress = 0
						href = f'<a href="{link_url}">{link_title}</a>'
						output += href
						link_title = ''
						link_url = ''
					else:
						link_url += char
				continue

			if char == 'https://'[https_progress]:
				https_progress += 1
				if https_progress == 8:
					https_progress = 0
					in_url = True
				continue
			elif https_progress > 0:
				output += 'https://'[:https_progress]
				https_progress = 0

			if in_url:
				if char not in url_chars or i == len(content) - 1:
					char_included = True
					if i == len(content) - 1:
						url_tmp += char
						char_included = False
					cant_end_with = '>)]'
					if url_tmp[-1] in cant_end_with:
						print('rip in the chat bois')
						char = url_tmp[-1] + char
						url_tmp = url_tmp[:-1]
						print(char, url_tmp)
					href = f'<a href="https://{url_tmp}">https://{url_tmp}</a>'
					if char_included:
						output += href + char
					else:
						output += href
					in_url = False
					url_tmp = ''
				else:
					url_tmp += char
				continue

			elif char == '`':
				if things[-1] == '`':
					del things[-1]
					output += '</code>'
				else:
					things.append(char)
					output += '<code>'
			elif char == 'https://'[https_progress]:
				pass
			elif char == '[':
				if hyperlink_progress == 0:
					hyperlink_progress = 1
				else:
					print('error in md parsing lol')
			else:
				output += char

		return output
