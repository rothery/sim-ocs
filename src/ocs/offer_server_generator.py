from glob_variables import mongo_port
from libs.read_config.read_config_files import Configuration
from operations.connections.mongo.connection import MongoConnection
from operations.scheduler.schedules import Schedules


class OffersGenerator(object):
    '''This is a generator that will increase the data usage for subscribers.  
       the data usage goes up to simulate a subscriber
       The main point of test is to test data for offers. 
       voice minutes / bundles and sms can be added, just not real reason for a simulator
       and thus needs to be implemented.
    
    '''
    
    def __init__(self):
        self.mongo = MongoConnection('localhost' , mongo_port, mongo_database='staf')
        self.conf = Configuration('config/core/ericsson/ocs/')
        print self.conf

    def schedule_min(self):
        print '1'


    def create_something(self):
        pass