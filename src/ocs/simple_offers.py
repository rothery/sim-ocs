from SimpleXMLRPCServer import SimpleXMLRPCServer
import xmlrpclib


def air():
    with open("./simple_offers.txt", "rb") as handle:
        return xmlrpclib.Binary(handle.read())

server = SimpleXMLRPCServer(("localhost", 10011))
print "Listening on port 10011..."
server.register_function(air, 'Air')

server.serve_forever()