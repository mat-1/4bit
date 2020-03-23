import motor.motor_asyncio
import os
import asyncio
from datetime import datetime


loop = asyncio.get_event_loop()


class Database:
	def __init__(self):
		self.username = os.getenv('dbuser')
		self.password = os.getenv('dbpass')
		self.conn = motor.motor_asyncio.AsyncIOMotorClient(
			f'mongodb+srv://{self.username}:{self.password}@cluster0-2ixzl.mongodb.net/fourbit?retryWrites=true&w=majority'
		)
		self.db = self.conn['fourbit']
		self.users = self.db.users
		self.servers = self.db.servers
		self.votes = self.db.votes

		self.voted_dm_queue = []

	async def new_user(self, userid):
		result = await self.users.insert_one({'_id': userid, 'cash': 0})
		return result

	async def new_server(self, serverid):
		result = await self.servers.insert_one({'_id': serverid})
		return result

	async def get_user(self, userid, createnew=True):
		if type(userid) == str:
			userid = str(userid)
		elif type(userid) != int:
			userid = userid.id
		userinfo = await self.users.find_one({'_id': userid})
		if userinfo is None:
			if not createnew:
				raise Exception
			await self.new_user(userid)
			return await self.get_user(userid, createnew)
		if 'cash' not in userinfo:
			userinfo['cash'] = 0
		return userinfo

	async def get_user_value(self, userid, key, default=None):
		userinfo = await self.get_user(userid)
		if key in userinfo:
			return userinfo[key]
		else:
			userinfo[key] = default
			await self.set_userinfo(userid, userinfo)
			return default

	async def get_server(self, serverid, createnew=True):
		serverinfo = await self.servers.find_one({'_id': serverid})
		if serverinfo is None:
			if not createnew:
				raise Exception('Server not found')
			await self.new_server(serverid)
			return await self.get_server(serverid, createnew)
		return serverinfo

	async def edit_user(self, userid, key, value):
		userinfo = await self.get_user(userid)
		userinfo[key] = value
		return await self.set_userinfo(userid, userinfo)

	async def edit_server(self, serverid, key, value):
		serverinfo = await self.get_server(serverid)
		serverinfo[key] = value
		return await self.set_serverinfo(serverid, serverinfo)

	async def set_userinfo(self, userid, userinfo):
		resultdata = await self.users.update_one(
			{'_id': userid},
			{'$set': userinfo},
			upsert=True
		)
		return resultdata.raw_result

	async def add_userinfo(self, userid, userinfo):
		resultdata = await self.users.update_one(
			{'_id': userid},
			{'$inc': userinfo},
			upsert=True
		)
		return resultdata.raw_result


	async def set_serverinfo(self, serverid, serverinfo):
		resultdata = await self.servers.update_one(
			{'_id': serverid},
			{'$set': serverinfo},
			upsert=False
		)
		return resultdata.raw_result

	async def give_cash(self, userid, amount):
		await self.add_userinfo(userid, {'cash': amount})

	async def get_cash(self, userid):
		userdata = await self.get_user(userid)
		return userdata.get('cash', 20)

	async def add_vote(self, userid):
		await self.votes.update_one(
			{'_id': userid},
			{'$set': {'vote_time': datetime.now()}}
		)

	async def get_vote(self, userid):
		resultdata = await self.votes.find_one({'_id': userid})
		return resultdata

	async def has_voted(self, userid):
		v = await self.get_vote(userid)
		if v is None:
			return False
		print(v)
		return True

db = Database()