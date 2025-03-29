import threading
import time

from lib import colormaps as cmap
from lib.functions import startup_animation, fastColorWipe
from lib.learnmidi import LearnMIDI
from lib.ledsettings import LedSettings
from lib.ledstrip import LedStrip
from lib.log_setup import logger
from lib.menu_mock import MenuLCDMock
from lib.menulcd import MenuLCD
from lib.midiports import MidiPorts
from lib.platform import get_platform_instance
from lib.hotspot import Hotspot
from lib.savemidi import SaveMIDI
from lib.usersettings import UserSettings
from lib.platform_detector import PlatformDetector


class ComponentInitializer:
    def __init__(self, args):
        self.args = args
        
        # Initialize the platform detector
        self.detector = PlatformDetector()
        
        # Get the appropriate platform instance
        self.platform = get_platform_instance()
        
        self.usersettings = UserSettings()
        self.midiports = MidiPorts(self.usersettings)
        self.ledsettings = LedSettings(self.usersettings)
        self.ledstrip = LedStrip(self.usersettings, self.ledsettings, self.args.leddriver if hasattr(self.args, 'leddriver') else "auto")
        self.learning = LearnMIDI(self.usersettings, self.ledsettings, self.midiports, self.ledstrip)
        self.hotspot = Hotspot(self.platform)
        self.saving = SaveMIDI()
        
        # Use the appropriate menu implementation based on the platform
        if self.detector.is_raspberry_pi:
            # Use the real LCD menu implementation on Raspberry Pi
            self.menu = MenuLCD("config/menu.xml", self.args, self.usersettings, self.ledsettings,
                                self.ledstrip, self.learning, self.saving, self.midiports,
                                self.hotspot, self.platform)
        else:
            # Use the mock menu implementation on desktop
            self.menu = MenuLCDMock("config/menu.xml", self.args, self.usersettings, self.ledsettings,
                                   self.ledstrip, self.learning, self.saving, self.midiports,
                                   self.hotspot, self.platform)
            
        self.setup_components()

    def setup_components(self):
        # Only run update-related tasks on Raspberry Pi
        if self.detector.is_raspberry_pi and not self.args.skipupdate:
            self.platform.copy_connectall_script()
            self.platform.install_midi2abc()
            
        logger.info(self.args)

        cmap.gradients.update(cmap.load_colormaps())
        cmap.generate_colormaps(cmap.gradients, self.ledstrip.led_gamma)
        cmap.update_multicolor(self.ledsettings.multicolor_range, self.ledsettings.multicolor)

        t = threading.Thread(target=startup_animation, args=(self.ledstrip, self.ledsettings))
        t.start()

        self.midiports.add_instance(self.menu)
        self.ledsettings.add_instance(self.menu, self.ledstrip)
        self.saving.add_instance(self.menu)
        self.learning.add_instance(self.menu)

        self.menu.show()
        self.midiports.last_activity = time.time()
        self.hotspot.hotspot_script_time = time.time()

        fastColorWipe(self.ledstrip.strip, True, self.ledsettings)
