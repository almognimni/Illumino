#!/bin/bash
echo "Starting Illumino Desktop Development Environment..."

# Activate virtual environment if it exists
if [ -f .venv/bin/activate ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Virtual environment not found. Creating one..."
    python3 -m venv .venv
    source .venv/bin/activate
    
    echo "Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

# Build Tailwind CSS if needed
if [ -f webinterface/package.json ]; then
    echo "Building Tailwind CSS..."
    cd webinterface
    npm install
    npm run build
    cd ..
fi

# Start the development server
echo "Starting development server..."
python dev_server.py --debug

# If we get here, the server has stopped
echo "Development server has stopped." 