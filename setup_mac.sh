#!/bin/bash

# Create and activate virtual environment
python3 -m venv .
source ./bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Setup MongoDB (if not already installed)
echo "To install MongoDB on Mac:"
echo "1. Install Homebrew if not already installed:"
echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
echo "2. Install MongoDB:"
echo "   brew tap mongodb/brew"
echo "   brew install mongodb-community"
echo "3. Start MongoDB:"
echo "   brew services start mongodb-community"

# Make other scripts executable
chmod +x start_app.sh

echo "Setup completed. Run './start_app.sh' to start the application."