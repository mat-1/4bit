import os
import re
import random


def parse_help(md):
	currentcmd = ''
	cmdusage = ''
	cmdshortdesc = ''
	cmdlongdesc = ''
	sectionname = ''
	sectionname2 = ''
	cmds = {}
	cmdslist = {}
	for line in md.splitlines():
		line = line.strip()
		if line[0] == '#':
			if '#' in line[1:]:  # command
				if cmdlongdesc != '':
					currentcmdinfo = {
						'name': currentcmd,
						'usage': cmdusage,
						'desc': cmdshortdesc,
						'longdesc': cmdlongdesc.strip()
					}
					cmds[sectionname2].append(currentcmdinfo)
					cmdslist[currentcmd] = {
						'name': currentcmd,
						'usage': cmdusage,
						'desc': cmdshortdesc,
						'longdesc': cmdlongdesc.strip()
					}
					cmdlongdesc = ''
				sectionname2 = sectionname

				currentcmd = line[1:]
				currentcmd, cmdshortdesc = currentcmd.split('#', 1)
				currentcmd, cmdshortdesc = currentcmd.strip(), cmdshortdesc.strip()
				if currentcmd.count(' ') == 0:
					cmdusage = ''
				else:
					currentcmd, cmdusage = currentcmd.split(' ', 1)
					cmdusage = cmdusage.strip()
			else:
				sectionname = line[1:].strip()  # section
				cmds[sectionname] = []
		else:
			cmdlongdesc += (line.strip() + '\n')
	currentcmdinfo = {
		'name': currentcmd,
		'usage': cmdusage,
		'desc': cmdshortdesc,
		'longdesc': cmdlongdesc.strip()
	}
	cmds[sectionname2].append(currentcmdinfo)
	return cmds, cmdslist


print('running static.py')
randomid = random.randint(0, 1000)
dbltoken = os.getenv('dbltoken')

votelink = 'https://discordbots.org/bot/386333909362933772/vote'
apivotelink = 'https://discordbots.org/api/bots/386333909362933772/votes'

dev_mode = os.getenv('dev') == 'true'

if dev_mode:
	website_link = 'https://4bit-dev.mat1.repl.co'
else:
	website_link = 'https://4bitbot.tk'

owners = [
	224588823898619905,
	487258918465306634 # allawesome
]

help_parsed, command_list = parse_help(open('help.md').read())

defaultprefix = '\\'

invite_link = 'https://discordapp.com/oauth2/authorize'\
	'?client_id=386333909362933772&scope=bot&permissions=-1'

yt_session = None
ytcfg_re = re.compile('ytcfg.set\\(({.*?})\\);')
ytcfg = None
yt_headers = None
yt_ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101\
	Firefox/66.0'
