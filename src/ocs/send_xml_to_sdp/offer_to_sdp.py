import datetime
import dateutil.tz
import logging
import random
import time
from xmlrpclib import ServerProxy, Transport, Error, Fault, ProtocolError


dt = datetime.datetime.now()
dt_now = dt
delta = datetime.timedelta(minutes=20)		
d = (dt + delta) 
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
# 			self.send_user_agent(h)
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

	def _strftime(self, value):
		if datetime:
			if isinstance(value, datetime.datetime):
				return "%04d%02d%02dT%02d:%02d:%02d+0200" % (
 	                value.year, value.month, value.day,
 	                value.hour, value.minute, value.second)
	



	def send_content(self, connection, request_body):

# 		print dir(connection), request_body
		connection.putheader('User-Agent', 'DTS/5.0/4.2')
		connection.putheader("Content-Type", "text/xml")
# 		, 'Content-Type': 'text/xml;charset=utf-8',\
		connection.putheader("Content-Length", str(len(request_body)))
		connection.putheader('Accept', 'application/xml')
# 		connection.addheaders('Authorization', 'Basic %s' % base64.encodestring('%s:%s' % login_details)[:-1])

		connection.endheaders()
		if request_body:
			connection.send(request_body)

class SDPOffer(object):
	def __init__(self, *args, **kwargs):
		object.__init__(self, *args, **kwargs)
		self.trans_id = random.randint(10000, 99999)
		
				
	def do_offer(self, host, otype , port=10010, dap_login_details=('user', 'user')):
		'Offers get, update and delete'
	
		client = ServerProxy("http://user:user@%s:%s/Air" % (host, port), transport=SpecialTransport())
		try:
			if otype == 'get':
				offer = { 'offerID' : 10L,
						'offerType' : 2L,
						'expiryDateTime' :dt_20min,
						'originHostName' : 'DTSSVR1',
						'originNodeType' : 'EXT',
				 		'originTimeStamp' : dt_now,
				  		'originTransactionID' : str(self.trans_id),
					  	'subscriberNumber' : '47112288',
					  	'subscriberNumberNAI' : 2L}
 				print 'offer', offer
				print(client.GetOffers(offer))
		
			elif otype == 'update':	
				offer = { 'offerID' : 10L ,
						'offerType' : 2L,
						'originHostName' : 'DTSSVR1',
						'originNodeType' : 'EXT',
				 		'originTimeStamp' : dt_now,
				 		'startDateTime' : dt_now,
				 		'expiryDateTime' : dt_20min.replace(tzinfo=dateutil.tz.gettz('SAST')) ,
				  		'originTransactionID' : str(self.trans_id),
					  	'subscriberNumber' : '47112288',
					  	'originOperatorID' : '11',
					  	'subscriberNumberNAI' : 2L}
				print 'offer', offer
				print(client.UpdateOffer(offer))
		
			elif otype == 'delete':
				
				offer = {'originNodeType' : 'EXT',
						'originHostName' : 'DTSSVR1',
				  		'originTransactionID' : str(self.trans_id),
				 		'originTimeStamp' : dt_now,
					  	'subscriberNumberNAIstruct' : 2L,
						'subscriberNumber' : '47112288',
	 					'offerID' : 10L ,
	 					'productID' : 1L }
		
				print offer
				print(client.DeleteOffer(offer))
	
		
		except Exception as e:
			logging.error('Exception raised opening a POST : {0}'.format(e))
			response = e
	
		return client

		
if __name__ == '__main__':
	
	sdpoffer = SDPOffer()

	print sdpoffer.do_offer('localhost', 'update')
	
# 	print sdpoffer.do_offer('172.28.200.102', 'update')
# 	print sdpoffer.do_offer('172.28.200.102', 'update')
# 	time.sleep(1)
# 	print sdpoffer.do_offer('172.28.200.102', 'get')
# 	time.sleep(1)
# 	sdpoffer.do_offer('172.28.200.102', 'delete')
	
