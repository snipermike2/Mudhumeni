# ussd/__init__.py
from flask import Blueprint

# Create the blueprint
ussd_blueprint = Blueprint('ussd', __name__)

# Import routes after blueprint is defined to avoid circular imports
from ussd.routes import *

def register_ussd_blueprint(app):
    """Register the USSD blueprint with the app"""
    app.register_blueprint(ussd_blueprint, url_prefix='/ussd')
    return ussd_blueprint

# This function will be used to handle USSD requests
def handle_request():
    """Handle USSD requests"""
    from ussd.routes import ussd_handler
    return ussd_handler()