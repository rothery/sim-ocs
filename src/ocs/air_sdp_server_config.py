
from ocs.mongo_conn import MongoConnection


def persist_config_mongo():
    'read config, persist to mongo doc store, close'
    
    mongo = MongoConnection('localhost' , 27017, mongo_database='staf')


# [air_sdp_config]

    l = [{"service_class_dt" : 1},{"service_class_non_dt": 7},{"service_offer_dt" : "0000100000000000000000000000000"},
         {"service_offer_non_dt" : "0000000000000000000000000000000"}]
    
    for d in l:
        mongo.save('air_sdp_msisdns', d)

    
if __name__ == '__main__':
    persist_config_mongo()
    
