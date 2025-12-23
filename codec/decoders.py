import pickle 
import json

def decode_simple_utf(payload):
    return payload.decode('utf-8')


def decode_pickle_numbered_list(payload):
    def numbered(values):
        return "\n".join(f"{i}. {value}"for i, value in enumerate(values, start=1)) + "\n"
    list = pickle.loads(payload)
    return {
        "formatted": numbered(list.values()),
        "values": list
    }

def decode_format_json_ipv4_address(packet):
    payload = json.loads(packet)
    address = payload['address']
    return (address['ip'],address['port'])

def decode_format_json_p2p(packet):
    payload = json.loads(packet)
    request_form = payload['request_form']
    return request_form

def decode_p2p_request(packet):
    payload = json.loads(packet)
    recipient_name = payload["recipient_name"]
    p2p_source = payload["from_address"]
    return (recipient_name,p2p_source)