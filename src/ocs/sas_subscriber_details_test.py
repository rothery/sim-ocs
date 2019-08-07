import unittest

from glob_variables import mongo_port
from operations.connections.mongo.connection import MongoConnection
from operations.core.ericsson.ocs.sas_subscriber_details import \
    SasSubscriberDetails


class SasSubscriberDetailsTest(unittest.TestCase):
    def setUp(self):
        self.mongo = MongoConnection('localhost' , mongo_port, mongo_database='staf')
        print self.mongo.insert_db('subscriber_details', {'subscriberNumber' : '12345'})
        self.ssd = SasSubscriberDetails()


    def test_insert_data(self):
        c = self.mongo.select_db('subscriber_details', {'subscriberNumber' : '12345'})
        self.assertEqual(c[0]['subscriberNumber'] , '12345')

    def test_get_sas_sub_data(self):
        x =  self.ssd.get_subscriber_details('12345')
        print 'ssd', x , len(x)
    
    def test_get_sas_sub_data_neg(self):
        x = self.ssd.get_subscriber_details('123456')
        print 'ssd_neg', x

    def test_update_sas_sub(self):
        self.ssd.update_subscriber_details(12345, {'new_data':'123'})
        print 'ssd_update', [x for x in self.mongo.select_db('subscriber_details', {'subscriberNumber' : '12345'})]

    def tearDown(self):
        self.mongo.remove('subscriber_details', {'subscriberNumber' : '12345'})
#                     self.mongo.insert_db('offers', xml)

if __name__ == '__main__':
    unittest.main()
        
