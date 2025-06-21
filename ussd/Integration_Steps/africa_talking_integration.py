# africa_talking_integration.py
import africastalking
from flask import Blueprint, request

# Create a blueprint for Africa's Talking integration
at_blueprint = Blueprint('africas_talking', __name__)

# Initialize Africa's Talking with your credentials
def initialize_africastalking():
    username = "sandbox"  # Replace with your Africa's Talking username
    api_key = "atsk_00b2653df104fa46386758f5cec0721451b6858eb85a9eb169691ac9c415d9befef6527e"    # Replace with your Africa's Talking API key
    
    africastalking.initialize(username, api_key)
    return africastalking.USSD

# Handler for USSD requests from Africa's Talking
@at_blueprint.route('/', methods=['POST'])
def africas_talking_handler():
    # Get the POST data
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "")
    
    # Process the USSD request using your existing USSD handler
    from ussd import handle_request
    
    # Create a mock request object with the necessary data
    class MockRequest:
        def __init__(self, form_data):
            self.form = form_data
    
    # Create the form data
    form_data = {
        'sessionId': session_id,
        'serviceCode': service_code,
        'phoneNumber': phone_number,
        'text': text
    }
    
    # Pass the data to your USSD handler
    request._current_form_data = form_data
    response = handle_request()
    
    # Return the response to Africa's Talking
    return response

# Register the blueprint with the app
def register_africas_talking_blueprint(app):
    app.register_blueprint(at_blueprint, url_prefix='/ussd')
    return at_blueprint