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
currentPlayer = 1  # 1 for player one, 2 for player two
player1Type = None  # Will be "solids" or "stripes" 
player2Type = None  # Will be "solids" or "stripes"
gameWinner = None  # Will store the winning player's name

def checkBallsPocketed(beforeTable, afterTable):
    """Check which balls were pocketed by comparing before and after tables"""
    beforeBalls = set()
    afterBalls = set()
    
    # Get ball numbers from before table
    for ball in beforeTable:
        if isinstance(ball, (Physics.StillBall, Physics.RollingBall)):
            if isinstance(ball, Physics.StillBall):
                beforeBalls.add(ball.obj.still_ball.number)
            else:
                beforeBalls.add(ball.obj.rolling_ball.number)
    
    # Get ball numbers from after table  
    for ball in afterTable:
        if isinstance(ball, (Physics.StillBall, Physics.RollingBall)):
            if isinstance(ball, Physics.StillBall):
                afterBalls.add(ball.obj.still_ball.number)
            else:
                afterBalls.add(ball.obj.rolling_ball.number)
    
    # Return balls that were pocketed (in before but not in after)
    return beforeBalls - afterBalls

def updatePlayerTypes(pocketedBalls):
    """Assign player types (solids/stripes) based on first ball pocketed"""
    global player1Type, player2Type, currentPlayer
    
    # Skip cue ball and 8-ball for type assignment
    validBalls = [ball for ball in pocketedBalls if ball != 0 and ball != 8]
    
    if validBalls and player1Type is None and player2Type is None:
        firstBall = validBalls[0]
        if 1 <= firstBall <= 7:  # Solid ball pocketed
            if currentPlayer == 1:
                player1Type = "solids"
                player2Type = "stripes"
            else:
                player1Type = "stripes" 
                player2Type = "solids"
        elif 9 <= firstBall <= 15:  # Stripe ball pocketed
            if currentPlayer == 1:
                player1Type = "stripes"
                player2Type = "solids"
            else:
                player1Type = "solids"
                player2Type = "stripes"

def updateScores(pocketedBalls):
    """Update player scores based on pocketed balls"""
    global scorePlayerOne, scorePlayerTwo, player1Type, player2Type
    
    for ball in pocketedBalls:
        if ball == 0:  # Cue ball - no points
            continue
        elif ball == 8:  # 8-ball - special handling needed
            continue
        elif 1 <= ball <= 7:  # Solid balls
            if player1Type == "solids":
                scorePlayerOne += 1
            elif player2Type == "solids":
                scorePlayerTwo += 1
        elif 9 <= ball <= 15:  # Stripe balls
            if player1Type == "stripes":
                scorePlayerOne += 1
            elif player2Type == "stripes":
                scorePlayerTwo += 1

def shouldSwitchTurns(pocketedBalls):
    """Determine if turn should switch based on game rules"""
    global currentPlayer, player1Type, player2Type
    
    # If cue ball was pocketed, switch turns (scratch)
    if 0 in pocketedBalls:
        return True
    
    # If no balls were pocketed, switch turns
    if not pocketedBalls or all(ball in [0, 8] for ball in pocketedBalls):
        return True
    
    # If player hasn't been assigned a type yet, don't switch if they pocketed a ball
    if player1Type is None and player2Type is None:
        return False
    
    # Check if player pocketed their own balls
    playerType = player1Type if currentPlayer == 1 else player2Type
    validBalls = [ball for ball in pocketedBalls if ball != 0 and ball != 8]
    
    if playerType == "solids":
        ownBalls = [ball for ball in validBalls if 1 <= ball <= 7]
    else:  # stripes
        ownBalls = [ball for ball in validBalls if 9 <= ball <= 15]
    
    # If they pocketed their own balls, they continue
    if ownBalls:
        return False
    
    # Otherwise, switch turns
    return True

def checkWinConditions(pocketedBalls):
    """Check for winning conditions and return winner if any"""
    global gameWinner, scorePlayerOne, scorePlayerTwo, player1Type, player2Type, currentPlayer, gameInstance
    
    currentPlayerName = gameInstance.player1Name if currentPlayer == 1 else gameInstance.player2Name
    opponentName = gameInstance.player2Name if currentPlayer == 1 else gameInstance.player1Name
    currentPlayerScore = scorePlayerOne if currentPlayer == 1 else scorePlayerTwo
    currentPlayerType = player1Type if currentPlayer == 1 else player2Type
    
    # Check if 8-ball was pocketed
    if 8 in pocketedBalls:
        # Player wins if they have all their balls (score = 7) and pocket the 8-ball
        if currentPlayerScore == 7:
            gameWinner = currentPlayerName
            return True
        else:
            # Player loses if they pocket 8-ball without having all their balls
            gameWinner = opponentName
            return True
    
    # Check if a player has pocketed all their balls (7 score)
    # Note: They still need to pocket the 8-ball to win
    if currentPlayerScore == 7:
        # Player has all their balls but hasn't won yet (needs 8-ball)
        return False
    
    # Check for scratch while shooting at 8-ball
    if 0 in pocketedBalls and currentPlayerScore == 7:
        # If player scratches while shooting at 8-ball, they lose
        gameWinner = opponentName
        return True
    
    return False

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
            
            # Determine current player name and status
            currentPlayerName = gameInstance.player1Name if currentPlayer == 1 else gameInstance.player2Name
            
            # Determine player statuses based on turn
            if currentPlayer == 1:
                p1Status = f"{gameInstance.player1Name}'s Turn"
                p2Status = ""
            else:
                p1Status = ""
                p2Status = f"{gameInstance.player2Name}'s Turn"

            gameData = {
                "p1Play": p1Status,
                "p2Play": p2Status,
                "p1Name": gameInstance.player1Name,
                "p2Name": gameInstance.player2Name,
                "p1Score": scorePlayerOne,
                "p2Score": scorePlayerTwo,
                "svg": lastTable.svg(),
                "gameName": gameInstance.gameName,
                "currentPlayer": currentPlayerName,
                "p1Type": player1Type or "Unassigned",
                "p2Type": player2Type or "Unassigned",
                "winner": gameWinner
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

        global gameInstance, lastTable, activePlayer, currentPlayer, scorePlayerOne, scorePlayerTwo, player1Type, player2Type  # Use global declarations for modifications
        
        if requestPath.path == '/start.html':
            # Processing form data to start a new game
            formData = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                        environ={'REQUEST_METHOD': 'POST',
                                                 'CONTENT_TYPE': self.headers['Content-Type']})

            playerOneName = formData.getvalue("firstPlayer")
            playerTwoName = formData.getvalue("secondPlayer")
            gameName = formData.getvalue("gameName")
            
            # Reset game state
            global currentPlayer, scorePlayerOne, scorePlayerTwo, player1Type, player2Type, gameWinner
            currentPlayer = 1  # Start with player 1
            scorePlayerOne = 0
            scorePlayerTwo = 0
            player1Type = None
            player2Type = None
            gameWinner = None

            gameInstance = Physics.Game(gameName=gameName, player1Name=playerOneName, player2Name=playerTwoName)
            activePlayer = playerOneName  # Start with player 1
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
            
            # Store the table state before the shot
            beforeTable = lastTable
            
            # Execute the shot
            currentPlayerName = gameInstance.player1Name if currentPlayer == 1 else gameInstance.player2Name
            lastTable, tableList = gameInstance.shoot(gameInstance.gameName, currentPlayerName, lastTable, velocityX, velocityY)
            
            # Check which balls were pocketed
            pocketedBalls = checkBallsPocketed(beforeTable, lastTable)
            
            # Update player types if this is the first ball pocketed
            updatePlayerTypes(pocketedBalls)
            
            # Update scores
            updateScores(pocketedBalls)
            
            # Check for winning conditions
            gameIsWon = checkWinConditions(pocketedBalls)
            
            # Only switch turns if the game hasn't been won
            if not gameIsWon and shouldSwitchTurns(pocketedBalls):
                currentPlayer = 2 if currentPlayer == 1 else 1
                activePlayer = gameInstance.player2Name if currentPlayer == 2 else gameInstance.player1Name

            tableList = json.dumps(tableList)

            print(f"Called shoot - Player {currentPlayer} ({currentPlayerName})")
            print(f"Balls pocketed: {pocketedBalls}")
            print(f"Score P1: {scorePlayerOne}, Score P2: {scorePlayerTwo}")
            print(f"Player types - P1: {player1Type}, P2: {player2Type}")

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

