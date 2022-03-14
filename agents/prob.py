# prob.py
# This is

import random
import numpy as np
import operator
from gridutil import *

best_turn = {('N', 'E'): 'turnright',
             ('N', 'S'): 'turnright',
             ('N', 'W'): 'turnleft',
             ('E', 'S'): 'turnright',
             ('E', 'W'): 'turnright',
             ('E', 'N'): 'turnleft',
             ('S', 'W'): 'turnright',
             ('S', 'N'): 'turnright',
             ('S', 'E'): 'turnleft',
             ('W', 'N'): 'turnright',
             ('W', 'E'): 'turnright',
             ('W', 'S'): 'turnleft'}


class LocAgent:
    def __init__(self, size, walls, eps_perc, eps_move):
        self.size = size
        self.walls = walls
        # list of valid locations
        self.locations = list({*locations(self.size)}.difference(self.walls))
        # dictionary from location to its index in the list
        self.loc_to_idx = {loc: idx for idx, loc in enumerate(self.locations)}
        self.eps_perc = eps_perc
        self.eps_move = eps_move

        # previous action
        self.prev_action = None

        # Calculate starting P
        prob = 0.25 * 1 / len(self.locations)
        self.P = prob * np.ones([len(self.locations), 4], dtype=np.float)
        self.loop = 0
        self.prev_percept=[]
        self.turn = True

    def __call__(self, percept):
        # update posterior
        # TODO PUT YOUR CODE HERE

        # transition model
        T = np.zeros([len(self.locations), len(self.locations), 4,4], dtype=np.float)
        if "bump" in percept:
            for idx, loc in enumerate(self.locations):
                T[idx,idx] = np.array([[1.0, 0., 0., 0.],
                                       [0., 1.0, 0., 0.],
                                       [0., 0., 1.0, 0.],
                                       [0., 0., 0., 1.0]])
        elif self.prev_action == "forward":
            for idx, loc in enumerate(self.locations):
                loc = list(loc)
                locN = [loc[0], loc[1] + 1]
                locS = [loc[0], loc[1] - 1]
                locW = [loc[0] - 1, loc[1]]
                locE = [loc[0] + 1, loc[1]]
                locs = [tuple(locN), tuple(locE), tuple(locS), tuple(locW)]
                T[idx,idx] = np.array([[0.0, 0., 0., 0.],
                                       [0., 0.0, 0., 0.],
                                       [0., 0., 0.0, 0.],
                                       [0., 0., 0., 0.0]])
                for idk,next_loc in enumerate(locs):
                    if legalLoc(next_loc, self.size) and (next_loc not in self.walls):
                        next_idx = self.loc_to_idx[next_loc]
                        T[idx, next_idx, idk,idk] = 0.95
                        T[idx, idx, idk,idk] = 0.05
                    else:
                        T[idx, idx, idk,idk] = 1.

        elif self.prev_action == "turnright":
                for idx, loc in enumerate(self.locations):
                    T[idx, idx, :] = np.array([[0.05, 0.0, 0., 0.95],
                                      [0.95, 0.05, 0., 0.],
                                      [0., 0.95, 0.05, 0.],
                                      [0., 0., 0.95, 0.05]])
        elif self.prev_action == "turnleft":
                for idx, loc in enumerate(self.locations):
                    T[idx, idx, :] = np.array([[0.05, 0.95, 0., 0.],
                                      [0., 0.05, 0.95, 0.],
                                      [0., 0., 0.05, 0.95],
                                      [0.95, 0., 0., 0.05]])

        # sensor model
        O = np.zeros([len(self.locations),4], dtype=np.float)
        for idx, loc in enumerate(self.locations):
            loc = list(loc)
            locN = [loc[0],loc[1]+1]
            locS = [loc[0], loc[1]-1]
            locW = [loc[0] - 1,loc[1]]
            locE = [loc[0] + 1,loc[1]]
            nesw = [tuple(locN),tuple(locE),tuple(locS),tuple(locW)]
            eswn = [tuple(locE), tuple(locS), tuple(locW), tuple(locN)]
            swne = [tuple(locS), tuple(locW), tuple(locN), tuple(locE)]
            wnes = [tuple(locW), tuple(locN), tuple(locE), tuple(locS)]
            locs = [nesw,eswn,swne,wnes]
            for idk, place in enumerate(locs):
                a = 1
                d = ['fwd', 'right', 'bckwd', 'left']
                for i, p in enumerate(d):
                    obstacle = (not legalLoc(place[i], self.size)) or (place[i] in self.walls)
                    if 'bump' in percept and p =='fwd':
                        a = a
                    elif obstacle == (p in percept):
                        a = a * (1 - self.eps_perc)
                    else:
                        a = a * self.eps_perc
                O[idx][idk] = a

        if np.sum(T) != 0:
            T = T.transpose(1,0,2,3)
            for i in range(len(self.locations)):
                a = [0 ,0 , 0 ,0]
                for j in range(len(self.locations)):
                    a = a + T[i][j]@ self.P[j]
                self.P[i] = a
        self.P = O*self.P
        self.P /= np.sum(self.P)
        action = 'forward'

        # TODO CHANGE THIS HEURISTICS TO SPEED UP CONVERGENCE
        # MY HEURISTICS
        if 'bump' in percept:
            if 'left' and 'right' in percept:
                action = np.random.choice(['turnright', 'turnleft'], 1, p=[0.5, 0.5])
            elif 'left' in percept:
                action = 'turnright'
                self.turn = False
            elif 'right' in percept:
                action = 'turnleft'
                self.turn = False
            else:
                action = np.random.choice(['turnright', 'turnleft'], 1, p=[0.5, 0.5])

        elif 'fwd' in percept:
            if 'left' in percept and 'right' not in percept:
                action =  'turnright'
                self.turn = False
            elif 'right' in percept and 'left' not in percept:
                action = 'turnleft'
                self.turn = False
            else:
                if self.prev_action == 'turnleft':
                    action = 'turnleft'
                    self.turn = False
                elif self.prev_action == 'turnright':
                    action = 'turnright'
                    self.turn = False
                else:
                    action = 'forward'
                    self.turn = True
        else:
            if 'right' in percept and self.turn and self.prev_action !='turnleft':
                    action = np.random.choice(['forward', 'turnleft'], 1, p=[0.6, 0.4])
                    self.turn = False
            elif 'left' in percept and self.turn and self.prev_action !='turnright':
                    action = np.random.choice(['forward', 'turnright'], 1, p=[0.6, 0.4])
                    self.turn = False
            else:
                    action = 'forward'
                    self.turn = True

        self.prev_percept = percept
        self.prev_action = action
        return action

    def getPosterior(self):
        # directions in order 'N', 'E', 'S', 'W'
        P_arr = np.zeros([self.size, self.size, 4], dtype=np.float)

        # put probabilities in the array
        # TODO PUT YOUR CODE HERE
        for idx, loc in enumerate(self.locations):
            P_arr[loc[0], loc[1]] = self.P[idx]
        return P_arr

    def forward(self, cur_loc, cur_dir):
        if cur_dir == 'N':
            ret_loc = (cur_loc[0], cur_loc[1] + 1)
        elif cur_dir == 'E':
            ret_loc = (cur_loc[0] + 1, cur_loc[1])
        elif cur_dir == 'W':
            ret_loc = (cur_loc[0] - 1, cur_loc[1])
        elif cur_dir == 'S':
            ret_loc = (cur_loc[0], cur_loc[1] - 1)
        ret_loc = (min(max(ret_loc[0], 0), self.size - 1), min(max(ret_loc[1], 0), self.size - 1))
        return ret_loc, cur_dir

    def backward(self, cur_loc, cur_dir):
        if cur_dir == 'N':
            ret_loc = (cur_loc[0], cur_loc[1] - 1)
        elif cur_dir == 'E':
            ret_loc = (cur_loc[0] - 1, cur_loc[1])
        elif cur_dir == 'W':
            ret_loc = (cur_loc[0] + 1, cur_loc[1])
        elif cur_dir == 'S':
            ret_loc = (cur_loc[0], cur_loc[1] + 1)
        ret_loc = (min(max(ret_loc[0], 0), self.size - 1), min(max(ret_loc[1], 0), self.size - 1))
        return ret_loc, cur_dir

    @staticmethod
    def turnright(cur_loc, cur_dir):
        dir_to_idx = {'N': 0, 'E': 1, 'S': 2, 'W': 3}
        dirs = ['N', 'E', 'S', 'W']
        idx = (dir_to_idx[cur_dir] + 1) % 4
        return cur_loc, dirs[idx]

    @staticmethod
    def turnleft(cur_loc, cur_dir):
        dir_to_idx = {'N': 0, 'E': 1, 'S': 2, 'W': 3}
        dirs = ['N', 'E', 'S', 'W']
        idx = (dir_to_idx[cur_dir] + 4 - 1) % 4
        return cur_loc, dirs[idx]
