import phylib;
import sqlite3
import os
import math


################################################################################
# import constants from phylib to global varaibles
BALL_RADIUS   = phylib.PHYLIB_BALL_RADIUS;
BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER;

# add more here
HOLE_RADIUS = phylib.PHYLIB_HOLE_RADIUS;
TABLE_LENGTH = phylib.PHYLIB_TABLE_LENGTH;
TABLE_WIDTH = phylib.PHYLIB_TABLE_WIDTH;
SIM_RATE = phylib.PHYLIB_SIM_RATE;
VEL_EPSILON = phylib.PHYLIB_VEL_EPSILON;
DRAG = phylib.PHYLIB_DRAG;
MAX_TIME = phylib.PHYLIB_MAX_TIME;
MAX_OBJECTS = phylib.PHYLIB_MAX_OBJECTS;

#a3
FRAME_INTERVAL = 0.01


HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg id="gameSVG" width="700" height="1375" viewBox="-25 -25 1400 2750"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">
<rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />""";
FOOTER = """</svg>\n""";


################################################################################
# the standard colours of pool balls
# if you are curious check this out:  
# https://billiards.colostate.edu/faq/ball/colors/

BALL_COLOURS = [ 
    "WHITE",
    "YELLOW",
    "BLUE",
    "RED",
    "PURPLE",
    "ORANGE",
    "GREEN",
    "BROWN",
    "BLACK",
    "LIGHTYELLOW",
    "LIGHTBLUE",
    "PINK",             # no LIGHTRED
    "MEDIUMPURPLE",     # no LIGHTPURPLE
    "LIGHTSALMON",      # no LIGHTORANGE
    "LIGHTGREEN",
    "SANDYBROWN",       # no LIGHTBROWN 
    ];

################################################################################
class Coordinate( phylib.phylib_coord ):
    """
    This creates a Coordinate subclass, that adds nothing new, but looks
    more like a nice Python class.
    """
    pass;


################################################################################
class StillBall( phylib.phylib_object ):
    """
    Python StillBall class.
    """

    def __init__( self, number, pos ):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_STILL_BALL, 
                                       number, 
                                       pos, None, None, 
                                       0.0, 0.0 );
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = StillBall;


    def svg(self):
        return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.still_ball.pos.x , self.obj.still_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.still_ball.number])
    # add an svg method here


################################################################################
class RollingBall( phylib.phylib_object ):
    """
    Python RollingBall class.
    """

    def __init__( self, number, pos, vel, acc ):
        """
        Constructor function. Requires ball number, position (x,y) and velocity
        (vx,vy) as arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_ROLLING_BALL, 
                                       number, 
                                       pos, vel, acc, 
                                       0.0, 0.0 );
      
        # this converts the phylib_object into a RollingBall class
        self.__class__ = RollingBall;

    def svg(self):
        return """  <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.rolling_ball.pos.x , self.obj.rolling_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.rolling_ball.number])

################################################################################
class Hole( phylib.phylib_object ):
    """
    Python Hole class.
    """

    def __init__( self, number, pos ):
        """
        Constructor function. Requires hole number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_HOLE, 
                                       None, 
                                       pos, None, None, 
                                       0.0, 0.0 );
      
        # this converts the phylib_object into a Hole class
        self.__class__ = Hole;

    def svg(self):
        return """ <circle cx="%d" cy="%d" r="%d" fill="black" />\n""" % (self.obj.hole.pos.x , self.obj.hole.pos.y, HOLE_RADIUS)

################################################################################
class HCushion( phylib.phylib_object ):
    """
    Python HCushion class.
    """

    def __init__( self, pos ):
        """
        Constructor function. Requires position (x,y) as arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_HCUSHION, 
                                       None, 
                                       pos, None, None, 
                                       0.0, 0.0 );
      
        # this converts the phylib_object into a HCushion class
        self.__class__ = HCushion;

    def svg(self):
        y_coordinate = -25 if self.obj.hcushion.y == 0 else 2700
        svg_str = f"<rect width='1400' height='25' x='-25' y='{y_coordinate}' style='fill:darkgreen;' />\n"
        return svg_str
################################################################################
class VCushion( phylib.phylib_object ):
    """
    Python VCushion class.
    """

    def __init__( self, pos ):
        """
        Constructor function. Requires position (x,y) as arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__( self, 
                                       phylib.PHYLIB_VCUSHION, 
                                       None, 
                                       pos, None, None, 
                                       0.0, 0.0 );
      
        # this converts the phylib_object into a VCushion class
        self.__class__ = VCushion;

    def svg(self):
        x_coordinate = -25 if self.obj.vcushion.x == 0 else 1350
        svg_str = f"<rect width='25' height='2700' x='{x_coordinate}' y='-25' style='fill:darkgreen;' />\n"
        return svg_str


################################################################################


class Table( phylib.phylib_table ):
    """
    Pool table class.
    """

    def __init__( self ):
        """
        Table constructor method.
        This method call the phylib_table constructor and sets the current
        object index to -1.
        """
        phylib.phylib_table.__init__( self );
        self.current = -1;

    def __iadd__( self, other ):
        """
        += operator overloading method.
        This method allows you to write "table+=object" to add another object
        to the table.
        """
        self.add_object( other );
        return self;

    def __iter__( self ):
        """
        This method adds iterator support for the table.
        This allows you to write "for object in table:" to loop over all
        the objects in the table.
        """
        self.current = -1;
        return self;

    def __next__( self ):
        """
        This provides the next object from the table in a loop.
        """
        self.current += 1;  # increment the index to the next object
        if self.current < MAX_OBJECTS:   # check if there are no more objects
            return self[ self.current ]; # return the latest object

        # if we get there then we have gone through all the objects
        self.current = -1;    # reset the index counter
        raise StopIteration;  # raise StopIteration to tell for loop to stop

    def __getitem__( self, index ):
        """
        This method adds item retreivel support using square brackets [ ] .
        It calls get_object (see phylib.i) to retreive a generic phylib_object
        and then sets the __class__ attribute to make the class match
        the object type.
        """
        result = self.get_object( index ); 
        if result==None:
            return None;
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall;
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall;
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole;
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion;
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion;
        return result;

    def __str__( self ):
        """
        Returns a string representation of the table that matches
        the phylib_print_table function from A1Test1.c.
        """
        result = "";    # create empty string
        result += "time = %6.1f;\n" % self.time;    # append time
        for i,obj in enumerate(self): # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i,obj);  # append object description
        return result;  # return the string

    def segment( self ):
        """
        Calls the segment method from phylib.i (which calls the phylib_segment
        functions in phylib.c.
        Sets the __class__ of the returned phylib_table object to Table
        to make it a Table object.
        """

        result = phylib.phylib_table.segment( self );
        if result:
            result.__class__ = Table;
            result.current = -1;
        return result;


    def svg(self):
        # Initialize SVG content with the header.
        svg_elements = [HEADER]

        # Add SVG representation of each item if it's not None.
        for item in self:
            if item is not None:
                svg_elements.append(item.svg())

        # Add the footer at the end of the SVG content.
        svg_elements.append(FOOTER)

        # Combine all the SVG elements into a single string.
        return ''.join(svg_elements)



        # add svg method here


    def roll(self, t):
        new = Table()
        for ball in self:
            if isinstance(ball, RollingBall):
                # create a new ball with the same number as the old ball
                new_ball = RollingBall(ball.obj.rolling_ball.number,
                                    Coordinate(0, 0),
                                    Coordinate(0, 0),
                                    Coordinate(0, 0))
                # compute where it rolls to
                phylib.phylib_roll(new_ball, ball, t)
                # add ball to table
                new += new_ball

            if isinstance(ball, StillBall):
                # create a new ball with the same number and pos as the old ball
                new_ball = StillBall(ball.obj.still_ball.number,
                                    Coordinate(ball.obj.still_ball.pos.x, ball.obj.still_ball.pos.y))
                # add ball to table
                new += new_ball

        # return table
        return new

#***********************************************************************************

    def cueBall(self, vel_x, vel_y):
        """
        Set velocities for the cue ball and calculate its acceleration due to drag.
        """
        
        # Locate the cue ball among potentially stationary balls
        cueBallFound = next((b for b in self if isinstance(b, StillBall) and b.obj.still_ball.number == 0), None)
        
        if cueBallFound:
            # Capture starting coordinates
            startX, startY = cueBallFound.obj.still_ball.pos.x, cueBallFound.obj.still_ball.pos.y
            
            # Switch state to indicate motion
            cueBallFound.type = phylib.PHYLIB_ROLLING_BALL
            
            # Determine accelerations based on drag and input velocities
            speed = math.sqrt(vel_x**2 + vel_y**2)
            accelX = (-vel_x * DRAG / speed if speed > VEL_EPSILON and vel_x != 0 else 0.0)
            accelY = (-vel_y * DRAG / speed if speed > VEL_EPSILON and vel_y != 0 else 0.0)
            
            # Apply updates to reflect movement
            cueBallFound.obj.rolling_ball.pos.x, cueBallFound.obj.rolling_ball.pos.y = startX, startY
            cueBallFound.obj.rolling_ball.vel.x, cueBallFound.obj.rolling_ball.vel.y = vel_x, vel_y
            cueBallFound.obj.rolling_ball.acc.x, cueBallFound.obj.rolling_ball.acc.y = accelX, accelY
            cueBallFound.obj.rolling_ball.number = 0


#***********************************************************************************
class Database:
    def __init__(self, reset=False):
        self.db_path = "phylib.db"
        if reset and os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.conn = sqlite3.connect(self.db_path)


    def createDB(self):
        cursor = self.conn.cursor()
        # Create Ball table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Ball (
                BALLID INTEGER PRIMARY KEY AUTOINCREMENT,
                BALLNO INTEGER NOT NULL,
                XPOS FLOAT NOT NULL,
                YPOS FLOAT NOT NULL,
                XVEL FLOAT,
                YVEL FLOAT
            )
        ''')
        # Create TTable
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS TTable (
                TABLEID INTEGER PRIMARY KEY AUTOINCREMENT,
                TIME FLOAT NOT NULL
            )
        ''')
        # Create BallTable #maybe delete the third line primary key
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS BallTable (
                BALLID INTEGER NOT NULL,
                TABLEID INTEGER NOT NULL,
                FOREIGN KEY (BALLID) REFERENCES Ball(BALLID),
                FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID)
            )
        ''')
        # Create Shot
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Shot (
                SHOTID INTEGER PRIMARY KEY AUTOINCREMENT,
                PLAYERID INTEGER NOT NULL,
                GAMEID INTEGER NOT NULL,
                FOREIGN KEY (PLAYERID) REFERENCES Player(PLAYERID),
                FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID)
            )
        ''')
        # Create TableShot
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS TableShot (
                TABLEID INTEGER NOT NULL,
                SHOTID INTEGER NOT NULL,
                FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID),
                FOREIGN KEY (SHOTID) REFERENCES Shot(SHOTID)
            )
        ''')
        # Create Game
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Game (
                GAMEID INTEGER PRIMARY KEY AUTOINCREMENT,
                GAMENAME VARCHAR(64) NOT NULL
            )
        ''')
        # Create Player
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Player (
                PLAYERID INTEGER PRIMARY KEY AUTOINCREMENT,
                GAMEID INTEGER NOT NULL,
                PLAYERNAME VARCHAR(64) NOT NULL,
                FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID)
            )
        ''')
        # Commit changes and close cursor
        self.conn.commit()
        cursor.close()


    #***********************************************************************************

    def readTable(self, tableID):
        cursor = self.conn.cursor()
        adjusted_tableID = tableID + 1
        rows = cursor.execute('''
            SELECT Ball.*, TTable.TIME
            FROM Ball 
            JOIN BallTable ON Ball.BALLID = BallTable.BALLID 
            JOIN TTable ON BallTable.TABLEID = TTable.TABLEID
            WHERE BallTable.TABLEID = ?
        ''', (adjusted_tableID,)).fetchall()
        
        if not rows:
            return None
        
        table = Table()
        for row in rows:
            ball_id, ball_no, xpos, ypos, xvel, yvel, time = row
            
            pos = Coordinate(float(xpos), float(ypos))
            
            if xvel is not None and yvel is not None:
                speed = math.sqrt(xvel**2 + yvel**2)
                accx = accy = 0.0
                if speed > VEL_EPSILON:
                    accx = (-xvel / speed) * DRAG
                    accy = (-yvel / speed) * DRAG
                vel = Coordinate(float(xvel), float(yvel))
                acc = Coordinate(accx, accy)
                ball = RollingBall(int(ball_no), pos, vel, acc)
            else:
                ball = StillBall(int(ball_no), pos)
            
            table += ball
        
        table.time = time
        cursor.close()
        return table


    #***********************************************************************************
    

    def writeTable(self, gameTable):
        # Initiating communication with the database
        cursor = self.conn.cursor()

        # Recording the current state of the game table
        cursor.execute("INSERT INTO TTable (TIME) VALUES (?)", (gameTable.time,))
        idOfTable = cursor.lastrowid  # Acquiring the ID for the newly inserted table record

        # Processing each ball associated with the game table
        for ball in gameTable:
            # Ensuring ball is of type RollingBall or StillBall
            if isinstance(ball, (RollingBall, StillBall)):
                # Determining ball specifics for database entry
                ballSpecs = (
                    ball.obj.rolling_ball.number if isinstance(ball, RollingBall) else ball.obj.still_ball.number,
                    ball.obj.rolling_ball.pos.x if isinstance(ball, RollingBall) else ball.obj.still_ball.pos.x,
                    ball.obj.rolling_ball.pos.y if isinstance(ball, RollingBall) else ball.obj.still_ball.pos.y,
                    ball.obj.rolling_ball.vel.x if isinstance(ball, RollingBall) else None,
                    ball.obj.rolling_ball.vel.y if isinstance(ball, RollingBall) else None,
                )
                # Inserting ball data into the Ball database
                cursor.execute("INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) VALUES (?, ?, ?, ?, ?)", ballSpecs)
                idOfBall = cursor.lastrowid  # Retrieving the ID for the ball

                # Associating the ball with its respective table
                cursor.execute("INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)", (idOfBall, idOfTable))

        # Committing the transaction to the database and concluding the operation
        self.conn.commit()
        cursor.close()

        # Adjusting for the returned table ID to be compatible with zero-based indexing
        return idOfTable - 1

    

   #***********************************************************************************

    def getGame(self, gameIdentifier):
        # Initialize the database cursor for query execution
        gameCursor = self.conn.cursor()

        # Query to gather game and associated players' information
        queryResult = gameCursor.execute("""SELECT GAMEID, GAMENAME, PLAYERNAME
                                            FROM Game
                                            JOIN Player ON Game.GAMEID = Player.GAMEID
                                            WHERE Game.GAMEID = ?
                                            ORDER BY PLAYERID""", (gameIdentifier + 1,)).fetchall()

        # If no matching game is found, close the cursor and return None
        if not queryResult:
            gameCursor.close()
            return None

        # Extracting game name and initializing a list with it
        gameInfo = [queryResult[0][1]]

        # Appending player names to the list
        for entry in queryResult:
            gameInfo.append(entry[2])

        # Closing the cursor after commiting any pending transaction
        gameCursor.close()

        # Returning the composite list containing game name followed by player names
        return gameInfo

    #***********************************************************************************
    
    def setGame(self, game):
        # Establish database interaction
        db_cursor = self.conn.cursor()

        # Insert the game's name into the 'Game' table and retrieve the game ID
        db_cursor.execute("INSERT INTO Game (GAMENAME) VALUES (?)", (game.gameName,))
        game_id = db_cursor.lastrowid

        # Organize player names for batch insertion into 'Player' table
        players = [(game_id, game.player1Name), (game_id, game.player2Name)]
        db_cursor.executemany("INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?)", players)

        # Commit the transaction to the database and close the cursor
        self.conn.commit()
        db_cursor.close()

        # Return the game ID, adjusted by subtracting one
        return game_id - 1


    #***********************************************************************************

    def getPlayerID(self, playerName):
        cursor = self.conn.cursor()
        player_id_query = cursor.execute("SELECT PLAYERID FROM Player WHERE PLAYERNAME = ?", (playerName,)).fetchone()
        cursor.close()

        if player_id_query:
            return player_id_query[0] - 1
        return None

    #***********************************************************************************

    def newShot(self, gameID, playerID):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO Shot (PLAYERID, GAMEID) VALUES (?, ?)", (playerID + 1, gameID + 1,))
        shot_id = cursor.lastrowid
        cursor.close()

        return shot_id - 1

    #***********************************************************************************

    def newTableShot(self, tableID, shotID):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO TableShot (TABLEID, SHOTID)
            SELECT ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM TableShot WHERE TABLEID = ? AND SHOTID = ?
            )
        """, (tableID + 1, shotID + 1, tableID + 1, shotID + 1))
        cursor.close()

    def gameExists(self, gameName):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM Game WHERE GAMENAME = ?", (gameName,))
        game_exists = cursor.fetchone()
        cursor.close()
        return bool(game_exists)

    def linkTableShot(self, tableID, shotID):
        cursor = self.conn.cursor()
        # This query checks if the combination of tableID and shotID already exists to avoid duplicates.
        cursor.execute("""
            INSERT INTO TableShot (TABLEID, SHOTID)
            SELECT ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM TableShot WHERE TABLEID = ? AND SHOTID = ?
            )
        """, (tableID + 1, shotID + 1, tableID + 1, shotID + 1))
        self.conn.commit()
        cursor.close()


    #***********************************************************************************

    def close(self):
        self.conn.commit();
        self.conn.close();

################################################################################

class Game:
    def __init__(self, gameID=None, gameName=None, player1Name=None, player2Name=None):
        """
        Initializes a Game instance either by loading an existing game using its ID
        or by creating a new game with provided names. Validates the provided arguments
        to determine the action.
        """
        # Initialize database connection and establish a cursor
        self.database = Database()
        self.database.createDB()
        self.cursor = self.database.conn.cursor()

        # Scenario: Load existing game by ID
        if gameID is not None and not any([gameName, player1Name, player2Name]):
            game_data = self.database.getGame(gameID)
            if game_data:
                self.gameID, self.gameName, self.player1Name, self.player2Name = gameID, game_data[0], game_data[1], game_data[2]
            else:
                raise ValueError("Game does not exist")
        
        # Scenario: Create new game with provided names
        elif all([gameName, player1Name, player2Name]) and gameID is None:
            self.gameName = gameName
            self.player1Name = player1Name
            self.player2Name = player2Name
            # Insert new game into the database and store its ID
            self.gameID = self.database.setGame(self)
        
        else:
            # Handle invalid constructor usage
            raise TypeError("Invalid combination of arguments for Game constructor")


    #***********************************************************************************

    def shoot(self, gameName, playerName, table, xvel, yvel):
        if not self.database.gameExists(gameName):
            raise ValueError(f"Game with name {gameName} does not exist.")
        
        playerID = self.database.getPlayerID(playerName)
        if playerID is None:
            raise ValueError(f"No player found with name: {playerName}")
        
        shotID = self.database.newShot(self.gameID, playerID)
        table.cueBall(xvel, yvel)  # Initialize cue ball velocity

        finalSegment, svgTables = self.processTableSegment(table, shotID)
        return finalSegment, svgTables

    #***********************************************************************************
    
    def processTableSegment(self, table, shotID):
        svgTables = []
        while table:
            nextSegment = table.segment()
            if not nextSegment:
                return table, svgTables

            framesCount = int((nextSegment.time - table.time) / FRAME_INTERVAL)
            for frame in range(1, framesCount + 1):
                frameTimestamp = frame * FRAME_INTERVAL
                updatedTable = table.roll(frameTimestamp)
                updatedTableID = self.database.writeTable(updatedTable)
                self.database.linkTableShot(updatedTableID, shotID)
                svgTables.append(updatedTable.svg())

            table = nextSegment
        return None, svgTables










# OTHER PORTION 



# import phylib;
# import os;
# import sqlite3;
# import math;

# ################################################################################
# # import constants from phylib to global varaibles
# BALL_RADIUS   = phylib.PHYLIB_BALL_RADIUS;

# BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER;
# HOLE_RADIUS   = phylib.PHYLIB_HOLE_RADIUS;
# TABLE_LENGTH  = phylib.PHYLIB_TABLE_LENGTH;
# TABLE_WIDTH   = phylib.PHYLIB_TABLE_WIDTH;
# SIM_RATE      = phylib.PHYLIB_SIM_RATE;
# VEL_EPSILON   = phylib.PHYLIB_VEL_EPSILON;
# DRAG          = phylib.PHYLIB_DRAG;
# MAX_TIME      = phylib.PHYLIB_MAX_TIME;
# MAX_OBJECTS   = phylib.PHYLIB_MAX_OBJECTS;

# FRAME_INTERVAL = 0.01;

# # Define the following constants for SVG
# HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?> <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
# "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd"> <svg width="700" height="1375" viewBox="-25 -25 1400 2750"
# xmlns="http://www.w3.org/2000/svg"
# xmlns:xlink="http://www.w3.org/1999/xlink">
# <rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />""";
# FOOTER = """</svg>\n""";

# ################################################################################
# # the standard colours of pool balls
# # if you are curious check this out:  
# # https://billiards.colostate.edu/faq/ball/colors/

# BALL_COLOURS = [ 
#     "WHITE",
#     "YELLOW",
#     "BLUE",
#     "RED",
#     "PURPLE",
#     "ORANGE",
#     "GREEN",
#     "BROWN",
#     "BLACK",
#     "LIGHTYELLOW",
#     "LIGHTBLUE",
#     "PINK",             # no LIGHTRED
#     "MEDIUMPURPLE",     # no LIGHTPURPLE
#     "LIGHTSALMON",      # no LIGHTORANGE
#     "LIGHTGREEN",
#     "SANDYBROWN",       # no LIGHTBROWN 
#     ];

# # Helper method to calculate acceleration
# def calculateAcceleration( vel_x, vel_y ):

#     rb_speed = math.sqrt( float(vel_x)**2 + float(vel_y)**2 );
    
#     rb_acc_x = 0.0;
#     rb_acc_y = 0.0;

#     if rb_speed > VEL_EPSILON:
#         if (vel_x != 0.0):
#             rb_acc_x = -float(vel_x) * DRAG / rb_speed;
#         if (vel_y != 0.0):
#             rb_acc_y = -float(vel_y) * DRAG / rb_speed;

#     return Coordinate( float(rb_acc_x), float(rb_acc_y) );

# ################################################################################
# class Coordinate( phylib.phylib_coord ):
#     """
#     This creates a Coordinate subclass, that adds nothing new, but looks
#     more like a nice Python class.
#     """
#     pass;


# ################################################################################
# class StillBall( phylib.phylib_object ):
#     """
#     Python StillBall class.
#     """

#     def __init__( self, number, pos ):
#         """
#         Constructor function. Requires ball number and position (x,y) as
#         arguments.
#         """

#         # this creates a generic phylib_object
#         phylib.phylib_object.__init__( self, 
#                                        phylib.PHYLIB_STILL_BALL, 
#                                        number, 
#                                        pos, None, None, 
#                                        0.0, 0.0 );
      
#         # this converts the phylib_object into a StillBall class
#         self.__class__ = StillBall;


#     def svg( self ):
#         return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % ( self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.still_ball.number] );


# ################################################################################
# class RollingBall( phylib.phylib_object ):
#     """
#     Python RollingBall class.
#     """

#     def __init__( self, number, pos, vel, acc ):
#         """
#         Constructor function. Requires ball number, position (x, y), velocity (x, y),
#         and acceleration (x, y) as arguments.
#         """

#         # this creates a generic phylib_object
#         phylib.phylib_object.__init__( self, 
#                                        phylib.PHYLIB_ROLLING_BALL, 
#                                        number, 
#                                        pos, vel, acc, 
#                                        0.0, 0.0 );
      
#         # this converts the phylib_object into a RollingBall class
#         self.__class__ = RollingBall;


#     def svg( self ):
#         return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % ( self.obj.rolling_ball.pos.x, self.obj.rolling_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.rolling_ball.number] );


# ################################################################################
# class Hole( phylib.phylib_object ):
#     """
#     Python Hole class.
#     """

#     def __init__( self, pos ):
#         """
#         Constructor function. Requires hole position (x, y) as an argument.
#         """

#         # this creates a generic phylib_object
#         phylib.phylib_object.__init__( self, 
#                                        phylib.PHYLIB_HOLE, 
#                                        0, 
#                                        pos, None, None, 
#                                        0.0, 0.0 );
      
#         # this converts the phylib_object into a Hole class
#         self.__class__ = Hole;


#     def svg( self ):
#         return """ <circle cx="%d" cy="%d" r="%d" fill="black" />\n""" % ( self.obj.hole.pos.x, self.obj.hole.pos.y, HOLE_RADIUS );


# ################################################################################
# class HCushion( phylib.phylib_object ):
#     """
#     Python HCushion class.
#     """

#     def __init__( self, y ):
#         """
#         Constructor function. Requires y-coordinate of the cushion as an argument.
#         """

#         # this creates a generic phylib_object
#         phylib.phylib_object.__init__( self, 
#                                        phylib.PHYLIB_HCUSHION, 
#                                        0, 
#                                        None, None, None, 
#                                        0.0, y);
      
#         # this converts the phylib_object into a HCushion class
#         self.__class__ = HCushion;


#     def svg( self ):
#         return """ <rect width="1400" height="25" x="-25" y="%d" fill="darkgreen" />\n""" % ( 2700 if self.obj.hcushion.y > 0 else -25 );


# ################################################################################
# class VCushion( phylib.phylib_object ):
#     """
#     Python VCushion class.
#     """

#     def __init__( self, x ):
#         """
#         Constructor function. Requires x-coordinate of the cushion as an argument.
#         """

#         # this creates a generic phylib_object
#         phylib.phylib_object.__init__( self, 
#                                        phylib.PHYLIB_VCUSHION, 
#                                        0, 
#                                        None, None, None, 
#                                        x, 0.0);
      
#         # this converts the phylib_object into a VCushion class
#         self.__class__ = VCushion;


#     def svg( self ):
#         return """ <rect width="25" height="2750" x="%d" y="-25" fill="darkgreen" />\n""" % ( 1350 if self.obj.vcushion.x > 0 else -25 );


# ################################################################################
# class Table( phylib.phylib_table ):
#     """
#     Pool table class.
#     """

#     def __init__( self ):
#         """
#         Table constructor method.
#         This method call the phylib_table constructor and sets the current
#         object index to -1.
#         """
#         phylib.phylib_table.__init__( self );
#         self.current = -1;

#     def __iadd__( self, other ):
#         """
#         += operator overloading method.
#         This method allows you to write "table+=object" to add another object
#         to the table.
#         """
#         self.add_object( other );
#         return self;

#     def __iter__( self ):
#         """
#         This method adds iterator support for the table.
#         This allows you to write "for object in table:" to loop over all
#         the objects in the table.
#         """
#         self.current = -1;
#         return self;

#     def __next__( self ):
#         """
#         This provides the next object from the table in a loop.
#         """
#         self.current += 1;  # increment the index to the next object
#         if self.current < MAX_OBJECTS:   # check if there are no more objects
#             return self[ self.current ]; # return the latest object

#         # if we get there then we have gone through all the objects
#         self.current = -1;    # reset the index counter
#         raise StopIteration;  # raise StopIteration to tell for loop to stop

#     def __getitem__( self, index ):
#         """
#         This method adds item retreivel support using square brackets [ ] .
#         It calls get_object (see phylib.i) to retreive a generic phylib_object
#         and then sets the __class__ attribute to make the class match
#         the object type.
#         """
#         result = self.get_object( index ); 
#         if result==None:
#             return None;
#         if result.type == phylib.PHYLIB_STILL_BALL:
#             result.__class__ = StillBall;
#         if result.type == phylib.PHYLIB_ROLLING_BALL:
#             result.__class__ = RollingBall;
#         if result.type == phylib.PHYLIB_HOLE:
#             result.__class__ = Hole;
#         if result.type == phylib.PHYLIB_HCUSHION:
#             result.__class__ = HCushion;
#         if result.type == phylib.PHYLIB_VCUSHION:
#             result.__class__ = VCushion;
#         return result;

#     def __str__( self ):
#         """
#         Returns a string representation of the table that matches
#         the phylib_print_table function from A1Test1.c.
#         """
#         result = "";    # create empty string
#         result += "time = %6.1f;\n" % self.time;    # append time
#         for i,obj in enumerate(self): # loop over all objects and number them
#             result += "  [%02d] = %s\n" % (i,obj);  # append object description
#         return result;  # return the string

#     def segment( self ):
#         """
#         Calls the segment method from phylib.i (which calls the phylib_segment
#         functions in phylib.c.
#         Sets the __class__ of the returned phylib_table object to Table
#         to make it a Table object.
#         """

#         result = phylib.phylib_table.segment( self );
#         if result:
#             result.__class__ = Table;
#             result.current = -1;
#         return result;
    
#     def svg( self ):

#         svg_str = HEADER; # define a string that equals constant
        
#         # Append SVG representation of each object
#         for obj in self:
#             if (obj != None):
#                 svg_str += obj.svg();
#         svg_str += FOOTER;

#         return svg_str;

    
#     def roll( self, t ):
#         new = Table();
#         for ball in self:
#             if isinstance( ball, RollingBall ):
#                 # create a new ball with the same number as the old ball
#                 new_ball = RollingBall( ball.obj.rolling_ball.number,
#                                         Coordinate(0, 0),
#                                         Coordinate(0, 0),
#                                         Coordinate(0, 0) );
#                 # compute where it rolls to
#                 phylib.phylib_roll( new_ball, ball, t );

#                 # add ball to table
#                 new += new_ball;

#             if isinstance( ball, StillBall ):
#                 # create a new ball with the same number and pos as the old ball
#                 new_ball = StillBall( ball.obj.still_ball.number,
#                                       Coordinate( ball.obj.still_ball.pos.x, 
#                                                  ball.obj.still_ball.pos.y ) );
#                 # add ball to table
#                 new += new_ball;

#         # return table
#         return new;

    
#     def cueBall( self, vel_x, vel_y ):
#         """
#         Set up the Cue ball with the given x & y velocity.
#         """

#         # Helper function to find the cue ball
#         def findCueBall():
#             for obj in self:
#                 if (isinstance(obj, StillBall) and obj.obj.still_ball.number == 0):
#                     return obj;
#             return None;
        
#         # Call helper to find the cue ball
#         cue_ball = findCueBall();

#         # If the Cue Ball was found
#         if cue_ball:
#             # Retrieve the x & y values of cue ball’s pos -> store them in temporary variables
#             pos_x = cue_ball.obj.still_ball.pos.x;
#             pos_y = cue_ball.obj.still_ball.pos.y;

#             # Set the type attribute of the cue ball
#             cue_ball.type = phylib.PHYLIB_ROLLING_BALL;

#             # Recalculate acc parameters
#             acc = calculateAcceleration( vel_x, vel_y );

#             # Set all attributes of the cue ball
#             cue_ball.obj.rolling_ball.pos.x = pos_x;
#             cue_ball.obj.rolling_ball.pos.y = pos_y;
#             cue_ball.obj.rolling_ball.vel.x = vel_x;
#             cue_ball.obj.rolling_ball.vel.y = vel_y;
#             cue_ball.obj.rolling_ball.acc.x = acc.x;
#             cue_ball.obj.rolling_ball.acc.y = acc.y;
#             cue_ball.obj.rolling_ball.number = 0;


# ################################################################################
# class Database:
#     def __init__(self, reset=False):
#         if reset and os.path.exists("phylib.db"):
#             os.remove("phylib.db");
        
#         db_file = "phylib.db";

#         self.conn = sqlite3.connect(db_file);
#         self.cursor = self.conn.cursor();
    
#     def createDB(self):

#         # Create Ball table
#         self.cursor.execute( """CREATE TABLE IF NOT EXISTS Ball 
#                                 ( BALLID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#                                   BALLNO INTEGER NOT NULL,
#                                   XPOS FLOAT NOT NULL,
#                                   YPOS FLOAT NOT NULL,
#                                   XVEL FLOAT,
#                                   YVEL FLOAT );""" );

#         # Create TTable table
#         self.cursor.execute( """CREATE TABLE IF NOT EXISTS TTable 
#                                 ( TABLEID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#                                   TIME FLOAT NOT NULL );""" );
        
#         # Create BallTable table
#         self.cursor.execute( """CREATE TABLE IF NOT EXISTS BallTable 
#                                 ( BALLID INTEGER,
#                                   TABLEID INTEGER,
#                                   FOREIGN KEY (BALLID) REFERENCES Ball(BALLID),
#                                   FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID) );""" );

#         # Create Shot table
#         self.cursor.execute( """CREATE TABLE IF NOT EXISTS Shot 
#                                 ( SHOTID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#                                   PLAYERID INTEGER NOT NULL,
#                                   GAMEID INTEGER NOT NULL,
#                                   FOREIGN KEY (PLAYERID) REFERENCES Player(PLAYERID),
#                                   FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID) );""" );

#         # Create TableShot table
#         self.cursor.execute( """CREATE TABLE IF NOT EXISTS TableShot 
#                                 ( TABLEID INTEGER NOT NULL,
#                                   SHOTID INTEGER NOT NULL,
#                                   FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID),
#                                   FOREIGN KEY (SHOTID) REFERENCES Shot(SHOTID) );""" );

#         # Create Game table
#         self.cursor.execute( """CREATE TABLE IF NOT EXISTS Game 
#                                 ( GAMEID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#                                   GAMENAME VARCHAR(64) NOT NULL );""" );

#         # Create Player table
#         self.cursor.execute( """CREATE TABLE IF NOT EXISTS Player 
#                                 ( PLAYERID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
#                                   GAMEID INTEGER NOT NULL,
#                                   PLAYERNAME VARCHAR(64) NOT NULL,
#                                   FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID) );""" );
        
#         self.conn.commit();
#         self.cursor.close();


#     def readTable(self, tableID):
#         # Open cursor
#         self.cursor = self.conn.cursor();

#         # Single SQL SELECT statement with JOIN clause to retrieve table information
#         rows = self.cursor.execute( """SELECT Ball.BALLID, Ball.BALLNO, Ball.XPOS, Ball.YPOS, Ball.XVEL, Ball.YVEL, TTable.TIME
#                                        FROM Ball 
#                                        JOIN BallTable 
#                                        ON Ball.BALLID = BallTable.BALLID 
#                                        JOIN TTable 
#                                        ON BallTable.TABLEID = TTable.TABLEID
#                                        WHERE BallTable.TABLEID = ?""", (tableID + 1,) ).fetchall();  # Add 1 to tableID to match SQL num

#         # Check if the table exists
#         if not rows:
#             self.cursor.close();
#             return None;

#         # Create a new Table
#         table = Table();

#         # Iterate through the retrieved rows
#         for row in rows:
#             # unpack into individual vars for easy handling
#             ball_id, ball_no, pos_x, pos_y, vel_x, vel_y, time = row;

#             # Create pos coordinate
#             pos = Coordinate( float(pos_x), float(pos_y) );

#             # Check if ball has vel
#             if vel_x is not None and vel_y is not None:
#                 # Create RollingBall with acceleration
#                 # Compute the acceleration on the rolling ball
#                 # Get acc & vel coordinates
#                 acc = calculateAcceleration( vel_x, vel_y);
#                 vel = Coordinate( float(vel_x), float(vel_y) );

#                 # Create rb
#                 ball = RollingBall( int(ball_no), pos, vel, acc );
#             else:
#                 # Create sb
#                 ball = StillBall( int(ball_no), pos );

#             # Add ball to the table
#             table += ball;

#         # Set the time attribute of the table
#         table.time = time;

#         # Commit changes and close cursor
#         self.conn.commit();
#         self.cursor.close();

#         return table;
    

#     def writeTable(self, table):
#         # Open cursor 
#         self.cursor = self.conn.cursor();

#         # Insert time into TTable table
#         self.cursor.execute( """INSERT INTO TTable (TIME) VALUES (?)""", (table.time,) );
        
#         # Get table id
#         table_id = self.cursor.lastrowid;

#         # Insert each ball into Ball and BallTable tables
#         for ball in table:
#             # Check for RollingBall
#             if isinstance(ball, ( RollingBall, StillBall )):
#                 self.cursor.execute( """INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) VALUES (?, ?, ?, ?, ?);""", 
#                                         (ball.obj.rolling_ball.number if isinstance(ball, RollingBall) else ball.obj.still_ball.number,
#                                          ball.obj.rolling_ball.pos.x if isinstance(ball, RollingBall) else ball.obj.still_ball.pos.x, 
#                                          ball.obj.rolling_ball.pos.y if isinstance(ball, RollingBall) else ball.obj.still_ball.pos.y, 
#                                          ball.obj.rolling_ball.vel.x if isinstance(ball, RollingBall) else None,
#                                          ball.obj.rolling_ball.vel.y if isinstance(ball, RollingBall) else None) );
#                 # Get ball id
#                 ball_id = self.cursor.lastrowid;

#                 # Add ball to BallTable
#                 self.cursor.execute("""INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)""", (ball_id, table_id));

#         self.conn.commit();
#         self.cursor.close();

#         return table_id - 1;
    
#     def getGame(self, gameID):
#         # Open cursor
#         self.cursor = self.conn.cursor()

#         # Fetch game data from Game & Player table
#         rows = self.cursor.execute( """SELECT GAMEID, GAMENAME, PLAYERNAME
#                                       FROM Game
#                                       JOIN Player 
#                                       ON Game.GAMEID = Player.GAMEID 
#                                       WHERE Game.GAMEID = ?
#                                       ORDER BY PLAYERID ASC""", (gameID + 1,)).fetchall();  # Add 1 to match SQL num

#         # Check if game exists
#         if not rows:
#             self.cursor.close();
#             return None;
        
#         # Create game list and add GAMERNAME
#         game = rows[0][1];

#         # Add PLAYERNAME's to game from query
#         for row in rows:
#             game.append(row[2]); 
            
#         # Commit changes and close cursor
#         self.conn.commit();
#         self.cursor.close();

#         return game;

    
#     def setGame(self, game):
#         # Open cursor
#         self.cursor = self.conn.cursor();

#         # Insert game name into the Game table
#         self.cursor.execute( """INSERT INTO Game (GAMENAME) VALUES (?)""", (game.gameName,) );

#         # Get game id
#         gameID = self.cursor.lastrowid;

#         # Insert player names into Player table
#         # self.cursor.execute( """INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?)""", (gameID, game.player1Name) );
#         # elf.cursor.execute( """INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?)""", (gameID, game.player2Name) );

#         # Prepare a list of tuples for player names
#         player_data = [(gameID, game.player1Name), (gameID, game.player2Name)];

#         # Insert player names into Player table using executemany
#         self.cursor.executemany( """INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?)""", player_data );

#         # Commit changes and close cursor
#         self.conn.commit();
#         self.cursor.close();

#         return gameID - 1;
    
    
#     def getPlayerID(self, playerName):
#         """
#         Helper method to get the playerID using the playerName.
#         """
#         # Open cursor
#         self.cursor = self.conn.cursor();

#         # Fetch player ID based on playerName
#         playerID = self.cursor.execute( """SELECT PLAYERID FROM Player WHERE PLAYERNAME = ?""", (playerName,) ).fetchone();

#         # Check if player exists
#         if playerID:
#             playerID = playerID[0];
#         else:
#             playerID = None;
        
#         # Commit changes and close cursor
#         self.conn.commit();
#         self.cursor.close();

#         return playerID - 1;
    

#     def newShot(self, gameID, playerID):
#         """
#         Helper method to insert values into the Shot table.
#         """

#         # Open cursor
#         self.cursor = self.conn.cursor();

#         # Insert a new shot into the Shot table
#         self.cursor.execute( """INSERT INTO Shot (PLAYERID, GAMEID) VALUES (?, ?)""", (playerID + 1, gameID + 1,) );

#         # Get shotID
#         shotID = self.cursor.lastrowid;

#         # Commit changes and close cursor
#         self.conn.commit();
#         self.cursor.close();

#         return shotID - 1;


#     def newTableShot(self, tableID, shotID):
#         """
#         Helper method to insert values into the TableShot table.
#         """

#         # Open cursor
#         self.cursor = self.conn.cursor();

#         # Insert only if the record does not exist
#         # self.cursor.execute( """INSERT INTO TableShot (TABLEID, SHOTID) VALUES (?, ?)""", (tableID + 1, shotID + 1,) );
#         self.cursor.execute( """INSERT INTO TableShot (TABLEID, SHOTID)
#                                 SELECT ?, ? 
#                                 WHERE NOT EXISTS (
#                                     SELECT 1
#                                     FROM TableShot 
#                                     WHERE TableShot.TABLEID = ? 
#                                     AND TableShot.SHOTID = ?)""", (tableID + 1, shotID + 1, tableID + 1, shotID + 1) );
        
#         # Commit changes and close cursor
#         self.conn.commit();
#         self.cursor.close();
    

#     def close(self):
#         self.conn.commit();
#         self.conn.close();
    

# ################################################################################
# class Game:

#     database : Database = None;
#     current_cursor = None;

#     def __init__( self, gameID=None, gameName=None, player1Name=None, player2Name=None ):

#         self.database = Database();
#         self.database.createDB();
#         self.cursor = self.database.conn.cursor();

#         # Check if constructor is called with valid arguments
#         if (gameID is not None 
#             and gameName is None 
#             and player1Name is None 
#             and player2Name is None):

#             # Get game data
#             game_data = self.database.getGame(gameID);

#             # Check if game exists
#             if game_data is not None:
#                 # Extract data
#                 self.gameID = gameID;
#                 self.gameName = game_data[0];
#                 self.player1Name = game_data[1];
#                 self.player2Name = game_data[2];
#             else:
#                 # Handle the case where the game does not exist
#                 raise ValueError("Game does not exist");

#         elif (gameID is None 
#               and isinstance(gameName, str) 
#               and isinstance(player1Name, str) 
#               and isinstance(player2Name, str)):
              
#             # Initialize member variables
#             self.gameName = gameName;
#             self.player1Name = player1Name;
#             self.player2Name = player2Name;

#             # Create new game in database and obtain the gameID
#             self.gameID = self.database.setGame(self);

#         else:
#             raise TypeError("Invalid combination of arguments for Game constructor");
    
#     def shoot( self, gameName, playerName, table, xvel, yvel ):

#         # Obtain the playerID using playerName
#         playerID = self.database.getPlayerID(playerName);
        
#         # Ensure the player exists in the database
#         if playerID is None:
#             raise ValueError(f"PlayerID for '{playerName}' not found.");
        
#         # Add a new entry to Shot table for the current game and given playerID
#         shotID = self.database.newShot(self.gameID, playerID);
        
#         # Find the cue ball, set type, calculate acc, set new data.
#         table.cueBall(xvel, yvel);

#         # Record the original table
#         #original_table_id = self.database.writeTable(table);
#         #self.database.newTableShot(original_table_id, shotID);

#         while table:
#             # Iterate over the segments
#             segment = table.segment();

#             # Stop loop
#             if (segment == None):
#                 break;

#             # Calculate length of the segment
#             segment_len = int( ( segment.time - table.time ) // FRAME_INTERVAL );

#             for i in range(segment_len):
#                 rt = i * FRAME_INTERVAL;
#                 # Create new table for each frame
#                 new_table = table.roll(rt);
#                 # Set the time of the new table
#                 new_table.time = table.time + rt;
#                 # Save the new table to the database and record it in TableShot
#                 new_table_id = self.database.writeTable(new_table);
#                 self.database.newTableShot(new_table_id, shotID);
            
#             # Update the table to the last state of the segment
#             table = segment;
            
