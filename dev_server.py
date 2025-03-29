#!/usr/bin/env python3
"""
Development server for the Illumino web interface.
This script allows you to run the web interface on a desktop environment for development purposes.
"""

import sys
import os
import asyncio
import threading
import argparse
from flask_cors import CORS
from flask import Flask, request, jsonify

# Add the current directory to the path so we can import the modules
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

from lib.platform_detector import PlatformDetector
from lib.argument_parser import ArgumentParser
from lib.component_initializer import ComponentInitializer
from lib.webinterface_manager import WebInterfaceManager
from lib.log_setup import logger


def parse_args():
    parser = argparse.ArgumentParser(description='Illumino Web Interface Development Server')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the web server on (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    return parser.parse_args()


def main():
    # Parse command line arguments
    args = parse_args()
    
    # Set current directory to the script directory
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    
    logger.info('Starting development server for Illumino web interface')
    
    # Check if we're on a Raspberry Pi
    platform_detector = PlatformDetector()
    if platform_detector.is_raspberry_pi:
        logger.warning('Running on a Raspberry Pi. Consider using the main visualizer.py script instead.')
    
    # Initialize components using the standard component initializer
    # This will use our platform detector to create appropriate mock objects
    illumino_args = ArgumentParser().args
    illumino_args.webinterface = True
    illumino_args.port = args.port
    
    component_initializer = ComponentInitializer(illumino_args)
    
    # Initialize the web interface
    web_interface_manager = WebInterfaceManager(
        illumino_args,
        component_initializer.usersettings,
        component_initializer.ledsettings,
        component_initializer.ledstrip,
        component_initializer.learning,
        component_initializer.saving,
        component_initializer.midiports,
        component_initializer.menu,
        component_initializer.hotspot,
        component_initializer.platform
    )
    
    # Import the Flask app after initialization to avoid circular imports
    from webinterface import webinterface
    
    # Enable CORS for development
    CORS(webinterface)
    
    # Run the Flask development server
    webinterface.run(
        host=args.host,
        port=args.port,
        debug=args.debug,
        use_reloader=False  # Disable reloader to avoid duplicate initialization
    )


if __name__ == "__main__":
    main() 