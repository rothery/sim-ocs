from ocs.mongo_conn import MongoConnection

mongo_port = 27017

class SasSubscriberDetails():
    def __init__(self):
        self.mongo = MongoConnection('localhost' , mongo_port, mongo_database='staf')


    def get_subscriber_details(self,subscriber_number):
        x = list(self.mongo.select_db('air_sdp_msisdns', {'_id' : subscriber_number}))
        if len(x) > 0:
            return x[0] #send a dict 
        else:
            return {u'ussdEndOfCallNotificationID': 1 ,'serviceClass': 7, 'dtactive': True, u'discount': 70, u'languageIDCurrent': 1, u'_id': u'{}'.format(subscriber_number)}
        
    def update_subscriber_details(self,subscriber_number,new_data):
        'new_data is a dict'
        self.mongo.insert_or_update('air_sdp_msisdns',new_data, 'subscriber_number')

            
    def provision_new_staf_sub(self,subscriber_number):
        d = {'subscriberNumber' : subscriber_number, 'service_class' : 'from_config_file'}   
        self.mongo.insert_db('subscriber_details', d )

        