import sys  # For accessing command line arguments
import cgi  # For handling form data; consider 'multipart' for future use
import re
import os
import glob
import Physics  # Physics simulation library
import random
import math
import json
from urllib.parse import urlparse, parse_qsl

# Initialize game state variables
gameInstance = None
activePlayer = ""
scorePlayerOne = 0
scorePlayerTwo = 0
isPlayerTwoActive = ""
isPlayerOneActive = ""
lastGameTable = None

def setupTable():
    # Initializes the pool table with balls in their starting positions
    poolTable = Physics.Table()
    ballPositions = [
        # Cue ball and other balls' starting positions
        Physics.StillBall(0, Physics.Coordinate(675, 2025)),  # Cue ball
        
        # Triangular rack configuration
        Physics.StillBall(1, Physics.Coordinate(675, 675)),  # Front ball
        Physics.StillBall(2, Physics.Coordinate(646, 618)),  # Second row, left
        # ...add remaining ball positions here for brevity...
        Physics.StillBall(15, Physics.Coordinate(788, 447))  # Last row, rightmost
    ]
    for ball in ballPositions:
        poolTable += ball
    return poolTable

# Web server components
from http.server import HTTPServer, SimpleHTTPRequestHandler

class RequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        requestPath = urlparse(self.path)

        if requestPath.path in ['/signup.html']:
            # Serve the signup form
            with open('.' + requestPath.path) as file:
                htmlContent = file.read()
            
            self.send_response(200)  # HTTP OK
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(htmlContent))
            self.end_headers()
            self.wfile.write(bytes(htmlContent, "utf-8"))
        
        elif requestPath.path == '/gameStatus':
            # Send current game status as JSON
            gameStatus = {
                "activePlayerOne": isPlayerOneActive,
                "activePlayerTwo": isPlayerTwoActive,
                "namePlayerOne": gameInstance.player1Name,
                "namePlayerTwo": gameInstance.player2Name,
                "scorePlayerOne": scorePlayerOne,
                "scorePlayerTwo": scorePlayerTwo,
                "tableSVG": lastGameTable.svg(),
                "gameTitle": gameInstance.gameName
            }
            self.send_json_response(gameStatus)
        else:
            # Handle unknown paths
            self.send_error(404, f"Resource {self.path} not found.")

    def send_json_response(self, data):
        jsonResponse = json.dumps(data)
        self.send_response(200)  # HTTP OK
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(jsonResponse, "utf-8"))

    def do_POST(self):
        requestPath = urlparse(self.path)

        global gameInstance, lastGameTable, activePlayer  # Use global declarations for modifications
        
        if requestPath.path == '/startGame':
            # Processing form data to start a new game
            formData = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                        environ={'REQUEST_METHOD': 'POST',
                                                 'CONTENT_TYPE': self.headers['Content-Type']})

            playerOneName = formData.getvalue("player1_name")
            playerTwoName = formData.getvalue("player2_name")
            gameName = formData.getvalue("game_name")
            
            gameInstance = Physics.Game(gameName=gameName, player1Name=playerOneName, player2Name=playerTwoName)
            activePlayer = random.choice([playerOneName, playerTwoName])
            lastGameTable = setupTable()

            # Serve the game interface
            self.serve_html_file("gameInterface.html", gameInstance.gameID)

        elif requestPath.path == '/executeShot':
            # Handle shot execution logic
            formData = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                        environ={'REQUEST_METHOD': 'POST',
                                                 'CONTENT_TYPE': self.headers['Content-Type']})
            xVel = float(formData.getvalue('xVelocity'))
            yVel = float(formData.getvalue('yVelocity'))
            
            svgSequence, finalTable = gameInstance.shoot(gameName, activePlayer, lastGameTable, xVel, yVel)
            lastGameTable = finalTable

            self.send_json_response(svgSequence)

    def serve_html_file(self, fileName, gameId):
        # Method to serve HTML files with dynamic content
        with open(fileName, "r") as file:
            content = file.read().replace("{id}", str(gameId))

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", len(content))
        self.end_headers()
        self.wfile.write(bytes(content, "utf-8"))

if __name__ == "__main__":
    server = HTTPServer(('localhost', int(sys.argv[1])), RequestHandler)
    print("Server running on port:", sys.argv[1])
    server.serve_forever()
