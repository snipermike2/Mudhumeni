#!/bin/bash
# setup_mudhumeni.sh - Mudhumeni AI Setup Script for macOS
# This script automates the setup process for the Mudhumeni AI project on macOS

# Colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Mudhumeni AI macOS Setup Script ===${NC}"
echo "This script will set up your development environment for Mudhumeni AI."

# Step 1: Check if Python is installed
echo -e "\n${YELLOW}Checking Python installation...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}Found $PYTHON_VERSION${NC}"
else
    echo -e "${RED}Python 3 not found. Please install Python 3.9 or later.${NC}"
    echo "You can install it using Homebrew with: brew install python@3.9"
    exit 1
fi

# Step 2: Check if pip is installed
echo -e "\n${YELLOW}Checking pip installation...${NC}"
if command -v pip3 &>/dev/null; then
    PIP_VERSION=$(pip3 --version)
    echo -e "${GREEN}Found $PIP_VERSION${NC}"
else
    echo -e "${RED}pip not found. Please install pip.${NC}"
    exit 1
fi

# Step 3: Check if project directory exists or create it
echo -e "\n${YELLOW}Setting up project directory...${NC}"
PROJECT_DIR="$HOME/Projects/Mudhumeni_AI"

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${GREEN}Project directory already exists at $PROJECT_DIR${NC}"
else
    echo "Creating project directory at $PROJECT_DIR"
    mkdir -p "$PROJECT_DIR"
    echo -e "${GREEN}Created project directory at $PROJECT_DIR${NC}"
fi

# Step 4: Navigate to project directory
cd "$PROJECT_DIR"
echo -e "${GREEN}Changed to directory: $PROJECT_DIR${NC}"

# Step 5: Create virtual environment
echo -e "\n${YELLOW}Setting up virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${GREEN}Virtual environment already exists${NC}"
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Virtual environment created successfully${NC}"
    else
        echo -e "${RED}Failed to create virtual environment${NC}"
        exit 1
    fi
fi

# Step 6: Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Virtual environment activated${NC}"
else
    echo -e "${RED}Failed to activate virtual environment${NC}"
    exit 1
fi

# Step 7: Install required packages
echo -e "\n${YELLOW}Installing required packages...${NC}"
if [ -f "requirements.txt" ]; then
    echo "Installing from requirements.txt..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Packages installed successfully${NC}"
    else
        echo -e "${RED}Failed to install packages${NC}"
        exit 1
    fi
else
    echo "requirements.txt not found. Installing core packages..."
    pip install flask langchain-groq numpy pandas scikit-learn requests gunicorn Werkzeug==2.3.7
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Core packages installed successfully${NC}"
    else
        echo -e "${RED}Failed to install core packages${NC}"
        exit 1
    fi
fi

# Step 8: Check for MongoDB (optional)
echo -e "\n${YELLOW}Checking MongoDB installation (optional)...${NC}"
if brew list mongodb-community &>/dev/null; then
    echo -e "${GREEN}MongoDB is installed via Homebrew${NC}"
    echo "You can start MongoDB with: brew services start mongodb-community"
else
    echo -e "${YELLOW}MongoDB is not installed. If your project requires MongoDB, you can install it with:${NC}"
    echo "brew tap mongodb/brew"
    echo "brew install mongodb-community"
    echo "brew services start mongodb-community"
fi

# Step 9: Create a sample .env file
echo -e "\n${YELLOW}Creating sample .env file...${NC}"
if [ -f ".env" ]; then
    echo -e "${YELLOW}.env file already exists. Not overwriting.${NC}"
else
    cat > .env << EOF
# Mudhumeni AI Environment Variables
FLASK_SECRET_KEY=replace_with_your_secret_key
GROQ_API_KEY=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
# MongoDB Connection (if needed)
MONGODB_URI=mongodb://localhost:27017/
EOF
    echo -e "${GREEN}Sample .env file created. Remember to update it with your actual keys.${NC}"
fi

# Step 10: Print instructions for running the app
echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}To run Mudhumeni AI:${NC}"
echo "1. Ensure you're in the project directory: cd $PROJECT_DIR"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run the application: python app.py"
echo -e "\n${GREEN}Happy farming with Mudhumeni AI!${NC}"