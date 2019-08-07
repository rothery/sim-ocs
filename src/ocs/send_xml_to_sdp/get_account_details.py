import datetime
import logging
import random
from xmlrpclib import ServerProxy, Transport, Error, Fault, ProtocolError

from operations.connections.mongo.connection import MongoConnection


dt = datetime.datetime.now()
dt_now = dt
delta = datetime.timedelta(minutes=20)        
d = (dt + delta) 
print d
dt_20min = d.isoformat().split(".")[0] + "+0100"
print (dt_20min)
dt_20min = d

class SpecialTransport(Transport):
    # Override
    def single_request(self, host, handler, request_body, verbose=0):
        # issue XML-RPC request

        h = self.make_connection(host)
        if verbose:
            h.set_debuglevel(1)

        try:
            self.send_request(h, handler, request_body)
            self.send_host(h, host)
            print 'skipping', h
#             self.send_user_agent(h)
            self.send_content(h, request_body)

            response = h.getresponse(buffering=True)
            if response.status == 200:
                self.verbose = verbose
                return self.parse_response(response)
        except Fault:
            raise
        except Exception:
            # All unexpected errors leave connection in
            # a strange state, so we clear it.
            self.close()
            raise

        # discard any response data and raise exception
        if (response.getheader("content-length", 0)):
            response.read()
        raise ProtocolError(
            host + handler,
            response.status, response.reason,
            response.msg,
            )



    def send_content(self, connection, request_body):

        print "Add your headers here!"
        print dir(connection), request_body
        connection.putheader('User-Agent', 'DTS/5.0/4.2')
        connection.putheader("Content-Type", "text/xml")
#         , 'Content-Type': 'text/xml;charset=utf-8',\
        connection.putheader("Content-Length", str(len(request_body)))
        connection.putheader('Accept', 'application/xml')
#         connection.addheaders('Authorization', 'Basic %s' % base64.encodestring('%s:%s' % login_details)[:-1])

        connection.endheaders()
        if request_body:
            connection.send(request_body)

class AccountDetails(object):
    def __init__(self, *args, **kwargs):
        object.__init__(self, *args, **kwargs)
        self.trans_id = random.randint(10000, 99999)
        
        
        
    def get_acc_details(self, host, port=10010, dap_login_details=('user', 'user')):
        'Offers get, update and delete'
    
        client = ServerProxy("http://user:user@%s:%s/Air" % (host, port), transport=SpecialTransport())
        try:
            send = {'subscriberNumberNAI' : 2L,
					'originNodeType' : 'EXT',
					'originTransactionID' : str(self.trans_id),
					'subscriberNumber' : '12345',
					'originTimeStamp' : dt_now,
					'originHostName' : 'DTSCC'
                    }
#             print('this', client.GetAccountDetails(send))
        
    
        except Error, v:
            print "ERROR", v
        
        except Exception as e:
            logging.error('Exception raised opening a POST : {0}'.format(e))
            response = e
    
        return client
        
        
if __name__ == '__main__':
    ad = AccountDetails()
    #     print sdpoffer.do_offer('10.64.8.40', 'update')
    # 	print ad.get_acc_details('172.28.200.102')/
    mongo = MongoConnection('localhost' , 27017, mongo_database='staf')
    
    print mongo.remove('subscriber_details', {'subscriberNumber' : '12345'})
    print ad.get_acc_details('localhost')
    print mongo.insert_db('subscriber_details', {'subscriberNumber' : '12345'})
    print ad.get_acc_details('localhost')
