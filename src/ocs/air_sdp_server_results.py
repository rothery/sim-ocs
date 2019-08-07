""" 
Sept 2014
The config is from a config file that loads some test msisdns into mongo, 
the validation will work off this mongo data
"""
from ocs.mongo_conn import MongoConnection


mongo_port = 27017

class SdpResults():
    def __init__(self):
        self.mongo = MongoConnection('localhost' , mongo_port, mongo_database='staf')
        self.mongo.remove('air_sdp_trans',{ })

    def persist_sdp_results_in_mongo(self,res):
        'put the results in mongo, easy to collect with the key'
        self.mongo.insert_db('air_sdp_trans', res)

    def persist_sdp_results_marker(self,id,state):
        'put the results in mongo, easy to collect with the key'
        self.mongo.insert_db('air_sdp_trans', id,state)
    
    
if __name__ == '__main__':
    res = {'one':'u2'}
    sdpr = SdpResults()
    sdpr.persist_sdp_results_in_mongo(res)
    
