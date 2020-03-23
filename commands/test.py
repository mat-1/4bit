import logging
import sys


logger = logging.getLogger('examplecommands')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('4bit.log')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


async def test(msgdata):
	message = msgdata['message']
	await message.channel.send('test')
