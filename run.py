import subprocess
import signal
import sys
import configparser

def run_scripts_concurrently():
    try:
        # Start app.py and script.py as separate processes
        print("Starting monitor and web app")
        app = subprocess.Popen(["python", "app.py"])
        script = subprocess.Popen(["python", "script.py"])

        # Wait for both processes to complete
        app.wait()
        script.wait()

        print("Both scripts have completed.")
    
    except KeyboardInterrupt:
        print("\n Keyboard Interrupt. Terminating processes...")
        app.terminate()
        script.terminate()
        app.wait() 
        script.wait()

        print("Processes have been terminated.")
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure the script files exist and are in the correct directory.")

def create_config():
    # Create a ConfigParser object
    config = configparser.ConfigParser()
    
    config['Settings'] = {}
    config['Settings']['Tesseract_Path'] = "C:\Program Files\Tesseract-OCR\tesseract.exe"
    endscript = config['Settings']['End_Script'] = "`"
    config['Settings']['Add_Win'] = "5"
    config['Settings']['Add_Loss'] = "6"
    config['Settings']['Increase_Streak'] = "7"
    with open('config.ini', 'w') as configwr:
        config.write(configwr)
    return 0
    
    
def create_scoreboard():
    # Create a ConfigParser object
    scoreboard = configparser.ConfigParser()

    scoreboard['Lifetime'] = {}
    scoreboard['Lifetime']['wins'] = "0"
    scoreboard['Lifetime']['losses'] = "0"
    scoreboard['CurrentSession'] = {}
    scoreboard['CurrentSession']['wins'] = "0"
    scoreboard['CurrentSession']['losses'] = "0"
    scoreboard['CurrentSession']['streak'] = "0"

    # Write to the file
    with open('scoreboard.ini', 'w') as scoreboardwr:
        scoreboard.write(scoreboardwr)
    
    return 1


def check_scoreboard():
    scoreboard = configparser.ConfigParser()
    scoreboard.read("./scoreboard.ini")
    
    try:
        LifetimeWins = scoreboard['Lifetime']['wins']
        LifetimeLosses = scoreboard['Lifetime']['losses']
        CurrentWins = scoreboard['CurrentSession']['wins']
        CurrentLosses = scoreboard['CurrentSession']['losses']
        CurrentStreak = scoreboard['CurrentSession']['streak']
        
    except Exception as e:
        print("scoreboard.ini needs to be rebuilt")
        return 0
        
    print("scoreboard.ini check completed successfully")
    return 1
    

def check_config():
    config = configparser.ConfigParser()
    config.read("./config.ini")
    
    try:
        ConfigTesseractPath = config['Settings']['Tesseract_Path']
        endscript = config['Settings']['End_Script']
        addwin = config['Settings']['Add_Win']
        addloss = config['Settings']['Add_Loss']
        IncreaseStreak = config['Settings']['Increase_Streak']

        
    except Exception as e:
        print("config.ini needs to be rebuilt")
        create_config()
        return 0 
        
    print("config.ini check completed successfully")
    return 1

if __name__ == "__main__":
    check_config()
    check_scoreboard()
    run_scripts_concurrently()
