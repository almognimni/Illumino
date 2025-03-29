import time
import os
import platform
from lib.log_setup import logger


class Hotspot:
    """Platform-independent hotspot implementation."""
    
    def __init__(self, platform_instance):
        self.platform_instance = platform_instance
        self.hotspot_script_time = 0
        self.time_without_wifi = 0
        self.last_wifi_check_time = 0
        
        # Only try to configure permissions on Raspberry Pi
        if platform.system() == 'Linux':
            try:
                # Check if it's a Raspberry Pi and has the proper directory
                if os.path.exists('/home/Piano-LED-Visualizer/'):
                    import subprocess
                    subprocess.run("sudo chmod a+rwxX -R /home/Piano-LED-Visualizer/", shell=True, check=False)
            except Exception as e:
                logger.warning(f"Failed to set permissions: {str(e)}")
    
    def manage(self, usersettings, midiports, startup=False):
        """Manage hotspot functionality, does nothing on non-Raspberry Pi systems."""
        if hasattr(self.platform_instance, 'manage_hotspot'):
            self.platform_instance.manage_hotspot(self, usersettings, midiports, startup) 