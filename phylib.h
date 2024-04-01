#ifndef _PHYLIB_H
#define _PHYLIB_H

#define PHYLIB_BALL_RADIUS (28.5) //mm
#define PHYLIB_BALL_DIAMETER (2 * PHYLIB_BALL_RADIUS)

#define PHYLIB_HOLE_RADIUS (2 * PHYLIB_BALL_DIAMETER)
#define PHYLIB_TABLE_LENGTH (2700.00) //mm
#define PHYLIB_TABLE_WIDTH (PHYLIB_TABLE_LENGTH/2.0) //mm

#define PHYLIB_SIM_RATE (0.0001) //s
#define PHYLIB_VEL_EPSILON (0.01) //mm/s

#define PHYLIB_DRAG (150.0) // mm/s^2
#define PHYLIB_MAX_TIME (600) //s

#define PHYLIB_MAX_OBJECTS (26) 

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

// enums are like grouped constants
typedef enum { //Polymorphic object types defined as enum, 
    PHYLIB_STILL_BALL = 0,
    PHYLIB_ROLLING_BALL = 1,
    PHYLIB_HOLE = 2,
    PHYLIB_HCUSHION = 3,
    PHYLIB_VCUSHION = 4,
} phylib_obj;


// Class representing a vector in 2 dimensions
typedef struct {
    double x;
    double y;
} phylib_coord;

// Child) Classes representing objects on the table (include these in your .h file)
// First, a ball that is not in motion (i.e. still). It has a number (cue ball is 0) and a position on the
// table.

typedef struct {
    unsigned char number;
    phylib_coord pos;
} phylib_still_ball;

// Next, a ball that is rolling (i.e. not still). It has a number (cue ball is 0) and a position on the
// table. It also has a velocity and a (negative) acceleration (due to friction).
typedef struct {
unsigned char number;
    phylib_coord pos;
    phylib_coord vel;
    phylib_coord acc;
} phylib_rolling_ball;

// Next, one of the 6 holes on the table. It has a position.
typedef struct {
    phylib_coord pos;
} phylib_hole;

// Next, a horizontal cushion (i.e. a cushion along either of the two the short sides of the table). It
// has only a y-coordinate.
typedef struct {
    double y;
} phylib_hcushion;

// Rather predictably, a vertical cushion (i.e. a cushion along either of the two the long sides of the
// table). It has only an x-coordinate.
typedef struct {
    double x;
} phylib_vcushion;


// Polymorphic Parent Class of objects on the table (include these in your .h file)
// First, we need a C union that can store any of the above classes/structure in the same space.
typedef union {
    phylib_still_ball still_ball;
    phylib_rolling_ball rolling_ball;
    phylib_hole hole;
    phylib_hcushion hcushion;
    phylib_vcushion vcushion;
} phylib_untyped;
// While this union can store an object of any of the above classes/structures, it cannot identify
// what the class of the object is, so we need another structure for that.


typedef struct {
    phylib_obj type;
    phylib_untyped obj;
} phylib_object;

// Here, the type is the enum indicating the class of the object, and obj is the object itself.
// We can now use phylib_object to represent a generic object in the billiards world

// Finally, the table (include this in your .h file)
typedef struct {
    double time;
    phylib_object *object[PHYLIB_MAX_OBJECTS];
} phylib_table;

// As the game proceeds there will be multiple table configurations at different points in time, so
// each table “knows” its time. There can be a maximum of 26 objects on the table: 15 numbered
// balls, 1 cue ball, 4 cushions, and 6 holes


// Function prototypes for constructor methods and descriptions for your
// assignment
phylib_object *phylib_new_still_ball( unsigned char number,
phylib_coord *pos );
// This function will allocate memory for a new phylib_object, set its type to
// PHYLIB_STILL_BALL and transfer the information provided in the function parameters into the
// structure. It will return a pointer to the phylib_object. If the malloc function fails, it will
// return NULL (before trying to store the function parameters in the (non-existent) structure).


phylib_object *phylib_new_rolling_ball( unsigned char number,
                                phylib_coord *pos,
                                phylib_coord *vel,
                                phylib_coord *acc );

phylib_object *phylib_new_hole( phylib_coord *pos );
phylib_object *phylib_new_hcushion( double y );
phylib_object *phylib_new_vcushion( double x );
// These functions will do the same thing as the phylib_new_still_ball function for their
// respective structures


/*This function will allocate memory for a table structure, returning NULL if the memory
 allocation fails. The member variable, time, will be set to 0.0. It will then assign the values of
 its array elements to pointers to new objects created by the phylib_new_* functions provided
 above. Specifically, it will add elements in this order:
1) a horizontal cushion at y=0.0;
 2) a horizontal cushion at y=PHYLIB_TABLE_LENGTH;
 3) a vertical cushion at x=0.0;
 4) a vertical cushion at x=PHYLIB_TABLE_WIDTH;
 5) 6 holes: positioned in the four corners where the cushions meet and two more
 midway between the top holes and bottom holes.
 The remaining pointers will all be set to NULL.*/
phylib_table *phylib_new_table( void );


/*This function should allocate new memory for a phylib_object.  Save the address of that 
object at the location pointed to by dest, and copy over the contents of the object from the 
location pointed to by src.  Hint, you can use memcpy to make this a one-step operation that 
works for any type of phylib_object.  If src points to a location containing a NULL pointer, 
then the location pointed to by dest should be assigned the value of NULL.*/
void phylib_copy_object( phylib_object **dest, phylib_object **src );

/*This function should allocate memory for a new phylib_table, returning NULL if the malloc 
fails.  Then the contents pointed to by table should be copied to the new memory location and 
the address returned.*/
phylib_table *phylib_copy_table( phylib_table *table );


/*This function should iterate over the object array in the table until it finds a NULL pointer.  It 
should then assign that pointer to be equal to the address of object.  If there are no NULL 
pointers in the array, the function should do nothing.*/
void phylib_add_object( phylib_table *table, phylib_object *object );


/**
 * This function should free every non-NULL pointer in the object array of table. It should then
 * also free table as well.
 */
void phylib_free_table(phylib_table *table);

/**
 * This function should return the difference between c1 and c2. That is the result’s x value
 * should be c1.x-c2.x and similarly for y.
 */
phylib_coord phylib_sub(phylib_coord c1, phylib_coord c2);

/**
 * This function should return the length of the vector/coordinate c. You can calculate this length
 * by using Pythagorean theorem. Important: you must not use the exp function from the math
 * library. That function is designed for raising values to a real power and is extremely inefficient
 * for something as simple as squaring a value.
 */
double phylib_length(phylib_coord c);

/**
 * This function should compute the dot-product between two vectors. Hint: the dot product is
 * equal to the sum of: the product of the x-values and the product of the y-values.
 */
double phylib_dot_product(phylib_coord a, phylib_coord b);

/**
 * This function should calculate the distance between two objects obj1 and obj2. obj1 must be
 * a PHYLIB_ROLLING_BALL; if it is not the function should return -1.0. Otherwise, the distance
 * between the obj1 (PHYLIB_ROLLING_BALL) and obj2 is given by the following rules:
 * 1) If obj2 is another BALL (ROLLING or STILL) then compute the distance between the
 *    centres of the two balls and subtract two radii (i.e. one PHYLIB_BALL_DIAMETER).
 * 2) If obj2 is a HOLE then compute the distance between the centre of the ball and the
 *    hole and subtract the HOLE_RADIUS.
 * 3) If obj2 is a CUSHION calculate the distance between the centre of the ball and the
 *    CUSHION and subtract the BALL_RADIUS. Hint: use abs since the ball might be left/above
 *    or right/below to CUSHION.
 * Return -1.0 if obj2 isn’t any valid type.
 */
double phylib_distance(phylib_object *obj1, phylib_object *obj2);


// Part 3
// These functions simulate the balls moving on the table.

/**
 * This function updates a new phylib_object that represents the old phylib_object after it 
has rolled for a period of time.  If new and old are not PHYLIB_ROLLING_BALLs, then the 
function should do nothing.  Otherwise, it should update the values in new.  Specifically the 
position, and velocities should be updated as follows:

p= p1 + v1t+ (1/
2)(a1)t^2

 
(For physics/math fans, this is the second integral of the acceleration.)  Here, the variable 
represents either the x or y position of the ball, the variable  represents either the x or y 
velocity of the ball, and   represents either the x or y acceleration of the ball.  The subscript 1 
indicates we are talking about the old ball.  The velocity of the new ball (in either the x or y 
dimension) is given by: 
 
v=v1 +a1(t)
  
One additional constraint must be observed.  If either velocity changes sign, then that velocity 
and its corresponding acceleration (x, or y) must be set to zero (if both velocities change sign, 
then both velocities and both accelerations must be set to zero).
*/
void phylib_roll( phylib_object *new, phylib_object *old, double time );

/*This function will check whether a ROLLING_BALL has stopped, and if it has, will convert it to a 
STILL_BALL.  You may assume that object is a ROLLING_BALL.  The function will return 1 if it 
converts the ball, 0 if it does not. 
 
For the purposes of this simulation a ball is considered to have stopped if its speed (which is the 
length of its velocity) is less than PHYLIB_VEL_EPSILON. 
 
Do not assume that the number, and x and y positions of the rolling ball will be automatically 
transferred to the still ball.*/
unsigned char phylib_stopped( phylib_object *object );

/*This is the most complicated function in the assignment but it can be handled by divide and 
conquer based on the type of object b.  You may assume that object a is a ROLLING_BALL. 
 
Note that the two arguments to this function are double pointers.  That is, they are pointers to 
pointers to phylib_objectss. 
 
CASE 1:  b is a HCUSHION: 
In this case the y velocity and y acceleration of a are reversed (negated).  This is the 
physical principle of angle of incidence equals angle of reflection. 
 
CASE 2:  b is a VCUSION: 
In this case the x velocity and x acceleration of a are reversed (negated).  This is the 
physical principle of angle of incidence equals angle of reflection. 
 
CASE 3:  b is a HOLE: 
In this case, free the memory of a and set it to NULL.  This represents the ball falling off 
the table. 
 
CASE 4:  b is a STILL_BALL: 
In this case, “upgrade” the STILL_BALL to a ROLLING BALL and proceed directly to CASE 
5 (do not collect $200).  HINT: if you leave out the break statement at the end of a case 
condition, the code will continue with the next case. 
 
CASE 5: b is a ROLLING_BALL: 
This one is a little bit tricky and will require us to calculate a few intermediate values 
before we can know the speeds and directions of the two balls after they collide. 
 
Compute the position of a with respect to b:  subtract the position of b from a; call it 
r_ab. 
 
Compute the relative velocity of a with respect to b:  subtract the velocity of b from a; 
call it v_rel. 
 
Divide the x and y components of r_ab by the length of r_ab; call that a normal 
vector, n. 
 
Calculate the ratio of the relative velocity, v_rel, in the direction of ball a by computing 
the dot_product of v_rel with respect to n; call that v_rel_n.   
 
Now, ball a will roll perpendicular to the direction from a to b, and b will run in the 
direction from a to b.
pdate the x velocity of ball a by subtracting v_rel_n multipied by the x component of 
vector n.  Similarly, Update the y velocity of ball a by subtracting v_rel_n multipied by 
the y component of vector n. 
 
Update the x and y velocities of ball b by adding the product of v_rel_n and vector n. 
 
Compute the speed of a and b as the lengths of their velocities.  If the speed is greater 
than PHYLIB_VEL_EPSILON then set the acceleration of the ball to the negative 
velocity divided by the speed multiplied by PHYLIB_DRAG. */
void phylib_bounce( phylib_object **a, phylib_object **b );

/*This function should return the number of ROLLING_BALLS on the table*/
unsigned char phylib_rolling( phylib_table *t );

/*This function should return a segment of a pool shot, as follows. 
 
If there are no ROLLING_BALLs on the table, it should return NULL. 
 
Otherwise, it should return a phylib_copy_table.  The returned table should be the result of 
applying the phylib_roll function to each ROLLING_BALL with a value of time that starts at 
PHYLIB_SIM_RATE and increments by PHYLIB_SIM_RATE.  All the balls should roll at the same 
time, so make sure to put the loop over the OBJECTS inside the loop over the time.  The loop 
over the time should end if: 
 
1) PHYLIB_MAX_TIME is reached, 
2) The phylib_distance between the ball and another phylib_object is less than 0.0. 
If this happens, apply the phylib_bounce function to the ball and the object before 
returning the copy of the table. 
3) A ROLLING_BALL has stopped*/
phylib_table *phylib_segment( phylib_table *table );

char *phylib_object_string( phylib_object *object );

#endif



