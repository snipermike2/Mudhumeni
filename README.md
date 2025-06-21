# Mudhumeni AI - Southern African Farming Assistant

An AI-powered farming guide specifically designed for farmers in Southern Africa.
# Mudhumeni AI - Southern African Farming Assistant

Mudhumeni AI is an intelligent farming assistant designed specifically for farmers in Southern Africa. It provides region-specific agricultural advice through multiple channels including a web interface, USSD, and SMS notifications.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Technical Architecture](#technical-architecture)
4. [Setup Instructions](#setup-instructions)
5. [USSD Integration Guide](#ussd-integration-guide)
6. [SMS Notification System](#sms-notification-system)
7. [Testing](#testing)
8. [Presenting the Project](#presenting-the-project)
9. [Troubleshooting](#troubleshooting)
10. [Dependencies](#dependencies)

## Project Overview

Mudhumeni AI leverages artificial intelligence to provide context-aware farming advice tailored to the unique environmental conditions of Southern Africa. The system offers:

- Personalized crop recommendations based on soil conditions
- Season-specific farming advice
- Pest control guidance
- Weather-related recommendations
- Market information

The most innovative aspect of our platform is its multi-channel approach, allowing farmers to access advice via:

- Web interface (for smartphone users)
- USSD service (for feature phone users)
- SMS notifications (proactive alerts)

This ensures that even farmers with basic feature phones in remote areas can access valuable agricultural knowledge.

## Features

### Core Features

- **AI-Powered Advice**: Uses LLaMA 3.3 via Groq API to generate relevant farming guidance
- **Seasonal Awareness**: Provides different advice based on the current farming season
- **Location-Based Recommendations**: Customizes guidance based on the user's province/region
- **Crop Recommendation Engine**: Suggests optimal crops based on soil parameters
- **Multilingual Support**: Available in multiple Southern African languages

### USSD Features

- Simple menu navigation
- Season-specific farming information
- Crop recommendations
- Farming advice on various topics
- User preference storage
- SMS notifications for critical alerts

## Technical Architecture

The system is built on a Flask web application with the following components:

- **Frontend**: HTML/CSS/JavaScript for web interface
- **Backend**: Python Flask application
- **AI Engine**: LLaMA 3.3 (accessed via Groq API)
- **Database**: MongoDB for data storage
- **USSD Interface**: Custom module for feature phone access
- **SMS System**: Proactive notification component

## Setup Instructions

### Prerequisites

- Python 3.9+
- MongoDB
- Groq API key
- USSD gateway account (Africa's Talking, Infobip, or Comviva)
- SMS gateway account (optional)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Mudhumeni_AI.git
   cd Mudhumeni_AI
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with required configuration:
   ```
   FLASK_SECRET_KEY=your_secret_key
   GROQ_API_KEY=your_groq_api_key
   MONGODB_URI=mongodb://localhost:27017/
   SMS_API_KEY=your_sms_api_key  # Optional
   SMS_SENDER_ID=Mudhumeni  # Optional
   ```

4. Initialize the database:
   ```bash
   python init_db.py
   ```

5. Start the application:
   ```bash
   python app.py
   ```

## USSD Integration Guide

### USSD Architecture

The USSD interface is organized as follows:

- `ussd/__init__.py` - Package initialization and blueprint registration
- `ussd/routes.py` - Main request handlers for USSD
- `ussd/session.py` - Session management for USSD users
- `ussd/Integration Steps/` - Provider-specific integration files

### Setting Up USSD

1. Ensure you have created the required directory structure:
   ```
   ussd/
   ├── __init__.py
   ├── routes.py
   ├── session.py
   └── Integration Steps/
       ├── africa_talking_integration.py
       ├── comviva_integration.py
       └── infobip_integration.py
   ```

2. Make sure `__init__.py` contains the blueprint setup:
   ```python
   from flask import Blueprint

   ussd_blueprint = Blueprint('ussd', __name__)

   from ussd.routes import *

   def register_ussd_blueprint(app):
       app.register_blueprint(ussd_blueprint, url_prefix='/ussd')
       return ussd_blueprint

   def handle_request():
       from ussd.routes import ussd_handler
       return ussd_handler()
   ```

3. Update gateway integration files to include proper imports:
   ```python
   # For all integration files (africa_talking_integration.py, etc.)
   import requests
   from flask import request, jsonify
   from ussd import handle_request
   ```

### Connecting to USSD Providers

Depending on your region, you'll need to register with one of these USSD providers:

#### Africa's Talking

1. Register at [Africa's Talking](https://africastalking.com/)
2. Create a new service and get your API keys
3. Configure the callback URL to your server: `https://your-server.com/ussd`
4. Use the `africa_talking_integration.py` file to handle requests

#### Infobip

1. Register at [Infobip](https://www.infobip.com/)
2. Set up USSD service and get credentials
3. Configure the callback URL
4. Use the `infobip_integration.py` file to handle requests

#### Comviva

1. Contact local Comviva representative
2. Complete their integration process
3. Set up the callback URL
4. Use the `comviva_integration.py` file to handle requests

### Testing USSD Locally

Before presenting or deploying, test your USSD service locally:

1. Start your Flask application:
   ```bash
   python app.py
   ```

2. Run the USSD simulator:
   ```bash
   python ussd/ussd_simulator.py
   ```

3. Follow the prompts in the simulator to navigate through the USSD menus

## SMS Notification System

The SMS system proactively sends important farming alerts:

- Weather forecasts
- Planting reminders
- Pest alerts
- Market price updates
- Seasonal transition notifications

### SMS Setup

1. Configure your SMS gateway credentials in the `.env` file
2. Start the notification system automatically with the app, or manually:
   ```python
   from sms_notifications import register_sms_notification_system
   register_sms_notification_system(app)
   ```

### Testing SMS

Test SMS notifications using the mock mode:

1. Omit the SMS_API_KEY from your environment to use mock mode
2. Check console output for mock SMS messages
3. For actual SMS testing, add your API key and run:
   ```python
   # Interactive testing
   from sms_notifications import FarmingSMSNotification
   sms = FarmingSMSNotification()
   sms.send_sms("+27123456789", "Test message from Mudhumeni AI")
   ```

## Testing

### Unit Testing

Run the unit tests to verify basic functionality:

```bash
python -m unittest discover tests
```

### Integration Testing

Test the integrated system components:

```bash
python -m unittest discover integration_tests
```

### USSD Testing

Test the USSD interface using the simulator:

```bash
python ussd/ussd_simulator.py
```

## Presenting the Project

When presenting Mudhumeni AI, follow these steps:

1. **Start the Application**:
   ```bash
   python app.py
   ```

2. **Demonstrate the Web Interface**:
   - Open `http://localhost:5000` in a browser
   - Show the chat interface
   - Demonstrate crop recommendations
   - Show the analytics dashboard

3. **Demonstrate USSD**:
   - Run the simulator in another terminal:
     ```bash
     python ussd/ussd_simulator.py
     ```
   - Walk through the different menu options
   - Show how farmers can get advice via USSD

4. **Show SMS Notifications**:
   - Demonstrate how alerts are sent
   - Explain the types of notifications

5. **Highlight Key Points**:
   - Multiple channels for different user types
   - Localized advice for Southern Africa
   - Season-specific recommendations
   - Integration with ML for crop recommendations

## Troubleshooting

### Common Issues

1. **Module Not Found Errors**:
   - Ensure all dependencies are installed
   - Check import paths and directory structure

2. **USSD Not Working**:
   - Verify that the ussd directory has the correct structure
   - Check that `__init__.py` exists and is properly configured
   - Ensure the routes are registered correctly

3. **MongoDB Connection Issues**:
   - Verify MongoDB is running
   - Check connection string in `.env`
   - Ensure proper network access

4. **API Key Issues**:
   - Verify Groq API key is valid
   - Check for API rate limits or quota issues

### Debug Mode

Run the app in debug mode for detailed logs:

```bash
export FLASK_DEBUG=1
python app.py
```

## Dependencies

The project requires the following main dependencies:

- Flask
- pymongo
- langchain
- langchain-groq
- requests
- numpy
- pandas
- scikit-learn
- python-dotenv
- flask-talisman
- flask-limiter
- schedule (for SMS notifications)

See `requirements.txt` for the complete list.

---

For more information or support, contact the development team.