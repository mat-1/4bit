import os
import sys
import logging
import asyncio
import jinja2_md

from jinja2 import Environment, \
	FileSystemLoader, \
	select_autoescape
from static import defaultprefix, website_link, help_parsed, command_list, \
	invite_link
from database import db
from aiohttp import web

logger = logging.getLogger('website')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

fh = logging.FileHandler('4bit.log')
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


jinja_env = Environment(
	loader=FileSystemLoader(searchpath='./templates'),
	# loader=PackageLoader('main'),
	autoescape=select_autoescape(['html', 'xml']),
	enable_async=True,
	extensions=[jinja2_md.MarkdownExtension]
)

print('defined jinja_env')

routes = web.RouteTableDef()

jinja_env.globals['website_url'] = website_link
jinja_env.globals['server_count'] = 0
jinja_env.globals['help_parsed'] = help_parsed
jinja_env.globals['command_list'] = command_list
jinja_env.globals['prefix'] = defaultprefix

index_template = jinja_env.get_template('index.html')
bugs_template = jinja_env.get_template('bugs.html')


@routes.get('/')
async def web_index(request):
	r = await index_template.render_async()
	r = r.replace('{prefix}', defaultprefix)
	return web.Response(
		body=r,
		content_type='text/html'
	)


@routes.get('/bugs')
async def web_index(request):
	r = await bugs_template.render_async()
	return web.Response(
		body=r,
		content_type='text/html'
	)


@routes.get('/invite')
async def redirect_invite(request):
	return web.HTTPFound(invite_link)


@routes.get('/commands')
async def redirect_commands(request):
	return web.HTTPFound(website_link + '#commands')


@routes.post('/api')
async def apiindex(request):
	if request.headers['Authorization'] == os.getenv('discordbotstoken'):
		data = await request.json()
		print(data)
		await db.give_cash(int(data['user']), 100)
		await db.add_vote(int(data['user']))
		db.voted_dm_queue.append(data['user'])
		return web.Response(text='Ok')
	else:
		return web.Response(text='Invalid Auth header')


# def aiohttp_server():
# 	app = web.Application()
# 	app.add_routes(routes)
# 	app.add_routes(
# 		[
# 			web.static('/', 'static')
# 		]
# 	)
# 	handler = app.make_handler()
# 	print('created handler:', handler)
# 	return handler


def start_server(loop):
	# loop = asyncio.new_event_loop()
	# asyncio.set_event_loop(loop2)
	# app = web.Application(
	# 	# middlewares=[middleware]
	# 	loop = loop2
	# )
	# app.add_routes(routes)
	# asyncio.ensure_future(
	# 	background_task,
	# 	loop=loop
	# )
	# # app.on_startup.append(background_task)
	# web.run_app(
	# 	app,
	# 	port=9999
	# )

	asyncio.set_event_loop(loop)
	app = web.Application()
	app.add_routes(routes)
	app.add_routes(
		[
			web.static('/', 'static')
		]
	)
	runner = web.AppRunner(app)
	loop.run_until_complete(runner.setup())
	site = web.TCPSite(runner, '0.0.0.0', 8080)
	asyncio.ensure_future(site.start())
