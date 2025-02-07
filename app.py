from flask import Flask, render_template, jsonify
import time
from configparser import ConfigParser
import signal
import sys

app = Flask(__name__)

# Load config.ini
config = ConfigParser()
config.read("./config.ini")




@app.route('/')
def home():
    return render_template('index.html')


@app.route('/get_number')
def get_number():
    Scoreboard = ConfigParser()
    Scoreboard.read("./scoreboard.ini")
    
    winslife = int(Scoreboard['Lifetime']['wins'])
    winscurrent = int(Scoreboard['CurrentSession']['wins'])
    losseslife = int(Scoreboard['Lifetime']['losses'])
    lossescurrent = int(Scoreboard['CurrentSession']['losses'])
    streakcurrent = int(Scoreboard['CurrentSession']['streak'])
    
    return jsonify(winslife=winslife, losseslife=losseslife, winscurrent=winscurrent, lossescurrent=lossescurrent, streakcurrent=streakcurrent)


def handle_keyboard_interrupt(signal, frame):
    print("\nReceived Keyboard Interrupt. Shutting down the Flask server...")
    sys.exit(0)


if __name__ == '__main__':
    # Setup signal handler for keyboard interrupt (Ctrl+C)
    signal.signal(signal.SIGINT, handle_keyboard_interrupt)

    app.run(debug=False)
