# Sea-of-thieves-hourglass-win-loss-counter-
A program that reads if you win or loose a hourglass match in sot and then displays it in a easy way for a stream to see

HOW THIS WORKS

auto_installer.bat installs all dependencies

run the "Run.bat" script, when this script is run it runs the 2 other scripts in this file using run.py and make sure that the config and scoreboard ini files exist

script.py
	-Determines if a win or loss happens then updates scoreboard.ini

app.py
	-Small webapp that displays the information from "wins.txt" and "losses.txt", it does this using the in HTML file located in templates and the CSS file located in \static\styles
	-style.css can be updated to ones liking to display the information in any required format. an example background.png is also provided. user can adjust size of webpage in the css file
	
The information can be shown in any web browser, or in OBS Browser source at http://127.0.0.1:5000 (localhost:5000)

config.ini
	-application settings
	
scoreboard.ini
	-where the information for wins and losses are stored
