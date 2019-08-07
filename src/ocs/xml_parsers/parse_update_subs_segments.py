import xmltodict, json


def convert_UpdateSubscriberSegmentation(s_xml):
    
    def xml_type_convert(od):
        i = od.items()[0]
        if i[0] == 'i4':
            return int(i[1]) 
        elif i[0] == 'boolean':
            return bool(int(i[1]))
    

    def serv_offerings(v):
        s = ''
        for i in v['array']['data']['value']:
            print i
            for j in i:
                l = i[j]['member']
                print 'me', xml_type_convert(l[0]['value']),xml_type_convert(l[1]['value'])

                s += l[1]['value'].items()[0][1]
        return s
    print 'this',type(s_xml)
    o = xmltodict.parse(s_xml)
    print o
    for i in o['methodCall']['params']['param']['value']['struct']['member']:
        if i['name'] == 'serviceOfferings':
            return serv_offerings(i['value'])
        
# print convert_UpdateSubscriberSegmentation1('UpdateSubscriberSegmentation.xml')

def convert_UpdateSubscriberSegmentation_dict(dic):
    for i in dict(dic):
        print i

if __name__ == '__main__':
    print convert_UpdateSubscriberSegmentation(open('UpdateSubscriberSegmentation.xml').read())



