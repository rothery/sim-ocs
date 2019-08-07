
# Balance and DATE

import datetime
import dateutil.tz
import xml
import xmlrpclib


dt = datetime.datetime.now()
dt_now = dt # .replace(tzinfo=dateutil.tz.gettz('SAST')) 


#FIRST

# proxy = xmlrpclib.ServerProxy("http://172.28.200.102:10010/")
proxy = xmlrpclib.ServerProxy("http://localhost:10010/Air")

p = {   'originHostName' : 'STAF_TEST',
        'originNodeType' : 'EXT',
        'originTransactionID' : '12341234',
        'originTimeStamp' : dt_now,
        'subscriberNumber' : '071123100456333',
        'subscriberNumberNAI' : 2L
    }

print "Send Get getAccountDetals" , p
x = proxy.GetAccountDetails(p)
for k,v in x.iteritems(): 
    print "{}={}".format(k,v)
    
print "Send Get BalanceAndDate" , p
x = proxy.GetBalanceAndDate(p)
for k,v in x.iteritems(): 
    print "{}={}".format(k,v)
