# Illumino Desktop Development Environment

This guide provides instructions for setting up and using the desktop development environment for the Illumino project's web interface.

## Overview

The desktop development environment allows you to work on the Illumino web interface without requiring a Raspberry Pi. It uses emulators for the LED strip and GPIO functionality, making it possible to develop and test the web interface on Windows, macOS, or Linux.

## Prerequisites

- Python 3.7+ installed
- Git (for cloning the repository)

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Illumino.git
   cd Illumino
   ```

2. Create a virtual environment and activate it:
   ```bash
   # On Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # On macOS/Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Install the front-end dependencies:
   ```bash
   cd webinterface
   npm install
   npm run build
   cd ..
   ```

## Running the Development Server

To start the development server, run:

```bash
python dev_server.py
```

This will start the Flask development server on port 5000 by default.

### Command Line Options

- `--port PORT`: Specify a custom port (default: 5000)
- `--debug`: Run in Flask debug mode with auto-reloading
- `--host HOST`: Specify the host to bind to (default: 0.0.0.0)

Example:
```bash
python dev_server.py --port 8080 --debug
```

## Accessing the Web Interface

Once the development server is running, you can access the web interface at:

```
http://localhost:5000
```

## LED Emulator

The LED emulator provides a visual representation of the LED strip. It's available through a WebSocket connection at:

```
ws://localhost:8765/ledemu
```

The development environment automatically detects that it's running on a desktop and provides appropriate emulation for the hardware components.

## Development Tips

### Code Organization

- `webinterface/`: Contains the Flask web interface
  - `static/`: Static assets (CSS, JavaScript, images)
  - `templates/`: Jinja2 HTML templates
  - `views.py`: Main web interface routes
  - `views_api.py`: API routes

- `lib/`: Contains the core functionality
  - `ledstrip_emulator.py`: LED strip emulator for desktop development
  - `gpio_emulator.py`: GPIO emulator for desktop development
  - `platform_detector.py`: Detects the platform and provides appropriate implementations

### WebSocket Testing

You can test the WebSocket connections using tools like:
- [Postman](https://www.postman.com/)
- [WebSocket King](https://websocketking.com/)
- Browser DevTools

### Tailwind CSS

The web interface uses Tailwind CSS for styling. To rebuild the CSS after making changes:

```bash
cd webinterface
npm run build
```

## Deploying to a Raspberry Pi

When you're ready to deploy your changes to a Raspberry Pi:

1. Transfer the code to your Raspberry Pi (using SSH, USB drive, or Git)
2. Install the Raspberry Pi dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the main application:
   ```bash
   python visualizer.py
   ```

## Troubleshooting

### Port Already in Use
If you see an error like "Port already in use", try specifying a different port:
```bash
python dev_server.py --port 8080
```

### Missing Dependencies
If you encounter missing dependencies, make sure you've installed all requirements:
```bash
pip install -r requirements-dev.txt
```

### WebSocket Connection Issues
If you have trouble connecting to the WebSocket, check that your firewall isn't blocking the connection and that the server is running correctly. 