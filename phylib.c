#include "phylib.h"

phylib_object *phylib_new_still_ball(unsigned char number, phylib_coord *pos) {
    phylib_object *obj = calloc(1, sizeof(phylib_object)); //changed from malloc to
    if (!obj) {
        return NULL;
    }

    obj->type = PHYLIB_STILL_BALL;
    obj->obj.still_ball.number = number;
    if (pos) {
        obj->obj.still_ball.pos = *pos;
    }

    return obj;
}


phylib_object *phylib_new_rolling_ball(unsigned char number, phylib_coord *pos, phylib_coord *vel, phylib_coord *acc) {
    phylib_object *obj = calloc(1, sizeof(phylib_object)); //changed from malloc to calloc
    if (!obj) {
        return NULL;
    }

    obj->type = PHYLIB_ROLLING_BALL;
    obj->obj.rolling_ball.number = number;
    if (pos) {
        obj->obj.rolling_ball.pos = *pos;
    }
    if (vel) {
        obj->obj.rolling_ball.vel = *vel;
    }
    if (acc) {
        obj->obj.rolling_ball.acc = *acc;
    }

    return obj;
}


phylib_object *phylib_new_hole(phylib_coord *pos) {
    phylib_object *obj = calloc(1, sizeof(phylib_object));
    if (!obj) {
        return NULL;
    }

    obj->type = PHYLIB_HOLE;
    if (pos) {
        obj->obj.hole.pos = *pos;
    }

    return obj;
}

phylib_object *phylib_new_hcushion(double y) {
    phylib_object *obj = calloc(1, sizeof(phylib_object)); //changed from malloc to calloc
    if (!obj) {
        return NULL;
    }

    obj->type = PHYLIB_HCUSHION;
    obj->obj.hcushion.y = y;

    return obj;
}

phylib_object *phylib_new_vcushion(double x) {
    phylib_object *obj = calloc(1, sizeof(phylib_object)); //changed from malloc to calloc
    if (!obj) {
        return NULL;
    }

    obj->type = PHYLIB_VCUSHION;
    obj->obj.vcushion.x = x;

    return obj;
}

phylib_table *phylib_new_table(void) {
    phylib_table *table = calloc(1, sizeof(phylib_table)); //changed from malloc to calloc
    if (!table) {
        return NULL;
    }

    table->time = 0.0;
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        table->object[i] = NULL;
    }

    // Create and add horizontal and vertical cushions
    table->object[0] = phylib_new_hcushion(0.0); // Horizontal cushion at y=0.0
    table->object[1] = phylib_new_hcushion(PHYLIB_TABLE_LENGTH); // Horizontal cushion at y=PHYLIB_TABLE_LENGTH
    table->object[2] = phylib_new_vcushion(0.0); // Vertical cushion at x=0.0
    table->object[3] = phylib_new_vcushion(PHYLIB_TABLE_WIDTH); // Vertical cushion at x=PHYLIB_TABLE_WIDTH

    table->object[4] = phylib_new_hole(&(phylib_coord){.x = 0.0, .y = 0.0}); // Top-left
    table->object[5] = phylib_new_hole(&(phylib_coord){.x = 0.0, .y = PHYLIB_TABLE_LENGTH / 2}); // Left-middle
    table->object[6] = phylib_new_hole(&(phylib_coord){.x = 0.0, .y = PHYLIB_TABLE_LENGTH}); // Left-bottom
    table->object[7] = phylib_new_hole(&(phylib_coord){.x = PHYLIB_TABLE_WIDTH, .y = 0.0}); // Top-right
    table->object[8] = phylib_new_hole(&(phylib_coord){.x = PHYLIB_TABLE_WIDTH, .y = PHYLIB_TABLE_LENGTH / 2}); // Right-middle
    table->object[9] = phylib_new_hole(&(phylib_coord){.x = PHYLIB_TABLE_WIDTH, .y = PHYLIB_TABLE_LENGTH}); // Right-bottom

    return table;
}

// P
// A
// R
// T

// 2


void phylib_copy_object(phylib_object **dest, phylib_object **src) {
    // Check if the source is NULL or points to a NULL object
    if  (*src == NULL) {
        *dest = NULL;
       
        return;
    }

    // Allocate memory for the destination object
    *dest = (phylib_object *)calloc(1, sizeof(phylib_object)); //changed from malloc to calloc
    if (*dest == NULL) {
        return;
    }

    // Copy the content from source to destination using memcpy
    memcpy(*dest, *src, sizeof(phylib_object));
}

phylib_table *phylib_copy_table(phylib_table *table) {
    if (table == NULL) {
       
        return NULL;
    }

    phylib_table *newTable = calloc(1, sizeof(phylib_table));
    if (newTable == NULL) {
        
        return NULL;
    }

    newTable->time = table->time;

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        
        phylib_copy_object(&newTable->object[i], &table->object[i]);
    }

    
    // phylib_free_table(table );
    return newTable;
}

void phylib_add_object(phylib_table *table, phylib_object *object) {
    if (table == NULL || object == NULL) {
     
        return;
    }

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (table->object[i] == NULL) {
            table->object[i] = object;
            return;
        }
    }
}


void phylib_free_table(phylib_table *table) {
    if (table == NULL) {
       
        return;
    }

    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        if (table->object[i] != NULL) {
      
            free(table->object[i]);
        }
    }

    free(table);
}

phylib_coord phylib_sub(phylib_coord c1, phylib_coord c2) {
    phylib_coord result;
    result.x = c1.x - c2.x;
    result.y = c1.y - c2.y;
    return result;
}

double phylib_length(phylib_coord c) {
    return sqrt(c.x * c.x + c.y * c.y);
}

double phylib_dot_product(phylib_coord a, phylib_coord b) {
    return ((a.x * b.x) + (a.y * b.y));
}

double phylib_distance(phylib_object *obj1, phylib_object *obj2) {
    // Null check for both objects and ensure obj1 is a PHYLIB_ROLLING_BALL
    if (obj1 == NULL || obj2 == NULL || obj1->type != PHYLIB_ROLLING_BALL) {
        return -1.0;
    }

    // Position of the rolling ball
    phylib_coord position1 = obj1->obj.rolling_ball.pos;
    phylib_coord position2;

    switch (obj2->type) {
        case PHYLIB_ROLLING_BALL:
            position2 = obj2->obj.rolling_ball.pos;
            return phylib_length(phylib_sub(position1, position2)) - PHYLIB_BALL_DIAMETER;
            break;

        case PHYLIB_STILL_BALL:
            position2 = obj2->obj.still_ball.pos;
            return phylib_length(phylib_sub(position1, position2)) - PHYLIB_BALL_DIAMETER;
            break;

        case PHYLIB_HOLE:
            position2 = obj2->obj.hole.pos;
            return phylib_length(phylib_sub(position1, position2)) - PHYLIB_HOLE_RADIUS;
            break;

        case PHYLIB_HCUSHION:
            // Calculate distance to the horizontal cushion and return
            return fabs(position1.y - obj2->obj.hcushion.y) - PHYLIB_BALL_RADIUS;

        case PHYLIB_VCUSHION:
            // Calculate distance to the vertical cushion and return
            return fabs(position1.x - obj2->obj.vcushion.x) - PHYLIB_BALL_RADIUS;

        default:
            // Handle unknown object types
            return -1.0;
    }
}


// P
// A
// R
// T

// 3


void phylib_roll( phylib_object *new, phylib_object *old, double time) {
    if (new == NULL || old == NULL || new->type != PHYLIB_ROLLING_BALL || old->type != PHYLIB_ROLLING_BALL) {
        return; // Do nothing if either object is NULL or not a rolling ball
    }

   
    new->obj.rolling_ball.pos.x = old->obj.rolling_ball.pos.x + old->obj.rolling_ball.vel.x * time + 0.5 * old->obj.rolling_ball.acc.x * time * time;
    new->obj.rolling_ball.pos.y = old->obj.rolling_ball.pos.y + old->obj.rolling_ball.vel.y * time + 0.5 * old->obj.rolling_ball.acc.y * time * time;

    
    new->obj.rolling_ball.vel.x = old->obj.rolling_ball.vel.x + old->obj.rolling_ball.acc.x * time;
    new->obj.rolling_ball.vel.y = old->obj.rolling_ball.vel.y + old->obj.rolling_ball.acc.y * time;

   
    if ((new->obj.rolling_ball.vel.x * old->obj.rolling_ball.vel.x) < 0) {
        new->obj.rolling_ball.vel.x = 0;
        new->obj.rolling_ball.acc.x = 0;
    }
    if ((new->obj.rolling_ball.vel.y * old->obj.rolling_ball.vel.y) < 0) {
        new->obj.rolling_ball.vel.y = 0;
        new->obj.rolling_ball.acc.y = 0;
    }
}

unsigned char phylib_stopped(phylib_object *object) {
    if (object == NULL || object->type != PHYLIB_ROLLING_BALL) {
        return 0; // Return 0 if object is NULL or not a rolling ball
    }

    // Calculate the speed of the ball
    double speed = sqrt(object->obj.rolling_ball.vel.x * object->obj.rolling_ball.vel.x +
                        object->obj.rolling_ball.vel.y * object->obj.rolling_ball.vel.y);

    // Check if the speed is less than the epsilon value
    if (speed < PHYLIB_VEL_EPSILON) {
        // Convert the rolling ball to a still ball
        object->type = PHYLIB_STILL_BALL;

        // Ensure the number, and x and y positions are copied to the still ball
        object->obj.still_ball.number = object->obj.rolling_ball.number;
        object->obj.still_ball.pos.x = object->obj.rolling_ball.pos.x;
        object->obj.still_ball.pos.y = object->obj.rolling_ball.pos.y;

    
        return 1; // Return 1 to indicate the ball has stopped and been converted
    }

    return 0; // Return 0 to indicate the ball has not stopped
}


void phylib_bounce(phylib_object **a, phylib_object **b) {
    
    if ((*a)->type != PHYLIB_ROLLING_BALL) {
        return;
    }

    phylib_rolling_ball *ball_a = &((*a)->obj.rolling_ball);

    switch ((*b)->type) {
        case PHYLIB_HCUSHION:
            // Reverse y velocity and y acceleration for ball a
            ball_a->vel.y = -ball_a->vel.y;
            ball_a->acc.y = -ball_a->acc.y;
            break;

        case PHYLIB_VCUSHION:
            // Reverse x velocity and x acceleration for ball a
            ball_a->vel.x = -ball_a->vel.x;
            ball_a->acc.x = -ball_a->acc.x;
            break;

        case PHYLIB_HOLE:
            free(*a);
            *a = NULL;
            break;

        case PHYLIB_STILL_BALL:
        ;
            phylib_coord pos = (*b)->obj.still_ball.pos;
            unsigned char num = (*b)->obj.still_ball.number;
            (*b)->type = PHYLIB_ROLLING_BALL;
            (*b)->obj.rolling_ball = (phylib_rolling_ball){ num, pos, {0.0, 0.0}, {0.0, 0.0} };

        case PHYLIB_ROLLING_BALL:
            ;
            // Compute the collision response for two rolling balls
            phylib_coord r_ab = phylib_sub(ball_a->pos, (*b)->obj.rolling_ball.pos);
            phylib_coord v_rel = phylib_sub(ball_a->vel, (*b)->obj.rolling_ball.vel);

            // Calculate the normal vector
            double length_r_ab = phylib_length(r_ab);
            phylib_coord n = { r_ab.x / length_r_ab, r_ab.y / length_r_ab };

            // Calculate the relative velocity in the direction of the normal
            double v_rel_n = phylib_dot_product(v_rel, n);

            // Update the velocities of both balls            
            ball_a->vel.x -= v_rel_n * n.x;
            ball_a->vel.y -= v_rel_n * n.y;

            (*b)->obj.rolling_ball.vel.x += v_rel_n * n.x;
            (*b)->obj.rolling_ball.vel.y += v_rel_n * n.y;

            // Update the accelerations based on the new velocities
            double speed_a = phylib_length(ball_a->vel);
            if (speed_a > PHYLIB_VEL_EPSILON) {
                ball_a->acc.x = -(ball_a->vel.x / speed_a) * PHYLIB_DRAG;
                ball_a->acc.y = -(ball_a->vel.y / speed_a) * PHYLIB_DRAG;
            }

            double speed_b = phylib_length((*b)->obj.rolling_ball.vel);
            if (speed_b > PHYLIB_VEL_EPSILON) {
                (*b)->obj.rolling_ball.acc.x = (-(*b)->obj.rolling_ball.vel.x / speed_b)*PHYLIB_DRAG;
                (*b)->obj.rolling_ball.acc.y = (-(*b)->obj.rolling_ball.vel.y / speed_b)*PHYLIB_DRAG;
            }
            break;

        default:
            // No action for other types
            break;
    }
}


unsigned char phylib_rolling(phylib_table *t) {
    unsigned char count = 0;
    // Loop through all the objects on the table
    for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++) {
        // Check if the object exists and is of type PHYLIB_ROLLING_BALL
        if (t->object[i] != NULL && t->object[i]->type == PHYLIB_ROLLING_BALL) {
            count++;  // Increment the count if a rolling ball is found
        }
    }
    return count;  // Return the total count of rolling balls
}


phylib_table *phylib_segment(phylib_table *table)
{
    // Verify movement by checking rolling status
    int movementStatus = phylib_rolling(table);

    if (movementStatus == 0)
    {
        return NULL;
    }

    // Clone the current table structure
    phylib_table *copiedTable = phylib_copy_table(table);

    // Simulation time initialization
    double elapsedTime = PHYLIB_SIM_RATE;

    // Time progression loop
    while (elapsedTime < PHYLIB_MAX_TIME)
    {
        // Iterate through potential moving objects
        for (int j = 0; j < PHYLIB_MAX_OBJECTS; j++)
        {
            // Identify and process rolling balls
            if (copiedTable->object[j] != NULL && copiedTable->object[j]->type == PHYLIB_ROLLING_BALL)
            {
                // Apply motion physics
                phylib_roll(copiedTable->object[j], table->object[j], elapsedTime);

                // Determine if motion has ceased
                if (phylib_stopped(copiedTable->object[j]) == 1)
                {
                    // Update simulation time and return modified table
                    copiedTable->time += elapsedTime;
                    return copiedTable;
                }
            }
        }

        // Collision and interaction checking loop
        for (int x = 0; x < PHYLIB_MAX_OBJECTS; x++)
        {
            // Re-check for rolling balls to process collisions
            if (copiedTable->object[x] != NULL && copiedTable->object[x]->type == PHYLIB_ROLLING_BALL)
            {
                for (int i = 0; i < PHYLIB_MAX_OBJECTS; i++)
                {
                    // Exclude self and check for proximity triggering a bounce
                    if (x != i && copiedTable->object[i] != NULL && phylib_distance(copiedTable->object[x], copiedTable->object[i]) < 0.0)
                    {
                        // Process collision effects and check for stop conditions
                        phylib_bounce(&copiedTable->object[x], &copiedTable->object[i]);

                        if (copiedTable->object[i])
                        {
                            phylib_stopped(copiedTable->object[i]);
                        }
                        // Update time with simulation progress and return table
                        copiedTable->time += elapsedTime;
                        return copiedTable;
                    }
                }
            }
        }

        // Increment the simulation time by the rate
        elapsedTime += PHYLIB_SIM_RATE;
    }
    // Return the updated table after completing simulation loop
    return copiedTable;
}


char *phylib_object_string( phylib_object *object ) 
{ 
  static char string[80]; 
  if (object==NULL) 
  { 
    snprintf( string, 80, "NULL;" ); 
    return string; 
  } 
 
  switch (object->type) 
  { 
    case PHYLIB_STILL_BALL: 
      snprintf( string, 80, 
               "STILL_BALL (%d,%6.1lf,%6.1lf)", 
               object->obj.still_ball.number, 
               object->obj.still_ball.pos.x, 
               object->obj.still_ball.pos.y ); 
      break; 
 
    case PHYLIB_ROLLING_BALL: 
      snprintf( string, 80, 
               "ROLLING_BALL (%d,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf,%6.1lf)", 
               object->obj.rolling_ball.number, 
               object->obj.rolling_ball.pos.x, 
               object->obj.rolling_ball.pos.y, 
               object->obj.rolling_ball.vel.x, 
               object->obj.rolling_ball.vel.y, 
               object->obj.rolling_ball.acc.x, 
               object->obj.rolling_ball.acc.y ); 
      break; 
 
    case PHYLIB_HOLE: 
      snprintf( string, 80, 
               "HOLE (%6.1lf,%6.1lf)", 
               object->obj.hole.pos.x, 
               object->obj.hole.pos.y ); 
      break; 
 
    case PHYLIB_HCUSHION: 
      snprintf( string, 80, 
               "HCUSHION (%6.1lf)", 
               object->obj.hcushion.y ); 
      break; 
 
    case PHYLIB_VCUSHION: 
      snprintf( string, 80, 
               "VCUSHION (%6.1lf)", 
               object->obj.vcushion.x ); 
      break; 
  } 
  return string; 
}

