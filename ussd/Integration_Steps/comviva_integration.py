# comviva_integration.py
from flask import request, jsonify
import requests
from ussd import ussd_blueprint, handle_request

def comviva_handler():
    """Handle USSD requests from Comviva"""
    # Get the POST data
    data = request.get_json()
    
    session_id = data.get('session_id', '')
    service_code = data.get('ussd_code', '')
    phone_number = data.get('msisdn', '')
    text = data.get('user_input', '')
    
    # Forward the request to our USSD handler
    forwarded_data = {
        'sessionId': session_id,
        'serviceCode': service_code,
        'phoneNumber': phone_number,
        'text': text
    }
    
    response = requests.post('http://your_server/ussd', data=forwarded_data)
    
    # Format the response for Comviva
    is_continue = response.text.startswith('CON')
    
    return jsonify({
        'message': response.text.replace('CON ', '').replace('END ', ''),
        'session_state': 'CONTINUE' if is_continue else 'END'
    })