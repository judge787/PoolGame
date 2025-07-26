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
    "WHITE",        # 0 - Cue ball
    "#FFD700",      # 1 - Yellow (solid)
    "#0000FF",      # 2 - Blue (solid)
    "#FF0000",      # 3 - Red (solid)
    "#800080",      # 4 - Purple (solid)
    "#FFA500",      # 5 - Orange (solid)
    "#008000",      # 6 - Green (solid)
    "#8B4513",      # 7 - Brown/Maroon (solid)
    "#000000",      # 8 - Black (8-ball)
    "#FFD700",      # 9 - Yellow (stripe)
    "#0000FF",      # 10 - Blue (stripe)
    "#FF0000",      # 11 - Red (stripe)
    "#800080",      # 12 - Purple (stripe)
    "#FFA500",      # 13 - Orange (stripe)
    "#008000",      # 14 - Green (stripe)
    "#8B4513",      # 15 - Brown/Maroon (stripe)
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
        ball_number = self.obj.still_ball.number
        x = self.obj.still_ball.pos.x
        y = self.obj.still_ball.pos.y
        
        # Cue ball (0) - White
        if ball_number == 0:
            return f'<circle cx="{x}" cy="{y}" r="{BALL_RADIUS}" fill="white" stroke="#ddd" stroke-width="1" />\n'
        
        # Solid balls (1-7)
        elif 1 <= ball_number <= 7:
            color = BALL_COLOURS[ball_number]
            return f'<circle cx="{x}" cy="{y}" r="{BALL_RADIUS}" fill="{color}" stroke="#333" stroke-width="1" />\n'
        
        # 8-ball - Black
        elif ball_number == 8:
            return f'<circle cx="{x}" cy="{y}" r="{BALL_RADIUS}" fill="black" stroke="#333" stroke-width="1" />\n'
        
        # Striped balls (9-15)
        elif 9 <= ball_number <= 15:
            base_color = BALL_COLOURS[ball_number]
            pattern_id = f"stripe_pattern_{ball_number}_{x}_{y}"
            
            return f'''<defs>
    <pattern id="{pattern_id}" patternUnits="userSpaceOnUse" width="20" height="8">
        <rect width="20" height="4" fill="{base_color}"/>
        <rect width="20" y="4" height="4" fill="white"/>
    </pattern>
</defs>
<circle cx="{x}" cy="{y}" r="{BALL_RADIUS}" fill="url(#{pattern_id})" stroke="#333" stroke-width="1" />
'''
        
        # Fallback for any other numbers
        else:
            return f'<circle cx="{x}" cy="{y}" r="{BALL_RADIUS}" fill="gray" stroke="#333" stroke-width="1" />\n'
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
        ball_number = self.obj.rolling_ball.number
        x = self.obj.rolling_ball.pos.x
        y = self.obj.rolling_ball.pos.y
        
        # Cue ball (0) - White
        if ball_number == 0:
            return f'<circle cx="{x}" cy="{y}" r="{BALL_RADIUS}" fill="white" stroke="#ddd" stroke-width="1" />\n'
        
        # Solid balls (1-7)
        elif 1 <= ball_number <= 7:
            color = BALL_COLOURS[ball_number]
            return f'<circle cx="{x}" cy="{y}" r="{BALL_RADIUS}" fill="{color}" stroke="#333" stroke-width="1" />\n'
        
        # 8-ball - Black
        elif ball_number == 8:
            return f'<circle cx="{x}" cy="{y}" r="{BALL_RADIUS}" fill="black" stroke="#333" stroke-width="1" />\n'
        
        # Striped balls (9-15)
        elif 9 <= ball_number <= 15:
            base_color = BALL_COLOURS[ball_number]
            pattern_id = f"stripe_pattern_{ball_number}_{x}_{y}"
            
            return f'''<defs>
    <pattern id="{pattern_id}" patternUnits="userSpaceOnUse" width="20" height="8">
        <rect width="20" height="4" fill="{base_color}"/>
        <rect width="20" y="4" height="4" fill="white"/>
    </pattern>
</defs>
<circle cx="{x}" cy="{y}" r="{BALL_RADIUS}" fill="url(#{pattern_id})" stroke="#333" stroke-width="1" />
'''
        
        # Fallback for any other numbers
        else:
            return f'<circle cx="{x}" cy="{y}" r="{BALL_RADIUS}" fill="gray" stroke="#333" stroke-width="1" />\n'

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
