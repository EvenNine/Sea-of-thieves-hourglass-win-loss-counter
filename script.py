import pyautogui
import pytesseract
import time
from PIL import Image
import logging
from datetime import datetime, timedelta
import os
import sys
import msvcrt
import colorama
from configparser import ConfigParser

#Credit Ekim941

class ScreenPatternCounter:
    def __init__(self, region, tesseract_path=None, check_interval=1.0, cooldown_period=120):
        """
        Initialize the screen pattern counter.

        Args:
            region (tuple): Screen region to monitor (left, top, width, height)
            wins_file (str): Path to the wins counter file
            losses_file (str): Path to the losses counter file
            tesseract_path (str): Path to Tesseract executable
            check_interval (float): Time between checks in seconds
            cooldown_period (int): Cooldown period in seconds after detection
        """
        self.region = region
        
        self.check_interval = check_interval
        self.cooldown_period = cooldown_period
        self.last_detection_time = None
        self.in_cooldown = False

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
            self.print_colored("Please ensure Tesseract is installed and the path is correct", "red")
            self.print_colored(f"Current Tesseract path: {pytesseract.pytesseract.tesseract_cmd}", "red")
            input("Press Enter to exit...")
            sys.exit(1)


        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(message)s',
            handlers=[
                logging.FileHandler('pattern_counter.log'),
            ]
        )
        
        Scoreboard = ConfigParser()
        Scoreboard.read("./scoreboard.ini")
        
        # Initialize counters
        self.wins_count_lifetime = Scoreboard['Lifetime']['wins']
        self.losses_count_lifetime = Scoreboard['Lifetime']['losses']
        self.wins_count_CurrentSession = Scoreboard['CurrentSession']['wins']
        self.losses_count_CurrentSession = Scoreboard['CurrentSession']['losses']

    def get_cooldown_status(self):
        """Get remaining cooldown time and status."""
        if not self.last_detection_time:
            return 0, False

        elapsed = (datetime.now() - self.last_detection_time).total_seconds()
        remaining = max(0, self.cooldown_period - elapsed)

        if remaining > 0:
            return remaining, True
        return 0, False

    def print_colored(self, message, color):
        """Print colored message to terminal."""
        colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "blue": "\033[94m",
            "yellow": "\033[93m",
            "reset": "\033[0m"
        }
        print(f"{colors[color]}{message}{colors['reset']}")

    def load_counter(self, file_path):
        
        """Load counter from file or initialize to 0 if file doesn't exist."""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    print("Load Counter ended")
                    return int(f.read().strip())
            else:
                
                return 0
        except Exception as e:
            self.print_colored(f"Error loading counter from {file_path}: {e}", "red")
            return 0

    def capture_region(self):
        
        """Capture the specified screen region."""
        try:
            screenshot = pyautogui.screenshot(region=self.region)
            
            return screenshot
        except Exception as e:
            self.print_colored(f"Error capturing screen: {e}", "red")
            
            return None

    def process_image(self, image):
        
        """Process the image using OCR."""
        try:
            text = pytesseract.image_to_string(image, timeout=15)
            
            return text.strip().lower()
        except Exception as e:
            self.print_colored(f"Error processing image: {e}", "red")
            
            return ""
    
    def check_patterns(self, text):
        
        Scoreboard = ConfigParser()
        Scoreboard.read("./scoreboard.ini")

        
        """Check for patterns in text and update appropriate counter."""
        # Check if we're in cooldown
        remaining_cooldown, in_cooldown = self.get_cooldown_status()
        if in_cooldown:
            return None
        
        
        if "streak increased" in text:
            life = int(Scoreboard['Lifetime']['wins'])
            current = int(Scoreboard['CurrentSession']['wins'])
            streak = int(Scoreboard['CurrentSession']['streak'])
            
            life += 1
            current += 1
            streak += 1
            
            Scoreboard['Lifetime']['wins'] = str(life)
            Scoreboard['CurrentSession']['wins'] = str(current)
            Scoreboard['CurrentSession']['streak'] = str(streak)
            
            with open('scoreboard.ini', 'w') as configfile:
                Scoreboard.write(configfile)
                
            self.print_colored(f"\nWin detected! Total wins: {life}", "green")
            self.last_detection_time = datetime.now()
            return "win"

        elif "battle lost" in text:
            life = int(Scoreboard['Lifetime']['losses'])
            current = int(Scoreboard['CurrentSession']['losses'])
            
            
            life += 1
            current += 1
            
            Scoreboard['Lifetime']['losses'] = str(life)
            Scoreboard['CurrentSession']['losses'] = str(current)
            Scoreboard['CurrentSession']['streak'] = "0"
            
            with open('scoreboard.ini', 'w') as configfile:
                Scoreboard.write(configfile)
            
            
            self.print_colored(f"\nLoss detected! Total losses: {life}", "yellow")
            self.last_detection_time = datetime.now()
            
            return "loss"
        
        return None    

    def run(self):
        """Main monitoring loop."""
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal
        self.print_colored("=== Screen Pattern Monitor Started ===", "blue")
        self.print_colored(f"Monitoring region: {self.region}", "blue")
        self.print_colored(f"Current stats - Wins: {self.wins_count_CurrentSession}, Losses: {self.losses_count_CurrentSession}", "blue")
        self.print_colored(f"Cooldown period: {self.cooldown_period} seconds", "blue")
        self.print_colored("Press 'Q' to quit", "blue")
        self.print_colored("=" * 38, "blue")

        try:
            print("Run Self Started")
            while True:
                # Check for 'Q' key press
                if msvcrt.kbhit():
                    if msvcrt.getch().decode().lower() == 'q':
                        raise KeyboardInterrupt

                # Display cooldown status if active
                remaining_cooldown, in_cooldown = self.get_cooldown_status()
                if in_cooldown:
                    minutes = int(remaining_cooldown // 60)
                    seconds = int(remaining_cooldown % 60)
                    sys.stdout.write(f"\rCooldown active: {minutes:02d}:{seconds:02d} remaining  ")
                    sys.stdout.flush()
                else:
                    sys.stdout.write("\rMonitoring...                            \n")
                    sys.stdout.flush()

                # Capture and process screen region if not in cooldown
                if not in_cooldown:
                    screenshot = self.capture_region()
                    if screenshot:
                        text = self.process_image(screenshot)
                        self.check_patterns(text)

                # Wait before next check
                
                time.sleep(self.check_interval)
                

        except KeyboardInterrupt:
            self.print_colored("\nMonitoring stopped by user", "yellow")
            self.print_colored(f"Final stats - Wins: {self.wins_count}, Losses: {self.losses_count}", "yellow")
            input("\nPress Enter to exit...")
        except Exception as e:
            self.print_colored(f"Unexpected error: {e}", "red")
            input("\nPress Enter to exit...")


def main():
    
    Scoreboard = ConfigParser()
    Scoreboard.read("./scoreboard.ini")
    
    Scoreboard['CurrentSession']['losses'] = "0"
    Scoreboard['CurrentSession']['wins'] = "0"
    Scoreboard['CurrentSession']['streak'] = "0"
            
    with open('scoreboard.ini', 'w') as configfile:
        Scoreboard.write(configfile)
    
    #Load config.ini
    config = ConfigParser()
    config.read("./config.ini")
    
    
    tesseract_path = config['Settings']['Tesseract_Path']
    
    
    
    
    # Get screen dimensions
    screen_width, screen_height = pyautogui.size()

    # Calculate region for bottom center (400x100)
    region_width = 1000
    region_height = 200
    region_left = (screen_width - region_width) // 2
    region_top = screen_height - region_height  # 50px from bottom

    monitor_region = (region_left, region_top, region_width, region_height)

    # Create and run the monitor
    monitor = ScreenPatternCounter(
        region=monitor_region,
        tesseract_path=tesseract_path,
        check_interval=11.0, # 11 seconds interval, was 10
        cooldown_period=60  # 1 minute cooldown
    )

    monitor.run()


if __name__ == "__main__":
    main()