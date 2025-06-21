#!/bin/bash

# Script to set up and run Mudhumeni AI

# Print colored messages
print_green() {
    echo -e "\e[32m$1\e[0m"
}

print_yellow() {
    echo -e "\e[33m$1\e[0m"
}

print_red() {
    echo -e "\e[31m$1\e[0m"
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_red "Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$python_version < 3.9" | bc -l) )); then
    print_red "Python version should be 3.9 or higher. Current version: $python_version"
    exit 1
fi

print_green "Python version $python_version detected."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_yellow "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_yellow "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_yellow "Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_yellow "Creating .env file..."
    echo "GROQ_API_KEY=your_groq_api_key_here" > .env
    echo "MONGODB_URI=mongodb://localhost:27017/mudhumeni_db" >> .env
    echo "FLASK_SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(16))')" >> .env
    print_yellow ".env file created. Please edit it with your actual API keys."
fi

# Ask if user wants to train the model
read -p "Do you want to train the model? (y/n): " train_model
if [[ $train_model == "y" ]]; then
    print_yellow "Training model..."
    python train_model.py
fi

# Ask if user wants to run the application
read -p "Do you want to run the application? (y/n): " run_app
if [[ $run_app == "y" ]]; then
    print_green "Running Mudhumeni AI..."
    python app.py
else
    print_green "Setup complete. Run 'python app.py' to start the application."
fi