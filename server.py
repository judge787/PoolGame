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
p1Play = ""
p2Play = ""
lastTable = None

def setupTable():
    table = Physics.Table()

    positions = [
        (0, 675, 2025),  # cue ball
        (1, 675, 675),  # 1-ball
        (2, 646, 618),  # left second row
        (3, 705, 618),  # right
        (4, 617, 561),  # left
        (5, 675, 561),
        (6, 732, 561),  # middle
        (7, 588, 504),  # left
        (8, 646, 504),
        (9, 703, 504),  # middle
        (10, 760, 504),  # middle
        (11, 559, 447),  # left
        (12, 617, 447),
        (13, 674, 447),  # middle
        (14, 731, 447),  # middle
        (15, 788, 447)  # middle
    ]

    still_balls = [Physics.StillBall(num, Physics.Coordinate(x, y)) for num, x, y in positions]
    
    for sb in still_balls:
        table += sb  

    return table

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
            
            response = dict(parse_qsl(requestPath.query))
            id = int(response.get("id"))

            gameData = {
                "p1Play": p1Play,
                "p2Play": p2Play,
                "p1Name": gameInstance.player1Name,
                "p2Name": gameInstance.player2Name,
                "p1Score": scorePlayerOne,
                "p2Score": scorePlayerTwo,
                "svg": lastTable.svg(),
                "gameName": gameInstance.gameName
            }

            response = json.dumps(gameData)
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "application/json" );
            self.end_headers();

            # send it to the broswer
            self.wfile.write( bytes( response, "utf-8" ) );

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

        global gameInstance, lastTable, activePlayer  # Use global declarations for modifications
        
        if requestPath.path == '/start.html':
            # Processing form data to start a new game
            formData = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                        environ={'REQUEST_METHOD': 'POST',
                                                 'CONTENT_TYPE': self.headers['Content-Type']})

            playerOneName = formData.getvalue("firstPlayer")
            playerTwoName = formData.getvalue("secondPlayer")
            gameName = formData.getvalue("gameName")
            

            gameInstance = Physics.Game(gameName=gameName, player1Name=playerOneName, player2Name=playerTwoName)
            activePlayer = random.choice([playerOneName, playerTwoName])
            lastTable = setupTable()

            with open("start.html", "r") as file:
                html = file.read()
            
            html = html.replace("{id}", str(gameInstance.gameID))

            # generate the headers
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/html" );
            self.send_header( "Content-length", len( html ) );
            self.end_headers();

            # send it to the broswer
            self.wfile.write( bytes( html, "utf-8" ) );
            file.close();


        elif requestPath.path == '/executeShot':
            # Handle shot execution logic
            formData = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                        environ={'REQUEST_METHOD': 'POST',
                                                 'CONTENT_TYPE': self.headers['Content-Type']})
            gameID = int(formData.getvalue('id'));
            velocityX = float(formData.getvalue('velocityX'))
            velocityY = float(formData.getvalue('velocityY'))
            
            lastTable, tableList = gameInstance.shoot(gameInstance.gameName, activePlayer, lastTable, velocityX, velocityY)

            tableList = json.dumps(tableList)

            print("Called shoot")

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write( bytes( tableList, "utf-8" ) );

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
    server = HTTPServer(('0.0.0.0', int(sys.argv[1])), RequestHandler)
    # server = HTTPServer(('localhost', int(sys.argv[1])), RequestHandler)
    print("Server running on port:", sys.argv[1])
    server.serve_forever()

