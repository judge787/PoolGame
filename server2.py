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
    server = HTTPServer(('localhost', int(sys.argv[1])), RequestHandler)
    print("Server running on port:", sys.argv[1])
    server.serve_forever()


# import sys; # argv
# import cgi; # parse Mutlipart FormData 
# import os;
# import Physics;
# import math;
# import random
# import json

# # web server parts
# from http.server import HTTPServer, BaseHTTPRequestHandler;

# # used to parse the URL and extract form data for GET reqs
# from urllib.parse import urlparse, parse_qsl;

# # Dictionary to store active game instances
# active_games = {};

# # Function to get create a game instance
# def newGame(game_name, p1_name, p2_name):
#     # Create a new game instance
#     game_instance = Physics.Game(gameName=game_name, player1Name=p1_name, player2Name=p2_name);

#     # Get game ID generated for the new game instance
#     game_id = game_instance.gameID;

#     # Store the game instance in the active_games dictionary
#     active_games[game_id] = game_instance;

#     # Return the game instance
#     return game_instance;

# # Function to get a game instance
# def getGame(gameID):
#     # Check if the game instance with the given ID is already active
#     if gameID in active_games:
#         # If yes, return the existing game instance
#         return active_games[gameID];

#     return None;

# def updateGame(gameID):
#     # Check if the game instance with the given ID is active
#     if gameID in active_games:
#         # If yes, retrieve the game instance
#         game_instance = active_games[gameID];

#         # Call database.getGame to fetch the updated game data
#         game_data = game_instance.database.getGame(gameID);

#         if game_data is not None:
#             # Update the game instance data with the retrieved data
#             game_instance.currentPlayerID = game_data[1];
#             game_instance.gameStarted = game_data[2];
#             game_instance.gameOver = game_data[3];
#             game_instance.winner = game_data[4];
#             game_instance.winnerMessage = game_data[5];

#             # Player 1 data
#             game_instance.player1ID = game_data[6][0];
#             game_instance.player1Playing = game_data[6][2];
#             game_instance.player1Score = game_data[6][3];

#             # Player 2 data
#             game_instance.player2ID = game_data[7][0];
#             game_instance.player2Playing = game_data[7][2];
#             game_instance.player2Score = game_data[7][3];
            
#             return game_instance;
#     return None


# # Function to initialize a new table
# def initialize_table():
#     # Setup the table
#     table = Physics.Table();  # Create a new table

#     # Define the number of rows and balls per row
#     rows = 5;
#     balls_per_row = [1, 2, 3, 4, 5];
#     ball_count = [1, 2, 9, 3, 8, 10, 4, 14, 7, 11, 12, 6, 15, 13, 5];

#     # Loop through each row
#     for row in range(rows):
#         # Loop through each ball in the row
#         for ball_number in range(balls_per_row[row]):
#             # Calculate x-coordinate for current ball
#             x = Physics.TABLE_WIDTH / 2.0 + (ball_number - balls_per_row[row] / 2.0) * (Physics.BALL_DIAMETER + 4.0);
#             # Calculate y-coordinate for current ball
#             y = Physics.TABLE_WIDTH / 2.0 - math.sqrt(3.0) / 2.0 * (Physics.BALL_DIAMETER + 4.0) * row;
#             # Get ball count for current position
#             current_ball_count = ball_count.pop(0);
#             # Create pos coordinate
#             pos = Physics.Coordinate(x, y);
#             # Create the ball and add it to the table
#             sb = Physics.StillBall(current_ball_count, pos);
#             table += sb;

#     # Add cue ball
#     pos = Physics.Coordinate(Physics.TABLE_WIDTH / 2.0 + 2, Physics.TABLE_LENGTH - Physics.TABLE_WIDTH / 2.0);
#     sb = Physics.StillBall(0, pos);
#     table += sb;

#     return table;

# # handler for web-server - handles both GET and POST reqs
# class MyHandler( BaseHTTPRequestHandler ):
#     def do_GET(self):
#         # parse URL to path & form data
#         parsed  = urlparse( self.path );

#         # check if the web-pages matches the list
#         if parsed.path in [ '/setupGame.html' ]:
            
#             # check if path exists
#             if os.path.exists("." + parsed.path):
#                 # retreive game HTML file
#                 fp = open( '.'+self.path );
#                 content = fp.read();

#                 # generate the headers
#                 self.send_response( 200 ); # OK
#                 self.send_header( "Content-type", "text/html" );
#                 self.send_header( "Content-length", len( content ) );
#                 self.end_headers();

#                 # send it to the broswer
#                 self.wfile.write( bytes( content, "utf-8" ) );
#                 # close file
#                 fp.close();
#             else:
#                 # Invalid request
#                 self.send_response(500)
#                 self.end_headers()
#                 self.wfile.write(b"Error setting up setupGame.html")
        
#         elif parsed.path == '/animate':
#             # Parse query parameters
#             query_params = dict(parse_qsl(parsed.query))
#             game_id = int(query_params.get('game_id'));
#             # time = float(query_params.get('time'));

#             if game_id is not None: #and time is not None:
#                 game = Physics.Game(gameID=game_id);
#                 last_shot_id = game.database.getLastShotID(game.gameID);
#                 print(f"animate CALLED, game_id= {game_id}, last_shot_id= {last_shot_id}");
#                 # Generate SVG content
#                 # svg_content = game.database.getTableSVG(game.gameID, last_shot_id, time);
#                 svg_list = game.database.getShotSVGs(game.gameID, last_shot_id);

#                 # Create a dictionary to hold SVG data
#                 svg_data = {}
#                 for i, svg_content in enumerate(svg_list, start=1):
#                     key = f"svg{i}"
#                     svg_data[key] = svg_content

#                 # Convert dictionary to JSON
#                 json_response = json.dumps(svg_data)

#                 # Send response
#                 self.send_response(200)
#                 self.send_header("Content-type", "image/svg+xml")
#                 self.end_headers()
#                 self.wfile.write(json_response.encode('utf-8'))

#         elif parsed.path == '/updateGame':
#             # Parse query parameters
#             query_params = dict(parse_qsl(parsed.query))
            
#             # Extract the game ID from the form data
#             game_id = int(query_params.get('game_id'));
            
#             if game_id is not None:

#                 # Update the game instance on server side
#                 game = updateGame(game_id);

#                 last_shot_id = game.database.getLastShotID(game.gameID);
#                 first_table_id = game.database.getFirstTableID(game.gameID, last_shot_id);
#                 last_table_id = game.database.getLastTableID(game.gameID, last_shot_id);
#                 table = game.getNextTableForShot(first_table_id, last_table_id);

#                 # Generate game SVG
#                 svg = table.svg();

#                 current_player_name = game.player1Name if game.currentPlayerID == game.player1ID else game.player2Name;

#                 winner = "";

#                 if game.winner is not None:
#                     winner = game.player1Name if game.winner == game.player1ID else game.player2Name

#                 game_info = {
#                     "game_name": game.gameName,
#                     "game_over": game.gameOver,
#                     "game_winner": winner,
#                     "winner_message": game.winnerMessage,
#                     "p1_name": game.player1Name,
#                     "p1_playing": game.player1Playing if game.player1Playing else "",
#                     "p1_score": game.player1Score,
#                     "p2_name": game.player2Name,
#                     "p2_playing": game.player2Playing if game.player2Playing else "",
#                     "p2_score": game.player2Score,
#                     "current_player": current_player_name,
#                     "svg": svg  # Assuming you have SVG data here
#                 }
                
#                 # Serialize the game_info dictionary to JSON format
#                 response_json = json.dumps(game_info)
                
#                 # Send the JSON response back to the client
#                 self.send_response(200)
#                 self.send_header("Content-type", "application/json")
#                 self.end_headers()
#                 self.wfile.write(bytes(response_json, "utf-8"))
                
#         else:
#             # generate 404 for GET requests that aren't the 2 files above
#             self.send_response( 404 );
#             self.end_headers();
#             self.wfile.write( bytes( "404: %s not found" % self.path, "utf-8" ) );
    
#     def do_POST(self):

#         # handle post req
#         # parse URL to get path & form data
#         parsed  = urlparse( self.path );

#         if parsed.path in [ '/playGame.html' ]:

#             # get data send as Multipart FormData (MIME format)
#             form = cgi.FieldStorage( fp=self.rfile,
#                                      headers=self.headers,
#                                      environ = { 'REQUEST_METHOD': 'POST',
#                                                  'CONTENT_TYPE': 
#                                                    self.headers['Content-Type'],
#                                                } 
#                                    );
#             # extract form data
#             game_name = form.getvalue('game_name');
#             p1_name = form.getvalue('player1_name');
#             p2_name = form.getvalue('player2_name');

#             try:
#                 # Create a new game instance
#                 game = newGame(game_name, p1_name, p2_name);
                
#                 # Create game setup
#                 table = initialize_table();
#                 svg = table.svg();

#                 current_player_name = game.player1Name if game.currentPlayerID == game.player1ID else game.player2Name;

#                 # Generate HTML response
#                 with open("playGame.html", "r") as f:
#                     response = f.read()
#                 response = response.replace("{game_id}", str(game.gameID));
#                 response = response.replace("{game_name}", game.gameName);
#                 response = response.replace("{p1_name}", game.player1Name);
#                 response = response.replace("{p2_name}", game.player2Name);
#                 response = response.replace("{current_player}", current_player_name);
#                 response = response.replace("{p1_score}", str(game.player1Score));
#                 response = response.replace("{p2_score}", str(game.player2Score));
#                 response = response.replace("{svg}", svg);

#                 # Generate the headers
#                 self.send_response( 200 ); # OK
#                 self.send_header( "Content-type", "text/html" );
#                 self.end_headers();

#                 # Send the HTML response to the browser
#                 self.wfile.write( bytes(response, "utf-8" ) );
            
#             except Exception as e:

#                 # Handle any exceptions that occur during game initialization
#                 error_response = f"<h1>Error occurred: {str(e)}</h1>"
#                 self.send_response(500)  # Internal Server Error
#                 self.send_header("Content-type", "text/html")
#                 self.send_header("Content-length", len(error_response))
#                 self.end_headers()
#                 self.wfile.write(bytes(error_response, "utf-8"))
        
#         elif parsed.path == '/shoot':
#             form = cgi.FieldStorage(fp=self.rfile,
#                                      headers=self.headers,
#                                      environ={'REQUEST_METHOD': 'POST',
#                                               'CONTENT_TYPE':
#                                                   self.headers['Content-Type'],
#                                               }
#                                      )

#             # Extract necessary data from form_data
#             game_id = int(form.getvalue('game_id'));
#             rb_vel_x = float(form.getvalue('x_vel'));
#             rb_vel_y = float(form.getvalue('y_vel'));
#             print(f"New Shot! rb_vel_x = {rb_vel_x}, rb_vel_y = {rb_vel_y}, game_id = {game_id}")
            
#             try:
#                 # Get the game
#                 game = getGame(game_id);
                
#                 if (int(game.gameStarted) == 0):
#                     # Create game setup
#                     table = initialize_table();
#                     print(f"IF")
#                 else:
#                     last_shot_id = game.database.getLastShotID(game.gameID);
#                     first_table_id = game.database.getFirstTableID(game.gameID, last_shot_id)
#                     last_table_id = game.database.getLastTableID(game.gameID, last_shot_id);
#                     table = game.getNextTableForShot(first_table_id, last_table_id);
#                     print(f"ELSE gameID={game.gameID}, last_shot_id={last_shot_id}, first_table_id={first_table_id}, last_table_id={last_table_id}")

#                 # Shoot and store SVGs
#                 svg_list = game.shoot(game.gameName, game.gameID, game.gameStarted, 
#                                              game.currentPlayerID, game.player1ID, game.player2ID, 
#                                              table, rb_vel_x, rb_vel_y);
                
#                 # send an array 
#                 json_response = json.dumps(svg_list)

#                 # Send response
#                 self.send_response(200)
#                 self.send_header("Content-type", "application/json")
#                 #self.send_header("Content-Length", len(json_response))
#                 self.end_headers()
#                 self.wfile.write(json_response.encode('utf-8'))
#                 # self.wfile.write(bytes(json_response, "utf-8"))

#             except Exception as e:
#                 # Handle any errors
#                 self.send_response(500)
#                 self.end_headers()
#                 self.wfile.write(bytes(str(e), "utf-8"))
#         else:
#             # generate 404 for POST requests that aren't the file above
#             self.send_response( 404 );
#             self.end_headers();
#             self.wfile.write( bytes( "404: %s not found" % self.path, "utf-8" ) );


# if __name__ == "__main__":
#     httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler );
#     print( "Server listing in port:  ", int(sys.argv[1]) );
#     httpd.serve_forever();