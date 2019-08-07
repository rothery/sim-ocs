'functions to read mongo for service class / offer testing'
from pymongo.mongo_client import MongoClient


def read_service_class(subscriber_info):
    print "subscriber_info", subscriber_info
    
    """Subscriber data for known subscriber. 
    dict: {u'ussdEndOfCallNotificationID': 1, u'serviceOfferCurrent': u'0000000000000000000000000000000', 
    u'main_account_balance': u'0', u'languageIDCurrent': 1, u'serviceClass': 7, u'_id': u'071123100456'}
    """
    mcl = MongoClient()        
    
    mongo_air_sdp_config = mcl["staf"]["air_sdp_config"]
    s = "service_class_{}".format(subscriber_info['serviceClass'])
    r = mongo_air_sdp_config.find_one({"_id" : s})
    if r:
        print r["value"]
    else:
        print 'skip'


if __name__ == '__main__':
    read_service_class({u'ussdEndOfCallNotificationID': 1, u'serviceOfferCurrent': u'0000000000000000000000000000000',
    u'main_account_balance': u'0', u'languageIDCurrent': 1, u'serviceClass': 7, u'_id': u'071123100456'})
    
    
    read_service_class({u'ussdEndOfCallNotificationID': 1, u'serviceOfferCurrent': u'0000000000000000000000000001000',
    u'main_account_balance': u'0', u'languageIDCurrent': 1, u'serviceClass': 120, u'_id': u'071123100456'})

    read_service_class({u'ussdEndOfCallNotificationID': 1, u'serviceOfferCurrent': u'0000000000000000000000000001000',
    u'main_account_balance': u'0', u'languageIDCurrent': 1, u'serviceClass': 12000, u'_id': u'071123100456'})
