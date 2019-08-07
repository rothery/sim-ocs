# from operations.core.ericsson.ocs.air_sdp_server_results import SdpResults
import datetime
import random
import xml.dom

from glob_variables import mongo_port
from operations.connections.mongo.connection import MongoConnection
from operations.sas.get_ussd_req import post_ussd_xmlrpc, ussd_format_time
from operations.sas.read_sas_resp import ReadSASResponse


mongo = MongoConnection('localhost' , mongo_port, mongo_database='staf')

ti = random.randrange(10000, 99999)
d = datetime.datetime.now()
dn = ussd_format_time(d)

mongo.insert_db('air_sdp_trans', {'originTransactionID' : ti , "state" : 'Start', 'test_date' : d })
x = post_ussd_xmlrpc('172.28.200.112', 8082, MSISDN='0711231001', transactionID=ti, TransactionTime=dn , USSDRequestString='1')
dom = xml.dom.minidom.parseString(str(x.read()))

resp = ReadSASResponse(dom)
for i in resp.get_result():
    print 'resp ',i


for i in mongo.select_db('air_sdp_trans', {'test_date' : {"$gte" : d }}):
    print i


