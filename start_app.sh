#!/bin/bash

# Activate the virtual environment
source ./bin/activate

# Set environment variables (you might want to move these to a .env file)
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Run the Flask application
python app.py