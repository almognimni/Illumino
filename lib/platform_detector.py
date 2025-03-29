import platform
import sys
from lib.log_setup import logger


class PlatformDetector:
    """Detects the platform and provides appropriate implementations for hardware interactions."""
    
    def __init__(self):
        self.is_raspberry_pi = self._is_raspberry_pi()
        self.is_development = not self.is_raspberry_pi
        logger.info(f"Platform detection: Raspberry Pi = {self.is_raspberry_pi}, Development mode = {self.is_development}")
    
    def _is_raspberry_pi(self):
        """Check if the current platform is a Raspberry Pi."""
        # Method 1: Check for 'arm' in machine
        if platform.machine().startswith('arm'):
            return True
            
        # Method 2: Check for Raspberry Pi in model info
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read()
                return 'Raspberry Pi' in model
        except:
            pass
            
        # On Windows/macOS, definitely not a Pi
        if platform.system() in ('Windows', 'Darwin'):
            return False
            
        return False
    
    def get_gpio_module(self):
        """Return the appropriate GPIO module based on platform."""
        if self.is_raspberry_pi:
            try:
                import RPi.GPIO as GPIO
                return GPIO
            except ImportError:
                logger.error("Failed to import RPi.GPIO module on Raspberry Pi")
                sys.exit(1)
        else:
            # Return mock GPIO implementation for development
            from lib.gpio_emulator import GPIO
            return GPIO
    
    def get_led_strip_class(self):
        """Return the appropriate LED strip class based on platform."""
        if self.is_raspberry_pi:
            try:
                from rpi_ws281x import Adafruit_NeoPixel, Color
                return Adafruit_NeoPixel
            except ImportError:
                logger.error("Failed to import rpi_ws281x.Adafruit_NeoPixel module on Raspberry Pi")
                sys.exit(1)
        else:
            # Return emulated LED strip for development
            from lib.ledstrip_emulator import Adafruit_NeoPixel_Emulator
            return Adafruit_NeoPixel_Emulator
    
    def get_led_strip_constants(self):
        """Return LED strip constants based on platform."""
        if self.is_raspberry_pi:
            try:
                from rpi_ws281x import ws
                return {
                    'LED_STRIP': ws.WS2811_STRIP_GRB,
                    'WS2811_STRIP_GRB': ws.WS2811_STRIP_GRB,
                    'WS2811_STRIP_RGB': ws.WS2811_STRIP_RGB,
                    'WS2811_STRIP_RBG': ws.WS2811_STRIP_RBG,
                    'WS2811_STRIP_GBR': ws.WS2811_STRIP_GBR,
                    'WS2811_STRIP_BGR': ws.WS2811_STRIP_BGR,
                    'WS2811_STRIP_BRG': ws.WS2811_STRIP_BRG
                }
            except ImportError:
                logger.error("Failed to import rpi_ws281x.ws module on Raspberry Pi")
                sys.exit(1)
        else:
            # Return mock constants for development
            from lib.ledstrip_emulator import (
                LED_STRIP, WS2811_STRIP_GRB, WS2811_STRIP_RGB, 
                WS2811_STRIP_RBG, WS2811_STRIP_GBR, WS2811_STRIP_BGR, WS2811_STRIP_BRG
            )
            return {
                'LED_STRIP': LED_STRIP,
                'WS2811_STRIP_GRB': WS2811_STRIP_GRB,
                'WS2811_STRIP_RGB': WS2811_STRIP_RGB,
                'WS2811_STRIP_RBG': WS2811_STRIP_RBG,
                'WS2811_STRIP_GBR': WS2811_STRIP_GBR,
                'WS2811_STRIP_BGR': WS2811_STRIP_BGR,
                'WS2811_STRIP_BRG': WS2811_STRIP_BRG
            }
    
    def manage_hotspot(self, hotspot, usersettings, midiports, startup=False):
        """Manage hotspot functionality."""
        # In development mode, we don't need to do anything with the hotspot
        if self.is_development:
            return
        
        # On Raspberry Pi, call the real hotspot manager
        if hasattr(hotspot, 'manage'):
            hotspot.manage(usersettings, midiports, startup) 