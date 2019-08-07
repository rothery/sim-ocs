#!/usr/bin/python
from  datetime import datetime as dt
import datetime
from pymongo.mongo_client import MongoClient
import random


# mongo = MongoConnection('localhost' , 27017, mongo_database='staf')
cl = MongoClient()        
mongo_staf = cl["staf"]  # ["offers"]

def sdp_offer_mgr(mongo):

    for i in mongo.offers.find({"expiryDateTime": { '$lte' :  datetime.datetime.utcnow() } }):
        print 'remove expiry date', i 
        mongo.offers.remove(i['_id'])

    # wind down
    print 'counting down with sdp offer mgr'
    for i in mongo.offers.find():
        if 'offer_units' not in i:
            offer_id = str(int(i['offerID']))
            if offer_id[0] in ['4']:  # 4 data.
                print int(offer_id[3:]) 
                i['offer_units'] = int(offer_id[3:]) * 1000000  # data
            else : 
                i['offer_units'] = int(offer_id[3:])  # minutes
            
            mongo.offers.save(i) 
            print 'updating offer_units as there are none, ', i

        else:
            # units - (units/((24 * days)*(20%))
            units = int(i['offer_units'])
            d = units * random.randint(80, 120) / 100.0
            x = (units * 24 * 60* int(str(i['offerID'])[2:3])) / d 
            print 'offer_units:{0} offer counter {1} ,less:{2}'.format(i['offer_units'], i['offer_counter'], x)
    
            i['offer_counter'] = i['offer_counter'] + x

            if i['offer_counter'] > i['offer_units']:
                print 'remove', i['_id'], i
                mongo.offers.remove(i['_id'])
            else:
                mongo.offers.save(i)
            continue
        
# for i in range(100):

sdp_offer_mgr(mongo_staf)
    

