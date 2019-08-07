#!/usr/bin/python
import datetime
import dateutil.parser
import dateutil.tz
import pprint
from pymongo.mongo_client import MongoClient
import random
import sys
import time
from twisted.internet import reactor
from twisted.python import log, logfile
from twisted.web import xmlrpc
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.web.xmlrpc import withRequest
from xml.dom.minidom import parseString
import xmlrpclib

from ocs.air_sdp_server_config import persist_config_mongo
from ocs.air_sdp_server_results import SdpResults
from ocs.mongo_conn import MongoConnection
from ocs.sas_subscriber_details import SasSubscriberDetails


mongo_port = 27017

# from twisted.manhole import gladereactor
# gladereactor.install()
Fault = xmlrpclib.Fault


def timeit(func):

    def wrapper(*arg):
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        print '[%s] took %0.3f ms' % (func.func_name, (t2 - t1) * 1000.0)
        return res

    return wrapper

    
class FormPage(Resource):

    def __init__(self):
        pass
            
    def render_GET(self, request):
        return '<html><body><form method="POST"><input name="the-field" type="text" /></form></body></html>'

    def render_POST(self, request):
        return '<html><body>You submitted: s</body></html>'
    
    def Connection(self):
        sys.exit(6)


class AirSdpServer(xmlrpc.XMLRPC):
    """
    This server is for SDP transactions from SAS and CGW. 
    Validation 
    """
    
    def __init__(self, allowNone=False, useDateTime=False , return_failures=5):
        'Failures returned are 5% by default'
        xmlrpc.XMLRPC.__init__(self, allowNone=allowNone, useDateTime=useDateTime)
    
        self.return_failures = return_failures
        

        print return_failures
        print('starting OCS server with return_failures= {} % \n'.format(return_failures))
        self.ssd = SasSubscriberDetails()        
        self.pp = pprint.PrettyPrinter(indent=2)

        self.sdpr = SdpResults() 
        self.mongo = MongoConnection('localhost' , mongo_port, mongo_database='staf')
        cl = MongoClient('localhost', 27017)        

        self.mongo_air_sdp_msisdns = cl["staf"]["air_sdp_msisdns"] 
        self.mongo_demo_msisdns = cl["staf"]["demo_msisdns"] 
        self.mongo_offers = cl["staf"]["offers"]
        self.mongo_air_sdp_config = cl["staf"]["air_sdp_config"]
        # loads a config file
    
    def dt_now(self):
        dt = datetime.datetime.now()
        d = dt.replace(tzinfo=dateutil.tz.gettz('GMT'))
        return d

    def dt_20mins(self):
        dt = self.dt_now()
        self.dt_now_GMT = dt.replace(tzinfo=dateutil.tz.gettz('GMT')) 
        delta = datetime.timedelta(minutes=20)        
        r = dt + delta
        return r.replace(tzinfo=dateutil.tz.gettz('GMT'))

    def gen_future_dt(self, min_from_now):
        'returns GMT'
        delta = datetime.timedelta(minutes=min_from_now)      
        r = self.dt_now() + delta
        return r.replace(tzinfo=dateutil.tz.gettz('GMT'))
#         return dt_20min.replace(tzinfo=dateutil.tz.gettz('GMT')) 

    def update_offer(self, xml):
        '''{'originTransactionID': 10172, 'originHostName': 'VXMLIVR1', 'subscriberNumber': '47112288', 
        'subscriberNumberNAIstruct': 2, 'offerID': 8, 'originTimeStamp': <DateTime '20140226T11:36:33' at 3447998>, 
        'originNodeType': 'EXT', 'productID': 2}'''

        d = (xml['originTimeStamp'])
        ot = dateutil.parser.parse(str(xml['originTimeStamp']))
        if 'expiryDateTime' in xml:
            et = dateutil.parser.parse(str(xml['expiryDateTime']))
        else:
            from dateutil.relativedelta import relativedelta
            et = ot + relativedelta(years=1)

        #### nothing complicated.  NEGATIVE TEST
        if self.is_this_the_bad_resp(self.return_failures):
            log.msg("Bad response sent to CGW ")

            xml['productID'] = 1
            xml['originTimeStamp'] = str(d)
            xml['originTimeStamp'] = ot
            xml['expiryDateTime'] = et
    
            response = {}
            response['availableServerCapabilities'] = 100L
            response['negotiatedCapabilities'] = 0
            response['originTransactionID'] = xml['originTransactionID']
            response['responseCode'] = 102L  # Subscriber not found

        else:

            xml['originTimeStamp'] = str(d)
    
            xml['productID'] = 1
            last_productID = 1  # def
            for i in self.mongo.select_db('offers', {'subscriberNumber' : xml['subscriberNumber']}, sort='originTimeStamp'):
                last_productID = i['productID']
                
            xml['productID'] += last_productID
            xml['originTimeStamp'] = ot
            xml['expiryDateTime'] = et
            xml['startDateTime'] = ot
            xml['offer_counter'] = 0  # Init
            if 'offerType' not in xml:
                xml['offerType'] = 2  # standard 
            log.msg("mongo.offers.save({})".format(xml))
            self.mongo.save('offers', xml)
    
            response = {}
            response['availableServerCapabilities'] = 100L
            response['expiryDateTime'] = et
            response['negotiatedCapabilities'] = 0
            response['offerID'] = 11L
            response['offerState'] = 0
            response['offerType'] = 2
            response['offerType'] = xml['offerType']
            
            if 'originOperatorID' in xml:
                response['originOperatorID'] = xml['originOperatorID']
            response['originTransactionID'] = xml['originTransactionID']
            response['productID'] = xml['productID']
            response['responseCode'] = 0
            response['startDateTime'] = ot
              
        self.pp.pprint(response)
        return response

    def is_this_the_bad_resp(self, pct_in):
        if random.randint(1, 100) <= pct_in:
            return True
        return False

    def delete_offer(self, xml):
        m = xml['subscriberNumber']
        if 'productID'in xml:
            # assume if there no product id there no value
            p = int(xml['productID'])        
            d = {"subscriberNumber":m, "productID":p}
            log.msg("Remove offer".format(d))
            self.mongo.remove('offers', d)
        else: log.msg("no product ID, not removing product from mongo datastore")
        
        response = {}
        response['availableServerCapabilities'] = [100]
        response['originTransactionID'] = xml['originTransactionID']
        response['negotiatedCapabilities'] = [0]
        response['responseCode'] = 0
        response['originTransactionID'] = xml['originTransactionID']
        self.pp.pprint(response)
        return response
  
    def execution_response(self):
        response = {}
        response['responseCode'] = 0
        response['originTransactionID'] = 'pjs_pc'
        self.pp.pprint(response)
        return response
    
    def get_balance_and_date_response(self, xml):
        '''{'creditClearanceDate': <DateTime '20140531T12:00:00+0000' at 793200>, 'availableServerCapabilities':
         [4346368], 'originTransactionID': '28167', 'offerInformationList': [{'expiryDateTime': <DateTime '20140409T10:52:55+0200' at 7934d0>,
          'offerID': 10, 'offerState': 0, 'startDateTime': <DateTime '20140409T09:32:56+0200' at 793518>, 
          'offerType': 2, 'productID': 93}, {'expiryDateTime': <DateTime '20140409T15:30:12+0200' at 793560>, 
          'offerID': 30, 'offerState': 0, 'startDateTime': <DateTime '20140408T15:56:38+0200' at 7935a8>, 
          'offerType': 2, 'productID': 92}], 'serviceFeeExpiryDate': <DateTime '20140531T12:00:00+0000' at 7935f0>, 
          'accountFlagsBefore': {'activationStatusFlag': True, 'supervisionPeriodExpiryFlag': False, 'supervisionPeriodWarningActiveFlag': False, 
          'negativeBarringStatusFlag': False, 'serviceFeePeriodExpiryFlag': False, 'serviceFeePeriodWarningActiveFlag': False}, 'serviceClassCurrent': 1, 
          'supervisionExpiryDate': <DateTime '20140531T12:00:00+0000' at 793680>, 'currency1': 'SEK', 'accountFlagsAfter': {'activationStatusFlag': True, 
          'supervisionPeriodExpiryFlag': False, 'supervisionPeriodWarningActiveFlag': False, 'negativeBarringStatusFlag': False,
           'serviceFeePeriodExpiryFlag': False, 'serviceFeePeriodWarningActiveFlag': False}, 
           'responseCode': 0, 'languageIDCurrent': 1, 'accountValue1': '176858', 'serviceRemovalDate': <DateTime '20140531T12:00:00+0000' at 793638>,
            'negotiatedCapabilities': [0]}
        '''
        sd = self.ssd.get_subscriber_details(xml['subscriberNumber'])
        response = {}
        response['responseCode'] = 0
        response['originTransactionID'] = xml['originTransactionID']
        response['serviceClassCurrent'] = int(sd['serviceClass'])
        response['currency1'] = 'ZAR'
        response['accountValue1'] = str(sd['main_account_balance'])
        response['currency2'] = 'ZAR'
        response['accountValue2'] = '99'

        response['dedicatedAccountInformation'] = self.create_dedicated_accounts(xml['subscriberNumber'], sd)

        lst = []
        log.msg("mongo_offers.find subscriberNumber : {}".format(xml['subscriberNumber']))
        mof = self.mongo_offers.find({"subscriberNumber": "{}".format(xml['subscriberNumber'])})
        for i in mof:
            log.msg("Found-{}".format(i))

            lst1 = []
            for c, j in enumerate(mof):    
                
                lst1.append({'usageCounterID': j['offerID'], 'usageCounterValue' : str(int(j['offer_counter'])), \
                             'usageThresholdInformationList':[ {'usageCounterID': 0, 'usageCounterValue' : str(int(j['offer_counter']))}]})
 
            try:
                ts = i['startDateTime']
            except:
                ts = i['originTimeStamp'] 
            
            lst.append({'offerID': i['offerID'], 'offerState': 0, 'offerType': i['offerType'], 'productID': i['productID'], \
                        'startDateTime': ts.replace(tzinfo=dateutil.tz.gettz('GMT')), \
                        'expiryDateTime': i['expiryDateTime'].replace(tzinfo=dateutil.tz.gettz('GMT')), \
                        'usageCounterUsageThresholdInformation' : lst1 })

            log.msg("Get balance and data,{}".format(lst))
            break;  # Only need one

        response['offerInformationList'] = lst
        response["supervisionExpiryDate"] = self.dt_20mins()
        response["serviceFeeExpiryDate"] = self.dt_20mins()
        response["creditClearanceDate"] = self.dt_20mins()
        response["serviceRemovalDate"] = self.dt_20mins()
        response["languageIDCurrent"] = int(sd['languageIDCurrent'])
        response["counters"] = {}

        self.pp.pprint(response)
        
        return response
        
    def create_dedicated_accounts(self, msisdn, sd):
        '''
        #dedicatedAccountActiveValue1 = "0"
        dedicatedAccountID = 50
        dedicatedAccountUnitType = 6 # volume
        dedicatedAccountValue1 = "344324"
        expiryDate 
        startDate dateTime.iso8601>00000101T12:00:00+0000</dateTime.iso8601>
        '''
        dtn = self.dt_now()
        dtf = self.gen_future_dt(10000) 
        # Voice is 2-5
        # SMS 6,7
        # Data 8-20
        dat = {1:1, 2:1, 3:1, 4:1, 5:1, 6:2, 7:2, 8:6, 9:6, 10:6, 11:6, 12:6, 13:6, 14:6, 15:6, 16:6, 17:6, 18:6, 19:6, 20:6, 30:1, 31:1, 32:2, 33:4, 34:4, 35:4, 36:7, 37:7, 38:7}
        if "info" not in sd:
            lst = []
            for i in dat:
                if i == 1:
                    sv = "20000"
                else:sv = "0"
                lst.append({"dedicatedAccountID": i, "dedicatedAccountValue1":sv, \
                            "dedicatedAccountUnitType" : dat[i], "subDedicatedAccountInformation":[]})
            d = sd 
            d["info"] = lst
            self.mongo_air_sdp_msisdns.update({ "_id" : msisdn}, d)
        
        ret = []
        x = self.mongo_air_sdp_msisdns.find_one({ "_id" : '{}'.format(msisdn)})["info"]
        for i in x:
            v = i
            v["dedicatedAccountID"] = int(i["dedicatedAccountID"])
            v["dedicatedAccountUnitType"] = int(i["dedicatedAccountUnitType"])
            v["dedicatedAccountValue1"] = str(i["dedicatedAccountValue1"])
            if "expiryDate" in i:
                dt = i["expiryDate"].replace(tzinfo=dateutil.tz.gettz('GMT'))
            else : dt = dtf
            v["expiryDate"] = dt
            v["startDate"] = dtn
            ret.append(v)
        return ret
 
    def get_offers_response(self, xml):
        
        response = {}
        response['availableServerCapabilities'] = [100]
        response['originTransactionID'] = xml['originTransactionID']
        response['negotiatedCapabilities'] = [0]
        response['responseCode'] = 0
        response['originTransactionID'] = xml['originTransactionID']
        response['offerInformation'] = ('1000', '1002', '1003', '1004', '1005', '1006', '1007', '1008', '1009', '1010')
        self.pp.pprint(response)
        
        return response

    def get_usage_threshold_counters(self, xml):
                
        response = {}
        uc = {}
        response['availableServerCapabilities'] = [100]
        response['negotiatedCapabilities'] = [0]
        response['originTransactionID'] = xml['originTransactionID']

        lst = []
        for c, i in enumerate(self.mongo_offers.find({"subscriberNumber": "{}".format(xml['subscriberNumber'])})):

            lst.append({'usageCounterID': i['offerID'], 'usageCounterValue' : str(int(i['offer_counter']))})
            log.msg("Get usage threshold counters ,#{}:{}".format(c, lst))
                    
        response['usageCounterUsageThresholdInformation'] = lst  # [uc]
        response['responseCode'] = 0
        self.pp.pprint(response)
        
        return response

    def get_account_details(self, xml):
        response = {}
        af = {}
        afb = {}
        sos = {}
        sd = self.ssd.get_subscriber_details(xml['subscriberNumber'])
        """[{u''ussdEndOfCallNotificationID' = 2': True, u'_id': u'0711231001', u'dtactive': True, u'discount': 70},'language':1]
        """
        af['activationStatusFlag'] = True
        af['negativeBarringStatusFlag'] = False
        af['serviceFeePeriodExpiryFlag'] = False
        af['serviceFeePeriodWarningActiveFlag'] = False
        af['supervisionPeriodExpiryFlag'] = False
        af['supervisionPeriodWarningActiveFlag'] = False
        response['accountFlags'] = af
        afb['activationStatusFlag'] = True
        afb['negativeBarringStatusFlag'] = False
        afb['serviceFeePeriodExpiryFlag'] = False
        afb['serviceFeePeriodWarningActiveFlag'] = False
        afb['supervisionPeriodExpiryFlag'] = False
        afb['supervisionPeriodWarningActiveFlag'] = False
        response['accountFlagsBefore'] = afb
        response['accountGroupID'] = 0
        response['activationDate'] = self.dt_now()
        response['creditClearanceDate'] = self.dt_20mins()
        response['creditClearancePeriod'] = 999
        response['firstIVRCallFlag'] = True
        response['languageIDCurrent'] = int(sd['languageIDCurrent'])  # Eng
        response['masterAccountNumber'] = 973838650
        response['masterSubscriberFlag'] = True
        response['maxServiceFeePeriod'] = 999
        response['maxSupervisionPeriod'] = 999
        response['originTransactionID'] = xml['originTransactionID']
        response['responseCode'] = 0 
        
        if 'serviceClass' in sd:
            response['serviceClassCurrent'] = int(sd['serviceClass'])
        else:
            mc = self.mongo_air_sdp_config.find_one({"_id" : "service_class_non_dt"})
            "{u'_id': u'service_class_non_dt', u'value': u'120'}"            
            response['serviceClassCurrent'] = int(mc["value"])
        print 'SC current', response['serviceClassCurrent'], type(response['serviceClassCurrent'])

        response['serviceFeeExpiryDate'] = self.dt_20mins()
        response['serviceFeePeriod'] = 972 

        if 'serviceOfferCurrent' in sd:
            so = sd['serviceOfferCurrent']
        else:
            so = self.mongo_air_sdp_config.find_one({"_id" : "service_offer_non_dt"})['value']
            "{u'_id': u'service_class_non_dt', u'value': u'000010000000000000000000000000'}"            
        self.serviceOffers = so
        sos = []
        for idx, i in enumerate(so):
            so = {}
            if i == '0':
                so['serviceOfferingActiveFlag'] = False
            else:
                so['serviceOfferingActiveFlag'] = True
            idx += 1
            so['serviceOfferingID'] = idx
            sos.append(so)

        print 'Service offerings', sos
        response['serviceOfferings'] = sos
        delta = datetime.timedelta(days=5)        
        dt_5days = self.dt_20mins() 
        z = dt_5days.replace(tzinfo=dateutil.tz.gettz('GMT')) 
        response['serviceRemovalDate'] = z
        response['serviceRemovalPeriod'] = 999 
        response['supervisionExpiryDate'] = self.dt_now()
        response['supervisionPeriod'] = 972 
#        response['ussdEndOfCallNotificationID'] = 2
        if 'ussdEndOfCallNotificationID' in sd:
            response['ussdEndOfCallNotificationID'] = int(sd['ussdEndOfCallNotificationID'])
        else:
            response['ussdEndOfCallNotificationID'] = 2
        
        import string
        oil = [{'attributeName' : "Segment", "attributeValueString" : random.choice(string.letters)}]
        
        response['offerInformationList'] = [{'attributeInformationList': oil, "offerID":88, "offerState":0, "offerType":2, "startDateTime":z}]
           
        self.pp.pprint(response)
        return response

    def update_subscriber_segmentation(self, xml):
        response = {}
        response['responseCode'] = 0
        response['originTransactionID'] = xml['originTransactionID']
        self.pp.pprint(response)
        
        return response
    
    def update_usage_thresholds_and_counters(self, xml):

        response = {}
        response['responseCode'] = 0
        response['originTransactionID'] = xml['originTransactionID']
        response['negotiatedCapabilities'] = 0
        response['availableServerCapabilities'] = 0

        updateUsageThresholdsAndCounters = {}    
        updateUsageThresholdsAndCounters["usageCounterID"] = xml['usageCounterUpdateInformation'][0]['usageCounterID']
        updateUsageThresholdsAndCounters["usageCounterValue"] = xml['usageCounterUpdateInformation'][0]['usageCounterValueNew']
        usageThresholdInformation = {}
        usageThresholdInformation["usageThresholdID"] = 10
        usageThresholdInformation["usageThresholdValue"] = "400"
        usageThresholdInformation["usageThresholdSource"] = 2  # ##x2
#             associatedPartyID-optional
        updateUsageThresholdsAndCounters["usageThresholdInformation"] = usageThresholdInformation
        response['updateUsageThresholdsAndCounters'] = updateUsageThresholdsAndCounters
        
        self.pp.pprint(response)
        
        return response
    
    def update_account_details(self, xml):
        
        response = {}
        response['responseCode'] = 0
        response['originTransactionID'] = xml['originTransactionID']
        self.pp.pprint(response)
        
        return response

    def update_std_resp(self, xml):
        'response is std dic.'
        response = {}
        response['responseCode'] = 0
        response['originTransactionID'] = xml['originTransactionID']
        self.pp.pprint(response)
        
        return response

    def update_serviceOfferings(self, xml):
        d = self.get_subscriber_detail(xml['subscriberNumber'])
        
        sof = d['serviceOfferCurrent']
        for lst_offering in xml['serviceOfferings']:          
            "[{'serviceOfferingID': 30, 'serviceOfferingActiveFlag': True}, {'serviceOfferingID': 28,  'serviceOfferingActiveFlag': True}, {'serviceOfferingID': 29, 'serviceOfferingActiveFlag': True}]"
            ss = sof
            i = lst_offering['serviceOfferingID']  # "{'serviceOfferingID': 28, 'serviceOfferingActiveFlag': True}"
            i -= 1
            sof = ss[:i] + str(int(lst_offering['serviceOfferingActiveFlag']))
            i += 1
            sof += ss[i:]
            
        return sof
    
    def read_req(self, request, xml):
        request.content.seek(0, 0)
        requestXMLContent = request.content.read()
        paramRawText = '[' + str(datetime.datetime.now()) + '] \n'
        dom = parseString(requestXMLContent)
        paramRawText = paramRawText + dom.toprettyxml() + '\n'
        for i in range(80):
            paramRawText = paramRawText + '-'
        paramRawText = paramRawText + '\n'
        print 'Received:\n' + paramRawText
        ts = xml
        ts['originTimeStamp'] = str(xml['originTimeStamp'])
        ts["action"] = "request_rec" 
        ts['test_date'] = self.dt_now()
        #REMOVED!!!
#         self.sdpr.persist_sdp_results_in_mongo(ts)
  
    def get_subscriber_detail(self, msisdn):
        "{u'languageIDCurrent': 1.0, u'ussdEndOfCallNotificationID': 0.0, u'_id': u'27431001002', u'serviceClass': 7.0, u'serviceOfferCurrent': u'0000000000000000000000000000000'}"
        return self.mongo_air_sdp_msisdns.find_one({ "_id" : '{}'.format(msisdn)})
    
    @withRequest
    @timeit
    def xmlrpc_GetAccountDetails(self, request, xml):
        print 'GetAccountDetails', xml
        # xm = {'originTransactionID': '1432215692722', 'originHostName': 'nodename112', 'subscriberNumber': '27222555772', 
        # 'subscriberNumberNAI': 2, 'originTimeStamp': <DateTime '20150521T13:41:32+0000' at 7fc9db769ef0>, 'originNodeType': 'EXT'}

        self.read_req(request, xml)
        r = self.get_account_details(xml)
        
        p = r.copy()
        p['action'] = 'GetAccountDetails'
        p['test_date'] = datetime.datetime.now()

        log.msg("Adding msisdn to mongo {}".format(xml['subscriberNumber']))
        log.msg('Msisdn details. {}'.format({ "_id" : xml['subscriberNumber'], 'serviceClass': r['serviceClassCurrent'], \
                                                 'languageIDCurrent':r['languageIDCurrent'] , 'ussdEndOfCallNotificationID' : r['ussdEndOfCallNotificationID'],
                                                  'serviceOfferCurrent' : self.serviceOffers}))

        if not self.mongo_air_sdp_msisdns.find_one({ "_id" : xml['subscriberNumber']}):    
            self.mongo_air_sdp_msisdns.save({ "_id" : xml['subscriberNumber'], 'serviceClass': r['serviceClassCurrent'], \
                                            'languageIDCurrent':r['languageIDCurrent'] , 'ussdEndOfCallNotificationID' : r['ussdEndOfCallNotificationID'],
                                            'serviceOfferCurrent' : self.serviceOffers, 'main_account_balance' : '10000', "demo server" : False}, True)
        
        # logs junk. 
        self.sdpr.persist_sdp_results_in_mongo(p)
        
        return r

    @withRequest
    @timeit
    def xmlrpc_GetBalanceAndDate(self, request, xml):
        self.read_req(request, xml)
        if not self.mongo_air_sdp_msisdns.find_one({ "_id" : xml['subscriberNumber']}):
            r = self.get_account_details(xml)
            # new numbers get 10000 value
            self.mongo_air_sdp_msisdns.save({ "_id" : xml['subscriberNumber'], 'serviceClass': r['serviceClassCurrent'], \
                                         'languageIDCurrent':r['languageIDCurrent'] , 'ussdEndOfCallNotificationID' : r['ussdEndOfCallNotificationID'],
                                         'serviceOfferCurrent' : self.serviceOffers, 'main_account_balance' : '10000', "demo server" : False}, True)

        r = self.get_balance_and_date_response(xml)
        p = r.copy()
        p['action'] = 'GetBalanceAndDate'
        p['test_date'] = datetime.datetime.now()
        self.sdpr.persist_sdp_results_in_mongo(p)

        return r

    @withRequest
    @timeit
    def xmlrpc_UpdateUsageThresholdsAndCounters(self, request, xml):
        self.read_req(request, xml)
        r = self.update_usage_thresholds_and_counters(xml)
        p = r.copy()
        p['action'] = 'UpdateUsageThresholdsAndCounters'
        p['test_date'] = datetime.datetime.now()
        self.sdpr.persist_sdp_results_in_mongo(p)
        return r

    @withRequest
    @timeit
    def xmlrpc_GetUsageThresholdsAndCounters(self, request, xml):
        self.read_req(request, xml)
        r = self.get_usage_threshold_counters(xml)
        p = r.copy()
        p['action'] = 'GetUsageThresholdsAndCounters'
        p['test_date'] = datetime.datetime.now()
        self.sdpr.persist_sdp_results_in_mongo(p)
        return r

    @withRequest
    @timeit
    def xmlrpc_GetOffers(self, request, xml):
        self.read_req(request, xml)
        r = self.get_offers_response(xml)
        p = r.copy()
        p['action'] = 'GetOffers'
        p['test_date'] = datetime.datetime.now()
        self.sdpr.persist_sdp_results_in_mongo(p)
        return r

    @withRequest
    @timeit
    def xmlrpc_UpdateOffer(self, request, xml):
        self.read_req(request, xml)
        return self.update_offer(xml)

    @withRequest
    @timeit
    def xmlrpc_DeleteOffer(self, request, xml):
        self.read_req(request, xml)
        return self.delete_offer(xml)

    @withRequest
    @timeit
    def xmlrpc_UpdateSubscriberSegmentation(self, request, xml):
        self.read_req(request, xml)
        r = self.update_subscriber_segmentation(xml)
        p = r.copy()
        p['action'] = 'UpdateSubscriberSegmentation'
        p['test_date'] = datetime.datetime.now()
        
        s = self.update_serviceOfferings(xml)

        print 'UpdateSubscriberSegmentation(serviceOffers), updated to {}'.format(s)
        d = self.mongo_air_sdp_msisdns.find_one({ "_id" : xml['subscriberNumber']})
        p['serviceOfferCurrent'] = s
        d['serviceOfferCurrent'] = s

        self.mongo_air_sdp_msisdns.update({ "_id" : xml['subscriberNumber']}, d)
        # log
        self.sdpr.persist_sdp_results_in_mongo(p)

        return r
        
    @withRequest
    @timeit
    def xmlrpc_UpdateAccountDetails(self, request, xml):
        self.read_req(request, xml)
        r = self.update_account_details(xml)
        log.msg('UpdateAccountDetails response {}'.format(r))
        p = r.copy()
        p['action'] = 'UpdateAccountDetails'
        p['test_date'] = datetime.datetime.now()

        d = self.mongo_air_sdp_msisdns.find_one({ "_id" : xml['subscriberNumber']})
        if 'ussdEndOfCallNotificationID' in xml:
            d['ussdEndOfCallNotificationID'] = xml['ussdEndOfCallNotificationID']
            log.msg('SOCN changed to {}'.format(xml['ussdEndOfCallNotificationID']))
        if 'languageIDNew' in xml:
            d['languageIDNew'] = xml['languageIDNew']
            log.msg('OCS language changed to {}'.format(xml['subscriberNumber']))
        self.mongo_air_sdp_msisdns.update({ "_id" : xml['subscriberNumber']}, d)

        self.sdpr.persist_sdp_results_in_mongo(p)

        return r

    @withRequest
    @timeit
    def xmlrpc_UpdateServiceClass(self, request, xml):
        self.read_req(request, xml)
        r = self.update_std_resp(xml)
        # update the msisdn on mongo
        """xml = {'originTransactionID': '1432210157716', 'originHostName': 'nodename112', 'serviceClassNew': 20, 'subscriberNumber': '27222555772', 
        'subscriberNumberNAI': 2, 'originTimeStamp': '20150521T12:09:17+0000', 'originNodeType': 'EXT', 'test_date': datetime.datetime(2015, 5, 21, 14, 9, 17, 121265), 
        'serviceClassAction': 'SetOriginal', 'action': 'request_rec'}
        """
        d = self.mongo_air_sdp_msisdns.find_one({ "_id" : xml['subscriberNumber']})
        d['serviceClass'] = int(xml['serviceClassNew'])
        self.mongo_air_sdp_msisdns.update({ "_id" : xml['subscriberNumber']}, d)

        print 'UpdateServiceClass', r , xml
        p = r.copy()
        p['action'] = 'UpdateServiceClass'
        p['test_date'] = datetime.datetime.now()
        self.sdpr.persist_sdp_results_in_mongo(p)
        return r
     
    @withRequest
    @timeit
    def xmlrpc_UpdateBalanceAndDate(self, request, xml):
        self.read_req(request, xml)

        response = {}
        responseCode = 0
        response['originTransactionID'] = xml['originTransactionID']
        
        d = self.mongo_air_sdp_msisdns.find_one({ "_id" : xml['subscriberNumber']})
        """ {u'info': [{u'dedicatedAccountValue1': u'0', u'dedicatedAccountUnitType': 6, u'dedicatedAccountID': 1, u'subDedicatedAccountInformation': []},"""

        if d == None:
            response['responseCode'] = 102  # subscriber not found
            return response        

        # DA2 for cash
        # DA10 for stretch data
        set9 = False
        
        if 'dedicatedAccountUpdateInformation' in xml:
            'use need dedicated account data'

            adjustmentAmount = 0
            dedicatedAccountUnitType = ""
            
            for i in xml["dedicatedAccountUpdateInformation"]:
                """ {'dedicatedAccountUnitType': 6, 'dedicatedAccountID': 2, 'adjustmentAmountRelative': '-0'}
                    {'dedicatedAccountUnitType': 6, 'dedicatedAccountValueNew': '20000', 'dedicatedAccountID': 3, 'expiryDate': <DateTime '20170601T12:00:00+0000' at 7fe60db01200>}
                    """
                posi = i["dedicatedAccountID"]
                posi -= 1
                da_before = int(d["info"][posi]["dedicatedAccountValue1"])
                da_after = da_before
                
                if "adjustmentAmountRelative" in i:
                    x = int(i["adjustmentAmountRelative"])
                    da_after += x
                    adjustmentAmount = x
                    dedicatedAccountUnitType = i["dedicatedAccountUnitType"]
                if "dedicatedAccountValueNew" in i:
                    x = i["dedicatedAccountValueNew"]
                    da_after = x
                    adjustmentAmount = x
                    dedicatedAccountUnitType = i["dedicatedAccountUnitType"]

                if "expiryDate" in i:
                    ed = dateutil.parser.parse(str(i['expiryDate']))
                    d['info'][posi]['expiryDate' ] = ed
                    print 'expiryDate', i["expiryDate"], ed

                # quick bal update
                d['info'][posi]['dedicatedAccountValue1' ] = str(da_after)
                
                self.mongo_air_sdp_msisdns.update({ "_id" : xml['subscriberNumber']}, d)

                if i["dedicatedAccountID"] == 1:
                    log.msg('Purchace !! Balance Change DA1')

                elif i["dedicatedAccountID"] == 9:
                    set9 = True

                elif i["dedicatedAccountID"] == 10:
                    if set9 == True:
                        if random.randint(0, 10) % 2 == 0:
                            # Break
                            response['responseCode'] = 100
                            responseCode = 100
                            print "Break to test first stretch fail"
                            self.mongo_air_sdp_msisdns.update({ "_id" : xml['subscriberNumber']}, d)
                            print self.pp.pprint(response)
                            return response
                        else:
                            print "Break to test first stretch fail -Skipped"
                            
                log.msg("UpdateBalanceAndDate : adjustmentAmount : {0},dedicatedAccountUnitType: {1},DA Balance before {2} , balance after {3}"\
                         .format(adjustmentAmount, dedicatedAccountUnitType, da_before, da_after))
                log.msg('DA Info {}'.format(i))
                 
            # Possible codes.
            # 0, 100, 102, 104, 105, 106, 121, 122, 123, 124, 126, 136, 139, 153, 163, 164,167, 204, 212, 226, 227, 230, 247, 249, 257, 260, 999
            if da_after < 0:  # insuff funds 
                d['info'][1]['dedicatedAccountValue1'] = '{}'.format(0)
                # TODO
                response['responseCode'] = 124  # Below minimum balance
            else :                
#                 d['main_account_balance'] = '{}'.format(da_after)
                response['responseCode'] = 0  # Successful

        # Main account
        if 'adjustmentAmountRelative' in xml and responseCode != 100: 

            bal_before = int(d['main_account_balance'])
            bal_after = int(d['main_account_balance'])
            ar = int(xml['adjustmentAmountRelative'])
            bal_after += ar
            log.msg ("UpdateBalanceAndDate MA  : MA Balance before {} , balance after {} , adjustmentAmountRelative {}".format(bal_before, bal_after, ar))
            
            # Possible codes.
            # 0, 100, 102, 104, 105, 106, 121, 122, 123, 124, 126, 136, 139, 153, 163, 164,167, 204, 212, 226, 227, 230, 247, 249, 257, 260, 999
            if bal_after < 0:  # insuff funds
#                 d['main_account_balance'] = '{}'.format(0)
                response['responseCode'] = 124  # Below minimum balance
            else :
                d['main_account_balance'] = '{}'.format(bal_after)
                response['responseCode'] = 0  # Successful

        self.mongo_air_sdp_msisdns.update({ "_id" : xml['subscriberNumber']}, d)

        print self.pp.pprint(response)
        return response


class MyResource(Resource):
    pass


if __name__ == '__main__':

    # rotate every 1 Meg
    log.startLogging(sys.stdout)
    persist_config_mongo()
    f = logfile.LogFile("ocs.log", "/tmp", rotateLength=10000000)    
    log.startLogging(f)

    root = MyResource()
    root.putChild("form", FormPage())  
    root.putChild("Air", AirSdpServer())
    root.putChild("", AirSdpServer())
     
    factory = Site(root)
     
    reactor.listenTCP(10010, factory, backlog=50)  #  @UndefinedVariable
    reactor.run()  #  @UndefinedVariable
    
#     from twisted.internet import reactor
#     r = AirSdpServer(return_failures=5)
#     reactor.listenTCP(10010, server.Site(r))  # @UndefinedVariable
#     print 'run'
#     reactor.run() #  @UndefinedVariable

