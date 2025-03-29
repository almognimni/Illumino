from lib.log_setup import logger
import numpy as np


class Adafruit_NeoPixel_Emulator:
    """Emulates the rpi_ws281x Adafruit_NeoPixel class for desktop development."""
    def __init__(self, num_pixels, pin, freq_hz, dma, invert, brightness, channel, strip_type):
        self.num_pixels = num_pixels
        self.pin = pin
        self.freq_hz = freq_hz
        self.dma = dma
        self.invert = invert
        self.brightness = brightness
        self.channel = channel
        self.strip_type = strip_type
        
        # Initialize pixel array (RGB values from 0-255)
        self._pixels = [(0, 0, 0) for _ in range(num_pixels)]
        
        logger.info(f"Initialized LED strip emulator with {num_pixels} pixels")
        
    def begin(self):
        """Initialize the library (must be called once before other functions)."""
        logger.info("LED strip emulator began")
        return
        
    def show(self):
        """Update the display with the data from the LED buffer."""
        # In a real implementation, this would push data to the LEDs
        # For the emulator, we do nothing as the web interface will access _pixels directly
        return
        
    def setPixelColor(self, n, color):
        """Set LED at position n to the provided 24-bit color value."""
        if 0 <= n < self.num_pixels:
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
            self._pixels[n] = (r, g, b)
        
    def setPixelColorRGB(self, n, red, green, blue, white=0):
        """Set LED at position n to the provided RGB color."""
        if 0 <= n < self.num_pixels:
            self._pixels[n] = (red, green, blue)
        
    def getPixels(self):
        """Return an array of pixel data."""
        return self._pixels
        
    def numPixels(self):
        """Return the number of pixels in the display."""
        return self.num_pixels
        
    def getPixelColor(self, n):
        """Get the 24-bit RGB color value for the LED at position n."""
        if 0 <= n < self.num_pixels:
            r, g, b = self._pixels[n]
            return (r << 16) | (g << 8) | b
        return 0
        
    def setBrightness(self, brightness):
        """Scale each LED in the buffer by the provided brightness."""
        self.brightness = brightness


# These constants are required for compatibility with rpi_ws281x
LED_STRIP = 0
WS2811_STRIP_GRB = 0
WS2811_STRIP_RGB = 0
WS2811_STRIP_RBG = 0
WS2811_STRIP_GBR = 0
WS2811_STRIP_BGR = 0
WS2811_STRIP_BRG = 0
WS2812_STRIP = 0
SK6812_STRIP = 0
SK6812W_STRIP = 0 