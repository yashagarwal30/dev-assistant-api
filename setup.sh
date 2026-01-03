#!/bin/bash
# Setup script for Dev Assistant API

echo "Setting up Dev Assistant API..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file from example
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env and add your ANTHROPIC_API_KEY"
else
    echo ".env file already exists"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your ANTHROPIC_API_KEY"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the application: python run.py"
echo "4. Visit http://localhost:8000/docs for API documentation"
