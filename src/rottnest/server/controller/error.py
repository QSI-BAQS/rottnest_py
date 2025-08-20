import json

def err(message, *args, **kwargs):
    return json.dumps({
        'message': 'err',
        'desc': f"Error: {message['message']} not recognised"
    })
