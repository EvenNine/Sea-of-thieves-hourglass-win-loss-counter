import pyautogui
import pytesseract
import time
from PIL import Image
import logging
from datetime import datetime, timedelta
import os
import sys
import colorama
from configparser import ConfigParser
from pynput import keyboard

# Credit Ekim941

# Global Variables
## Config File
config = ConfigParser()
config.read("./config.ini")

## Scoreboard file
Scoreboard = ConfigParser()
Scoreboard.read("./scoreboard.ini")

class ScreenPatternCounter:

    def __init__(self, region, tesseract_path=None, check_interval=1.0, cooldown_period=120):
        self.region = region
        self.check_interval = check_interval
        self.cooldown_period = cooldown_period
        self.last_detection_time = None
        self.running = True

        # Initialize colorama for Windows color support
        colorama.init()

        # Configure Tesseract path
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        # Verify Tesseract installation
        try:
            pytesseract.get_tesseract_version()
            self.print_colored("Tesseract OCR initialized successfully", "green")
        except Exception as e:
            self.print_colored("ERROR: Tesseract OCR not found or not configured properly", "red")
            sys.exit(1)

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[logging.FileHandler('pattern_counter.log')]
        )

        # Initialize counters
        self.wins_count_lifetime = int(Scoreboard['Lifetime']['wins'])
        self.losses_count_lifetime = int(Scoreboard['Lifetime']['losses'])
        self.wins_count_CurrentSession = int(Scoreboard['CurrentSession']['wins'])
        self.losses_count_CurrentSession = int(Scoreboard['CurrentSession']['losses'])
        self.wins_count_CurrentStreak = int(Scoreboard['CurrentSession']['streak'])
        


    def on_press(self, key):
        try:
            EndScript = config['Settings']['End_Script']
            AddWin = config['Settings']['Add_Win']
            AddLoss = config['Settings']['Add_Loss']
            IncreaseStreak = config['Settings']['Increase_Streak']
            
            if key.char == EndScript:  # Stop if "`" is pressed
                self.running = False
                return False  # Stops the listener
                
            elif key.char == AddWin:  # Increase Streak
                self.wins_count_lifetime += 1
                self.wins_count_CurrentSession += 1
                self.wins_count_CurrentStreak += 1
                
                Scoreboard['Lifetime']['wins'] = str(self.wins_count_lifetime)
                Scoreboard['CurrentSession']['wins'] = str(self.wins_count_CurrentSession)
                Scoreboard['CurrentSession']['streak'] = str(self.wins_count_CurrentStreak)
            
                with open('scoreboard.ini', 'w') as configfile:
                    Scoreboard.write(configfile)
                self.print_colored(f"\nWin manually added. Total wins: {self.wins_count_lifetime}", "yellow")
                
            elif key.char == AddLoss:  # Decrease Streak 
                self.losses_count_lifetime += 1
                self.losses_count_CurrentSession += 1
                self.wins_count_CurrentStreak *= 0
                Scoreboard['Lifetime']['losses'] = str(self.losses_count_lifetime)
                Scoreboard['CurrentSession']['losses'] = str(self.losses_count_CurrentSession)
                Scoreboard['CurrentSession']['streak'] = str(self.wins_count_CurrentStreak)
               
            
                with open('scoreboard.ini', 'w') as configfile:
                    Scoreboard.write(configfile)
                self.print_colored(f"\nLoss manually added. Total losses: {self.losses_count_lifetime}", "yellow")

            elif key.char == IncreaseStreak:  # Increase Streak

                self.wins_count_CurrentStreak += 1
                
                Scoreboard['CurrentSession']['streak'] = str(self.wins_count_CurrentStreak)
            
                with open('scoreboard.ini', 'w') as configfile:
                    Scoreboard.write(configfile)
                self.print_colored(f"\nStreak manually increased. Streak: {self.wins_count_CurrentStreak}", "yellow")             

             
        except AttributeError:
            pass

    def get_cooldown_status(self):
        if not self.last_detection_time:
            return 0, False
        elapsed = (datetime.now() - self.last_detection_time).total_seconds()
        remaining = max(0, self.cooldown_period - elapsed)
        return remaining, remaining > 0

    def print_colored(self, message, color):
        colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "blue": "\033[94m",
            "yellow": "\033[93m",
            "reset": "\033[0m"
        }
        print(f"{colors[color]}{message}{colors['reset']}")

    def capture_region(self):
        try:
            return pyautogui.screenshot(region=self.region)
        except Exception as e:
            self.print_colored(f"Error capturing screen: {e}", "red")
            return None

    def process_image(self, image):
        try:
            return pytesseract.image_to_string(image, timeout=15).strip().lower()
        except Exception as e:
            self.print_colored(f"Error processing image: {e}", "red")
            return ""

    def check_patterns(self, text):
        remaining_cooldown, in_cooldown = self.get_cooldown_status()
        if in_cooldown:
            return None

        if "streak increased" in text:
            self.wins_count_lifetime += 1
            self.wins_count_CurrentSession += 1
            Scoreboard['Lifetime']['wins'] = str(self.wins_count_lifetime)
            Scoreboard['CurrentSession']['wins'] = str(self.wins_count_CurrentSession)
            
            with open('scoreboard.ini', 'w') as configfile:
                Scoreboard.write(configfile)

            self.print_colored(f"\nWin detected! Total wins: {self.wins_count_lifetime}", "green")
            self.last_detection_time = datetime.now()
            return "win"

        elif "battle lost" in text:
            self.losses_count_lifetime += 1
            self.losses_count_CurrentSession += 1
            Scoreboard['Lifetime']['losses'] = str(self.losses_count_lifetime)
            Scoreboard['CurrentSession']['losses'] = str(self.losses_count_CurrentSession)
            
            with open('scoreboard.ini', 'w') as configfile:
                Scoreboard.write(configfile)

            self.print_colored(f"\nLoss detected! Total losses: {self.losses_count_lifetime}", "yellow")
            self.last_detection_time = datetime.now()
            return "loss"
        
        return None

    def run(self):
        EndScript = config['Settings']['End_Script']
        AddWin = config['Settings']['Add_Win']
        AddLoss = config['Settings']['Add_Loss']
        IncreaseStreak = config['Settings']['Increase_Streak']
        
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_colored("=== Screen Pattern Monitor Started ===", "blue")
        self.print_colored("\nCurrent Keybinds are as follow", "blue")
        self.print_colored(f"Add Win: {AddWin} \nAdd Loss:{AddLoss} \nIncrease Streak: {IncreaseStreak} \nClose Script {EndScript} ", "blue")
        self.print_colored("You can change these by editing the config.ini file", "blue")

        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()

        while self.running:
            remaining_cooldown, in_cooldown = self.get_cooldown_status()

            if in_cooldown:
                minutes = int(remaining_cooldown // 60)
                seconds = int(remaining_cooldown % 60)
                sys.stdout.write(f"\rCooldown active: {minutes:02d}:{seconds:02d} remaining  ")
                sys.stdout.flush()
            else:
                sys.stdout.write("\rMonitoring...                            \n")
                sys.stdout.flush()

            if not in_cooldown:
                screenshot = self.capture_region()
                if screenshot:
                    text = self.process_image(screenshot)
                    self.check_patterns(text)
            
            time.sleep(self.check_interval)

        self.print_colored("\nMonitoring stopped.", "yellow")
        listener.stop()


def main():
    Scoreboard['CurrentSession']['losses'] = "0"
    Scoreboard['CurrentSession']['wins'] = "0"
    Scoreboard['CurrentSession']['streak'] = "0"

    with open('scoreboard.ini', 'w') as configfile:
        Scoreboard.write(configfile)

    tesseract_path = config['Settings']['Tesseract_Path']
    screen_width, screen_height = pyautogui.size()
    region = ((screen_width - 1000) // 2, screen_height - 200, 1000, 200)

    monitor = ScreenPatternCounter(region, tesseract_path, check_interval=11.0, cooldown_period=60)
    monitor.run()

if __name__ == "__main__":
    main()
