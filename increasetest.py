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


def main():
    # Load config.ini
    config = ConfigParser()
    Scoreboard = ConfigParser()
    config.read("./config.ini")
    Scoreboard.read("./scoreboard.ini")

    wins_file = config['Settings']['Wins_File']
    losses_file = config['Settings']['Losses_File']
    tesseract_path = config['Settings']['Tesseract_Path']

    # Get values and convert them to integers
    wins_db_life = int(Scoreboard['Lifetime']['Wins'])
    wins_db_current = int(Scoreboard['CurrentSession']['Wins'])

    print("Current session wins =", wins_db_current)
    print("Lifetime wins =", wins_db_life)

    print("Increasing wins...")

    # Increment values
    wins_db_life += 1
    wins_db_current += 1

    print("Current session wins =", wins_db_current)
    print("Lifetime wins =", wins_db_life)

    # Save updated values back to Scoreboard
    Scoreboard['Lifetime']['Wins'] = str(wins_db_life)
    Scoreboard['CurrentSession']['Wins'] = str(wins_db_current)

    # Write changes to file
    with open('scoreboard.ini', 'w') as configfile:
        Scoreboard.write(configfile)

    print("File saved")
    print("Current session wins =", wins_db_current)
    print("Lifetime wins =", wins_db_life)

if __name__ == "__main__":
    main()