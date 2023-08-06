# Location - Project

Below is a report that describes how the program works. The report is divided into two parts: Calculating the robot's location distribution and Heuristics.

## Calculating the robot location distribution

Three matrices are used to calculate the robot location distribution:

T - the transition matrix 

O - matrix containing sensor measurements

P - the robot's location distribution matrix

The whole process is based on updating the P matrix by multiplying it by the transition factor and then the O matrix

## P matrix

The P matrix consists of 42 vectors with 4 values each. The vectors represent free locations (of which there are 42) and the values represent individual orientations. 
Initially, all locations have equal probability equal to 1/42 * 1/4. 

## T matrix

The matrix T has size 42x42x4x4. This is due to the fact that for four orientations all possible situations must be taken into account. 
Orientations in the vector are placed according to the order ['N','E','S','W'].

If in the set of percepts a "bump" was detected (the robot hit the wall), a unitary matrix is created for each location,
because the robot will 100% (i.e., 1.0) stay at a given location in a given orientation.

In the case of a right turn in the vector in place of the direction we write 0.05 and for the direction to the right 0.95 
e.g., for orientation N is --> [0.05, 0.95 ,0 ,0] and for orientation S is --> [0 ,0,0.05, 0.95]. 

We do in a similar way for a left turn. We just change the locations for the values (instead of [0 ,0,0.05, 0.95] to [0 ,0.95,0.05,0]).

For forward movement to each location, a list of neighboring locations is created. Then it is checked if the neighbors are walls.
If a given neighbor is not a wall then for each location a matrix is created equal to the unitary matrix multiplied by 0.05.
This results from the fact that there is 0.05 probability that the robot will stay in a given location in a given orientation.
Then, for the next location, a matrix is created equal to the unitary matrix multiplied by 0.95.
This results from the fact that there is 0.95 probability that the robot will move to a given location in an unchanging orientation.
Thus for each place is formed matrix 4x4
If the neighbor is a wall then on the place of the orientation in the given vector is written the value 1.


## Matrix 0

The matrix O has a size of 42x4. A 4 element vector is created for each position.
Each element in this vector defines a probability for a particular orientation of the robot.
Five lists are created. The first four are lists for each instance of the robot's location. Neighbors of a given location are placed in these lists in different order 
([N,E,S,W], [E,S,W,N], [S,W,N,E], [W,N,E,S])

The fifth list, on the other hand, is the collection of all these lists.
The for loop checks each orientation and if the sensor has correctly determined the position of the walls, it multiplies the timestamp variable "a" 
(with initial value 1.0) times 0.9,and if wrong then 0.1.
If there is a 'bump' in 'percept' then for the orientation 'fwd' it multiplies the variable 'a' times 1.0. 

This cycle is repeated for all lists and the results (values of variable 'a') are stored in a vector. 

This is repeated for all locations so we get a 42x4 matrix.

## Multiplication of matrix

At the very beginning we perform the multiplication of matrices T and P. 

We transpose the matrix T because the rows must correspond to the next states. In the original T, the rows correspond to the current states.

The multiplication of T and P consists in matrix multiplication of successive matrices of a given state by successive rows of the matrix P.
The resulting vectors are added together and written as the matrix vector P for a given state

Then each element of the matrix P is multiplied by each element of the matrix O.

At the very end, we normalize the matrix P so that the sum of the elements in the matrix totals 1.

## Heuristics

Heuristics are based on the principle of moving the robot forward as often as possible.
In this way, the robot converges fastest to the algorithm and calculates the probability of its position and orientation.

Heuristics are divided into 3 subsections.

At the very beginning it is checked if the robot has not run into a wall. If there are no walls, or if there are walls on both left and right sides
then the robot randomly rotates to the left or right (50% chance to rotate in one direction is 50%). On the other hand, if there is a wall next to the robot
then the robot rotates opposite to it. 

If the robot has not run into a wall, and an obstacle is detected in front, it is first checked if the wall is only on the left or right side. 
The agent then turns to the opposite side. If walls are on the sides of the robot, the turn is determined based on the previous move. 
If it was a left/right turn, the robot repeats the action. If not, the robot moves forward.

If there is no wall in front, the robot's rotation depends on three factors. 
If the sensor detects only one wall, the robot is allowed to turn, and its previous move was not a turn, it can turn left or right.
This depends on which side of the wall is located. The permission to move is given at
The motion permission is given at program initialization and when the robot moves forward. If the robot makes a turn in either direction, permission is revoked until the robot moves forward.
If the conditions are met, the move is randomly selected from the set ['forward' , 'turnleft/turnroght'] with probability [0.6,0.4]. 
This allows the robot to exit the 'T' shaped part of the corridor. At the same time, however, emphasis is still placed on forward motion.
If the robot cannot move right/left, it moves forward.



