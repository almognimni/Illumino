import os
import time
from xml.dom import minidom
import mido
from lib.log_setup import logger


class MenuLCDMock:
    """Mock implementation of MenuLCD for desktop development"""
    def __init__(self, xml_file_name, args, usersettings, ledsettings, ledstrip, learning, saving, midiports, hotspot, platform):
        self.usersettings = usersettings
        self.ledsettings = ledsettings
        self.ledstrip = ledstrip
        self.learning = learning
        self.saving = saving
        self.midiports = midiports
        self.hotspot = hotspot
        self.platform = platform
        self.args = args
        
        # Load the menu XML file if it exists
        if os.path.exists(xml_file_name):
            try:
                self.DOMTree = minidom.parse(xml_file_name)
            except Exception as e:
                logger.warning(f"Failed to parse menu XML: {str(e)}")
                # Create a minimal DOM tree
                self.DOMTree = minidom.getDOMImplementation().createDocument(None, "menu", None)
        else:
            logger.warning(f"Menu XML file {xml_file_name} not found")
            # Create a minimal DOM tree
            self.DOMTree = minidom.getDOMImplementation().createDocument(None, "menu", None)
            
        self.current_location = "menu"
        self.pointer_position = 0
        self.background_color = usersettings.get_setting_value("background_color")
        self.text_color = usersettings.get_setting_value("text_color")
        
        # Values for screensaver functionality
        self.screensaver_delay = usersettings.get_setting_value("screensaver_delay")
        self.screen_off_delay = usersettings.get_setting_value("screen_off_delay")
        self.led_animation_delay = usersettings.get_setting_value("led_animation_delay")
        self.led_animation = usersettings.get_setting_value("led_animation")
        self.screen_on = int(usersettings.get_setting_value("screen_on"))
        self.screen_status = 1
        self.screensaver_is_running = False
        self.last_activity = time.time()
        self.is_idle_animation_running = False
        self.is_animation_running = False
        
        # Mock screensaver settings
        self.screensaver_settings = {
            'time': usersettings.get_setting_value("time"),
            'date': usersettings.get_setting_value("date"),
            'cpu_chart': usersettings.get_setting_value("cpu_chart"),
            'cpu': usersettings.get_setting_value("cpu"),
            'ram': usersettings.get_setting_value("ram"),
            'temp': usersettings.get_setting_value("temp"),
            'network_usage': usersettings.get_setting_value("network_usage"),
            'sd_card_space': usersettings.get_setting_value("sd_card_space"),
            'local_ip': usersettings.get_setting_value("local_ip")
        }
        
        self.update_songs()
        self.update_ports()
        self.update_led_note_offsets()
        self.speed_multiplier = 1
        
        logger.info("Mock LCD menu initialized")
    
    def update_songs(self):
        """Update the songs list in the menu tree"""
        try:
            # Get the songs from the Songs directory
            if os.path.exists("Songs"):
                songs_list = os.listdir("Songs")
                logger.info(f"Found {len(songs_list)} songs")
        except Exception as e:
            logger.warning(f"Failed to update songs: {str(e)}")
    
    def update_ports(self):
        """Update MIDI ports in the menu tree"""
        try:
            ports = list(dict.fromkeys(mido.get_input_names()))
            logger.info(f"Found {len(ports)} MIDI ports")
        except Exception as e:
            logger.warning(f"Failed to update ports: {str(e)}")
    
    def update_led_note_offsets(self):
        """Update LED note offsets in the menu tree"""
        logger.info("Mock: update_led_note_offsets")
        pass
    
    def update_multicolor(self, colors_list):
        """Update multicolor settings in the menu tree"""
        logger.info(f"Mock: update_multicolor with {len(colors_list)} colors")
        pass
    
    def show(self, position="default", back_pointer_location=None):
        """Update the display (mock implementation - just logs)"""
        self.last_activity = time.time()
        logger.debug(f"Mock LCD show: position={position}, location={self.current_location}")
        return
    
    def change_pointer(self, direction):
        """Change the pointer position in the menu"""
        logger.debug(f"Mock: change_pointer {direction}")
        return
    
    def enter_menu(self):
        """Enter the selected menu item"""
        logger.debug(f"Mock: enter_menu at position {self.pointer_position}")
        return
    
    def go_back(self):
        """Go back to the previous menu"""
        logger.debug(f"Mock: go_back from {self.current_location}")
        return
    
    def render_message(self, title, message, delay=500):
        """Render a message on the display (mock implementation)"""
        logger.info(f"Mock LCD message: {title} - {message}")
        return
    
    def render_screensaver(self, hour=None, date=None, cpu=None, cpu_average=None, ram=None, temp=None, 
                          cpu_history=None, upload=0, download=0, card_space=None, local_ip="0.0.0.0"):
        """Render the screensaver (mock implementation)"""
        logger.debug("Mock: render_screensaver")
        return
    
    def change_settings(self, choice, location):
        """Change a setting value"""
        logger.info(f"Mock: change_settings - {choice} at {location}")
        return 0
    
    def change_value(self, value):
        """Change a value in the current menu"""
        logger.debug(f"Mock: change_value {value}")
        return
    
    def toggle_screensaver_settings(self, setting):
        """Toggle a screensaver setting"""
        setting = setting.lower()
        setting = setting.replace(" ", "_")
        if str(self.screensaver_settings[setting]) == "1":
            self.usersettings.change_setting_value(setting, "0")
            self.screensaver_settings[setting] = "0"
        else:
            self.usersettings.change_setting_value(setting, "1")
            self.screensaver_settings[setting] = "1"
        return
    
    def disable_screen(self):
        """Disable the screen (mock implementation)"""
        logger.debug("Mock: disable_screen")
        self.screen_status = 0
        return
    
    def enable_screen(self):
        """Enable the screen (mock implementation)"""
        logger.debug("Mock: enable_screen")
        self.screen_status = 1
        return
    
    def speed_change(self):
        """Change the animation speed multiplier"""
        logger.debug(f"Mock: speed_change to {self.speed_multiplier}")
        return 