import datetime
import random
import xml
import xmlrpclib

from operations.sas.get_ussd_req import post_ussd_xmlrpc, ussd_format_time
from operations.sas.read_sas_resp import ReadSASResponse


dt = datetime.datetime.now()
dt_now = dt

# proxy = xmlrpclib.ServerProxy("http://172.28.200.102:10010/")
proxy = xmlrpclib.ServerProxy("http://localhost:10010/")

p = {   'originHostName' : 'STAF_TEST',
        'originNodeType' : 'EXT',
        'originTransactionID' : '12341234',
        'originTimeStamp' : dt_now,
        'subscriberNumber' : '071123100456',
        'subscriberNumberNAI' : 2L
    }

print "Send GetAccountDetails" , p
x = proxy.GetAccountDetails(p)
for k,v in x.iteritems(): 
    print "{}={}".format(k,v)

# p = {  <?xml version="1.0" ?>
#                         <name>subscriberNumberNAI</name>
#                         <value>
#                             <i4>2</i4>
# 
#                         <name>originNodeType</name>
#                         <value>
#                             <string>EXT</string>
# 
#                         <name>ussdEndOfCallNotificationID</name>
#                         <value>
#                             <i4>1</i4>
# 
#                         <name>subscriberNumber</name>
#                         <value>
#                             <string>27123456789</string>
#                         </value>
#                     </member>
#                     <member>
#                         <name>originTransactionID</name>
#                         <value>
#                             <string>1440158361869</string>
#                         </value>
#                     </member>
#                     <member>
#                         <name>originTimeStamp</name>
#                         <value>
#                             <dateTime.iso8601>20150821T13:59:21+0200</dateTime.iso8601>
#                         </value>
#                     </member>
#                     <member>
#                         <name>originHostName</name>
#                         <value>
#                             <string>dts</string>
#                         </value>
#                     </member>
#                 </struct>
#             </value>
#         </param>
#     </params>
# </methodCall>
# 
#     }
 
#Used for start and end of call notification. 
print "Send UpdateAccountDetails" , p
x = proxy.UpdateAccountDetails(p)
for k,v in x.iteritems(): 
    print "{}={}".format(k,v)

