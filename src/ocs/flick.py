import json
from pymongo.mongo_client import MongoClient
import random
import requests
import sys

from operations.connections.mongo.mongo_expire import MongoExpire


mon_flick_login = MongoExpire('flick', 'my_login', expire_after=3600)
mongoc = MongoClient('localhost', 27017)        
url = 'http://api.hotsocket.co.za:8080'
# url = 'https://v1.hotsocket.co.za'

uname = 'rorotikamobile'


def get_token():
    'returns token for rorotikamobile'
    j = None
    for i in  mon_flick_login.find_event('rorotikamobile'):
        j = i
    if j:
        mon_flick_login.log.info('found token {}'.format(i))
        token = i['token']
    else : 
        mon_flick_login.log.info("Create token")
        payload = {'username': uname, 'password': 'XEBDgUTEvy2mvtqzQ6WS', 'as_json': 'true'}
        
        # GET
        r = requests.get('{}/login/'.format(url))
        
        # GET with params in URL'
        # r = requests.get(url, params=payload)
        # POST with form-encoded data
        r = requests.post('{}/login/'.format(url), data=payload)
        
        # Response, status etc
        print r.text
        print r.status_code
        '''{"response":{"message":"Login Successful.","status":"0000","token":"e_EnJww2AMelIyBwuW_sUf3SD6zEHobb9FP1Iv_BVVgSmaSAIOcKUY606t8u1F4ja5nG-yLUfiTmdsF0shi9-A"}}'''        
        d = json.loads(r.text)
        token = d['response']['token']
        
        ds = {"_id" : uname}
        ds["token"] = d["response"]["token"]
        
        mon_flick_login.save(ds)
    
    return token


def buy_bundle( msisdn, denomination='5', type='DATA'):
    'DATA, AIRTIME , denomination is diff for different operators'

    db = mongoc["flick"]
    mm = db['testcol']
    mm.update({"_id":"purchaces"} , {"$inc":{"cnt":1}},True)
    i = mm.find({"_id":"purchaces"})
    ref = i[0]['cnt']
    
    r_send = {'token': get_token() , 
              'username': uname ,
              'recipient_msisdn': msisdn,
              'product_code': 'DATA',
              'denomination': denomination,
              'network_code': 'MTN',
              'reference':  ref ,
              'notes': 'Test demo server',
              'as_json': 'true'}  
    mon_flick_login.log.info('Recharge send: {}'.format(r_send))  
    r = requests.post('{}/recharge/'.format(url), data=r_send)
 
    print r.status_code
     
    mon_flick_login.log.info('Recharge rec: {}'.format(r.text))
    return r.text


def get_statement( msisdn=None): 
    r_send = {'token': get_token() ,
              'username': uname ,
              'start_date': '2019-01-01' ,
              'end_date': '2019-02-01' ,
              'recipient_msisdn': msisdn,
              'as_json': 'true'}
    mon_flick_login.log.info('Statement send: {}'.format(r_send))
    r = requests.post('{}/statement/'.format(url), data=r_send)
    mon_flick_login.log.info('Statement rec: {}'.format(r.text))

# get_statement('27821231234')


def get_status(ref=9988, hs_ref=99881): 
    r_send = {'token': get_token() ,
              'username': uname ,
              'reference': ref ,
              'hotsocket_ref': hs_ref ,
              'as_json': 'true'}
    mon_flick_login.log.info('Status send: {}'.format(r_send))
    r = requests.post('{}/status/'.format(url), data=r_send)
    mon_flick_login.log.info('Status rec: {}'.format(r.text))



def get_balance():
    r_send = {'token': get_token() ,
              'username': uname ,
              'as_json': 'true'}
    mon_flick_login.log.info('Get balance send: {}'.format(r_send))
    r = requests.post('{}/balance/'.format(url), data=r_send)
    mon_flick_login.log.info('Get balance rec : {}'.format(r.text))


if __name__ == '__main__':
#     print get_token()
    print
#     print get_balance()
    print buy_bundle('27835017855')
#     print get_status(345345345)

