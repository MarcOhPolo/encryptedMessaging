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

def decode_format_json_ipv4_address(payload):
    
    address = payload['address']
    return (address['ip'],address['port'])