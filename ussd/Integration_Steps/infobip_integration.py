# infobip_integration.py
from flask import request, jsonify

def infobip_handler():
    """Handle USSD requests from Infobip"""
    # Get the POST data
    data = request.get_json()
    
    session_id = data.get('session_id', '')
    service_code = data.get('service_code', '')
    phone_number = data.get('msisdn', '')
    text = data.get('input', '')
    
    # Forward the request to our USSD handler
    forwarded_data = {
        'sessionId': session_id,
        'serviceCode': service_code,
        'phoneNumber': phone_number,
        'text': text
    }
    
    response = requests.post('http://your_server/ussd', data=forwarded_data)
    
    # Format the response for Infobip
    return jsonify({
        'response': response.text.replace('CON ', ''),
        'action': 'continue' if response.text.startswith('CON') else 'end'
    })