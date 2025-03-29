@echo off
echo Starting Illumino Desktop Development Environment...

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo Virtual environment not found. Creating one...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    
    echo Installing development dependencies...
    pip install -r requirements-dev.txt
)

REM Build Tailwind CSS if needed
if exist webinterface\package.json (
    echo Building Tailwind CSS...
    cd webinterface
    npm install
    npm run build
    cd ..
)

REM Start the development server
echo Starting development server...
python dev_server.py --debug

REM If we get here, the server has stopped
echo Development server has stopped.
pause 
read -p "Press any key to continue..."
