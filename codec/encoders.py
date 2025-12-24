import pickle
import json

def encode_simple_utf(payload):
    return payload.encode('utf-8')

def encode_pickle(payload):
    return pickle.dumps(payload)

def encode_format_json_ipv4_address(payload):
    packet = json.dumps({ 
                    "address": {
                        "ip": payload[0],
                        "port": payload[1]
                    }
                }
            )
    return packet.encode('utf-8')

def encode_format_json_p2p_request(payload):
    packet = json.dumps({
                "request_form": {
                    "target_name": payload[0],
                    "response": payload[1]
                },
                "from_address":{
                    "ip": payload[2],
                    "port": payload[3]
                }
            }
        )
    return packet.encode('utf-8')

# New method to send request to include the p2p session socket info
def encode_p2p_request(payload):
    packet = json.dumps({
        "recipient_name": payload[0],
        "from_address":
        {
            "ip": payload[1],
            "port": payload[2]
        }
    })
    return packet.encode('utf-8')