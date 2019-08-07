import logging
from pymongo.mongo_client import MongoClient
import sys


class MongoConnection():
	'''
	Class requires some keyword arg for the connection.
	host='localhost', mongo_database='none'
	'''
	def __init__(self, host, port, mongo_database='STAF' , **vargs):
		self._host = host
		self._port = int(port)
		self.log = logging.getLogger()
		ch = logging.StreamHandler(sys.stdout)
		ch.setLevel(logging.INFO)
		formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
		ch.setFormatter(formatter)
		self.log.addHandler(ch)
		

		'Connecton opens with class properties.'
		self.log.info('Mongo connection successful to "{}"'.format(mongo_database), module='mongo_db')
		try:
			conn = MongoClient(self._host , self._port)
			self._mdbconn = conn["{}".format(mongo_database)]
		except :
			self.log.error("Database connection failed {0}".format(sys.exc_info()))


	def create_collection(self, name,keys=None, with_key=False):
		collection = self._mdbconn[name]
		if with_key:
			#create_index(self, keys, **kwargs):
			collection.create_index(keys, unique=True)
		return collection
	
	def drop_collection(self, name):
		self.log.info('Mongo drop collection: "{}"'.format(name), module='mongo_db')
		return self._mdbconn[name].drop()

	def select_all_db(self, collection_name):
		self.log.info('Mongo select from collection: "{}"'.format(collection_name), module='mongo_db')
		return self._mdbconn[collection_name].find()
	
	def find(self,collection_name,key,debug=False):
		if debug==True:
			self.log.info('Mongo find from collection: "{}",key:"{}"'.format(collection_name,key), module='mongo_db')
		return self._mdbconn[collection_name].find(key)

	def find_one(self,collection_name,key,debug=False):
		if debug==True:
			self.log.info('Mongo find_one from collection: "{}",key:"{}"'.format(collection_name,key), module='mongo_db')
		return self._mdbconn[collection_name].find_one(key)

	def select_db(self, collection_name, key, sort=None, sort_dir=1):
		'sort asc is 1 or desc  is -1'
		self.log.info('Mongo find from collection: "{}",key:"{}",sort {}'.format(collection_name,key,sort), module='mongo_db')
		if sort == None:
			cursor = self._mdbconn[collection_name].find(key)
		else:
# 			print sort , sort_dir
			cursor = self._mdbconn[collection_name].find(key).sort(sort, sort_dir)
		return cursor	
	
	def insert_db(self, collection_name, data):
		'collection name to insert, with dict of data , returns data object id'
		self.log.info('Mongo insert to collection: "{}",data:"{}"'.format(collection_name,data), module='mongo_db')
		return self._mdbconn["{}".format(collection_name)].insert(data)

	def update_db(self, collection, query, data):
		self.log.info('Mongo update to collection: "{}",query:"{}",data:"{}"'.format(collection,query,data), module='mongo_db')
		self.update(collection, query, data)
		
	def update(self, collection, colkey, data):
		# data is a dict
		self.log.info('Updating mongo_collection[{}] key:[{}],data:[{}]'.format(collection , colkey, data),module='mongo_connection')
		self._mdbconn["{}".format(collection)].update(colkey, {'$set': data})

	def upsert(self, collection, colkey, data):
		# colkey = {} and data is {} too
		self._mdbconn["{}".format(collection)].update(colkey, {'$set': data},True)

	def insert_or_update(self, collection, data, colkey='_id'):
		# data is a dict, True inserts or updates
		# collectionl.update({'_id':d['_id']}, d, True)
		self.log.info('Inserting into mongo_collections:[{}] key:[{}],data:[{}]'.format(collection , colkey, data),module='mongo_connection')
		if colkey != '_id':
			self._mdbconn["{}".format(collection)].update(dict([('{0}'.format(colkey), data['{0}'.format(colkey)])]), data, True)	
		else:
			self._mdbconn["{}".format(collection)].update({'_id': '_id'}, data, True)	

	def save(self, collection,data):
		self.log.info('Saving into mongo_collection:{} , data:{}"'.format(collection , data),module='mongo_connection')
		self._mdbconn["{}".format(collection)].save(data, True)	
		
	def remove(self, collection, arg=''):
		'remove all leave arg out, use {key:val} '
		return self._mdbconn["{}".format(collection)].remove(arg)

	def disconnect_db(self):
		self.mconn.disconnect()

	def close(self):
		self._mongoconn.close()

	def get_cursor(self):
		return self._cursor

if __name__ == '__main__':
	mongo = MongoConnection('localhost' , 27017, mongo_database='staf')
	m = mongo.create_collection('test')
	mongo.save('test_save',{'dat':5})
	mongo.save('test_save',{'_id':'this id','dat':5})
	
