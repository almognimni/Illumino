import time
import subprocess
from subprocess import call
import os
import filecmp
from shutil import copyfile
from lib.log_setup import logger
import re
import socket
import platform as py_platform
from collections import defaultdict
from lib.platform_detector import PlatformDetector


class PlatformBase:
    """Base platform implementation with default behaviors."""
    
    def __init__(self):
        self.detector = PlatformDetector()
        
    def __getattr__(self, name):
        def method(*args, **kwargs):
            return False, f"Method '{name}' is not supported on this platform", ""
        return method


class PlatformNull(PlatformBase):
    """Null platform implementation for non-Raspberry Pi environments."""
    
    def __init__(self):
        super().__init__()
        logger.info("Using null platform implementation")
    
    def __getattr__(self, name):
        return self.pass_func

    def pass_func(self, *args, **kwargs):
        pass
    
    def get_local_address(self):
        """Get the local IP address."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Doesn't need to be reachable
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception as e:
            logger.warning(f"Error getting local IP address: {str(e)}")
            return "127.0.0.1"
    
    def get_wifi_networks(self):
        """Mock implementation for desktop environments."""
        return [
            {"ssid": "Development Network", "signal": 90, "security": "WPA2"},
            {"ssid": "Test Network", "signal": 65, "security": "WPA"}
        ]


class PlatformRasp(PlatformBase):
    """Raspberry Pi specific platform implementation."""
    
    def __init__(self):
        super().__init__()
        logger.info("Using Raspberry Pi platform implementation")
    
    @staticmethod
    def copy_connectall_script():
        # make sure connectall.py file exists and is updated
        if not os.path.exists('/usr/local/bin/connectall.py') or \
                filecmp.cmp('/usr/local/bin/connectall.py', 'lib/connectall.py') is not True:
            logger.info("connectall.py script is outdated, updating...")
            copyfile('lib/connectall.py', '/usr/local/bin/connectall.py')
            os.chmod('/usr/local/bin/connectall.py', 493)

    def install_midi2abc(self):
        if not self.is_package_installed("abcmidi"):
            logger.info("Installing abcmidi")
            subprocess.call(['sudo', 'apt-get', 'install', 'abcmidi', '-y'])

    @staticmethod
    def update_visualizer():
        call("sudo git reset --hard HEAD", shell=True)
        call("sudo git checkout .", shell=True)
        call("sudo git clean -fdx -e Songs/ -e "
             "config/settings.xml -e config/wpa_disable_ap.conf -e visualizer.log", shell=True)
        call("sudo git clean -fdx Songs/cache", shell=True)
        call("sudo git pull origin master", shell=True)
        call("sudo pip install -r requirements.txt", shell=True)

    @staticmethod
    def shutdown():
        call("sudo /sbin/shutdown -h now", shell=True)

    @staticmethod
    def reboot():
        call("sudo /sbin/reboot now", shell=True)

    @staticmethod
    def restart_visualizer():
        call("sudo systemctl restart visualizer", shell=True)

    @staticmethod
    def restart_rtpmidid():
        call("sudo systemctl restart rtpmidid", shell=True)

    @staticmethod
    def is_package_installed(package_name):
        try:
            # Run the 'dpkg' command to check if the package is installed
            result = subprocess.run(['dpkg', '-s', package_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    check=True, text=True)
            output = result.stdout
            status_line = [line for line in output.split('\n') if line.startswith('Status:')][0]

            if "install ok installed" in status_line:
                logger.info(f"{package_name} package is installed")
                return True
            else:
                logger.info(f"{package_name} package is not installed")
                return False
        except subprocess.CalledProcessError:
            logger.warning(f"Error checking {package_name} package status")
            return False

    @staticmethod
    def create_hotspot_profile():
        # Check if the 'Hotspot' profile already exists
        check_profile = subprocess.run(['sudo', 'nmcli', 'connection', 'show', 'Hotspot'],
                                       capture_output=True, text=True)

        if 'Hotspot' in check_profile.stdout:
            logger.info("Hotspot profile already exists. Skipping creation.")
            return

        # If we reach here, the profile doesn't exist, so we create it
        logger.info("Creating new Hotspot profile...")

        try:
            subprocess.run([
                'sudo', 'nmcli', 'connection', 'add', 'type', 'wifi', 'ifname', 'wlan0',
                'con-name', 'Hotspot', 'autoconnect', 'no', 'ssid', 'PianoLEDVisualizer'
            ], check=True)

            subprocess.run([
                'sudo', 'nmcli', 'connection', 'modify', 'Hotspot',
                '802-11-wireless.mode', 'ap', '802-11-wireless.band', 'bg',
                'ipv4.method', 'shared'
            ], check=True)

            subprocess.run([
                'sudo', 'nmcli', 'connection', 'modify', 'Hotspot',
                'wifi-sec.key-mgmt', 'wpa-psk'
            ], check=True)

            subprocess.run([
                'sudo', 'nmcli', 'connection', 'modify', 'Hotspot',
                'wifi-sec.psk', 'visualizer'
            ], check=True)

            logger.info("Hotspot profile created successfully.")
        except subprocess.CalledProcessError as e:
            logger.warning(f"An error occurred while creating the Hotspot profile: {e}")

    @staticmethod
    def enable_hotspot():
        logger.info("Enabling Hotspot")
        subprocess.run(['sudo', 'nmcli', 'connection', 'up', 'Hotspot'])

    @staticmethod
    def disable_hotspot():
        logger.info("Disabling Hotspot")
        subprocess.run(['sudo', 'nmcli', 'connection', 'down', 'Hotspot'])

    @staticmethod
    def get_current_connections():
        try:
            with open(os.devnull, 'w') as null_file:
                output = subprocess.check_output(['iwconfig'], text=True, stderr=null_file)

            if "Mode:Master" in output:
                return False, "Running as hotspot", ""

            for line in output.split('\n'):
                if "ESSID:" in line:
                    ssid = line.split("ESSID:")[-1].strip().strip('"')
                    if ssid != "off/any":
                        access_point_line = [line for line in output.split('\n') if "Access Point:" in line]
                        if access_point_line:
                            access_point = access_point_line[0].split("Access Point:")[1].strip()
                            return True, ssid, access_point
                        return False, "Not connected to any Wi-Fi network.", ""
                    return False, "Not connected to any Wi-Fi network.", ""

            return False, "No Wi-Fi interface found.", ""
        except subprocess.CalledProcessError:
            return False, "Error occurred while getting Wi-Fi information.", ""

    def is_hotspot_running(self):
        try:
            result = subprocess.run(
                ['nmcli', 'connection', 'show', '--active'],
                capture_output=True,
                text=True
            )
            return 'Hotspot' in result.stdout
        except Exception as e:
            logger.warning(f"Error checking hotspot status: {str(e)}")
            return False

    def manage_hotspot(self, hotspot, usersettings, midiports, first_run=False):
        if first_run:
            self.create_hotspot_profile()
            if int(usersettings.get_setting_value("is_hotspot_active")):
                if not self.is_hotspot_running():
                    logger.info("Hotspot is enabled in settings but not running. Starting hotspot...")
                    self.enable_hotspot()
                    time.sleep(5)

                    if self.is_hotspot_running():
                        logger.info("Hotspot started successfully")
                    else:
                        logger.warning("Failed to start hotspot")
                else:
                    logger.info("Hotspot is already running")

        current_time = time.time()
        if not hotspot.last_wifi_check_time:
            hotspot.last_wifi_check_time = current_time

        if (current_time - hotspot.hotspot_script_time) > 60 and (current_time - midiports.last_activity) > 60:
            hotspot.hotspot_script_time = current_time
            if int(usersettings.get_setting_value("is_hotspot_active")):
                return

            wifi_success, wifi_ssid, _ = self.get_current_connections()

            if not wifi_success:
                hotspot.time_without_wifi += (current_time - hotspot.last_wifi_check_time)
                if hotspot.time_without_wifi > 240:
                    logger.info("No wifi connection. Enabling hotspot")
                    usersettings.change_setting_value("is_hotspot_active", 1)
                    self.enable_hotspot()
            else:
                hotspot.time_without_wifi = 0

        hotspot.last_wifi_check_time = current_time

    def connect_to_wifi(self, ssid, password, hotspot, usersettings):
        # Disable the hotspot first
        self.disable_hotspot()

        try:
            result = subprocess.run(
                ['sudo', 'nmcli', 'device', 'wifi', 'connect', ssid, 'password', password],
                capture_output=True,
                text=True,
                timeout=30  # Set a timeout for the connection attempt
            )
            # Check if the connection was successful
            if result.returncode == 0:
                logger.info(f"Successfully connected to {ssid}")
                usersettings.change_setting_value("is_hotspot_active", 0)
                return True
            else:
                logger.warning(f"Failed to connect to {ssid}. Error: {result.stderr}")
                usersettings.change_setting_value("is_hotspot_active", 1)
                self.enable_hotspot()

        except subprocess.TimeoutExpired:
            logger.warning(f"Connection attempt to {ssid} timed out")
            usersettings.change_setting_value("is_hotspot_active", 1)
            self.enable_hotspot()
        except Exception as e:
            logger.warning(f"An error occurred while connecting to {ssid}: {str(e)}")
            usersettings.change_setting_value("is_hotspot_active", 1)
            self.enable_hotspot()

    def disconnect_from_wifi(self, hotspot, usersettings):
        logger.info("Disconnecting from wifi")
        # Get a list of active connections
        active_connections = subprocess.run(['nmcli', '-t', '-f', 'NAME', 'connection', 'show', '--active'],
                                          capture_output=True, text=True)

        for connection in active_connections.stdout.strip().split('\n'):
            if connection and connection != 'Hotspot':
                # Disable the connection
                subprocess.run(['sudo', 'nmcli', 'connection', 'down', connection])

        # Set the hotspot flag
        usersettings.change_setting_value("is_hotspot_active", 1)
        self.enable_hotspot()

    @staticmethod
    def get_wifi_networks():
        networks = []
        try:
            result = subprocess.run(['sudo', 'nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY', 'device', 'wifi', 'list'],
                                   capture_output=True, text=True)

            def calculate_signal_strength(level):
                # Map the signal level to a percentage (0% to 100%) linearly.
                # -50 dBm or higher -> 100%
                # -90 dBm or lower -> 0%
                try:
                    level = int(level)
                    return max(0, min(100, level))
                except ValueError:
                    return 0

            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(':')
                    if len(parts) >= 3:
                        ssid = parts[0]
                        signal = calculate_signal_strength(parts[1])
                        security = ':'.join(parts[2:])  # Join in case security field contains ':'
                        
                        # Skip empty SSIDs
                        if ssid:
                            # Check if network is already in the list
                            existing_network = next((net for net in networks if net["ssid"] == ssid), None)
                            if existing_network:
                                # If same network appears multiple times, keep the one with the strongest signal
                                if signal > existing_network["signal"]:
                                    existing_network["signal"] = signal
                                    existing_network["security"] = security
                            else:
                                networks.append({
                                    "ssid": ssid,
                                    "signal": signal,
                                    "security": security
                                })
        
            # Sort by signal strength, descending
            networks.sort(key=lambda x: x["signal"], reverse=True)
            return networks
        except Exception as e:
            logger.warning(f"Error getting WiFi networks: {str(e)}")
            return []

    @staticmethod
    def get_local_address():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Doesn't need to be reachable
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    @staticmethod
    def change_local_address(new_name):
        # Check if new_name is a valid hostname
        if not re.match(r'^[a-zA-Z0-9-]{1,63}$', new_name):
            return False, "Invalid hostname. Only letters, numbers, and hyphens are allowed."

        try:
            # Update hostname in /etc/hostname
            with open('/etc/hostname', 'w') as f:
                f.write(new_name)

            # Update /etc/hosts
            with open('/etc/hosts', 'r') as f:
                lines = f.readlines()

            with open('/etc/hosts', 'w') as f:
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2 and parts[0] == '127.0.1.1':
                            # Modify this line
                            parts[1] = new_name
                            f.write(' '.join(parts) + '\n')
                        else:
                            f.write(line)

            # Apply changes
            subprocess.run(['sudo', 'systemctl', 'restart', 'avahi-daemon'])
            
            return True, f"Hostname changed to {new_name}. Please reboot for changes to take full effect."
        except Exception as e:
            return False, f"Error changing hostname: {str(e)}"


def get_platform_instance():
    """Factory function to get the appropriate platform implementation."""
    detector = PlatformDetector()
    if detector.is_raspberry_pi:
        return PlatformRasp()
    else:
        return PlatformNull()
