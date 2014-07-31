# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 15:54:42 2014

@author: Isaiah Bell
Copyright (c) 2014
Released under MIT License
"""

from types import ListType

class RobotController(object):
    '''
    Bundle the instances used to control a robot
    '''
    def __init__(self):
        self.myeffector = EndEffector()
        self.myenvironment = Environment()

class EndEffector(object):
    '''
    Defines the position and velocity of an end effector with Cartesian coordianates
        position = [x-cord , y-cord , angle with x-axis, angle with y-axis, angle with z-axis
        velocity = [vx,vy,vz,omega_x,omega_y,omega_z]
        reaction time = the time step evaluated when updating position with velocity base controls
            if the position will enter unsafe area in the time step then the position will not be
            updated and the user will be notified visually
    '''

    def __init__(self,position = (0,0,0,0,0,0),velocity = (0,0,0,0,0,0),reaction_time=0.1):
        self.position = list(position)
        self.velocity = list(velocity)

        self.react_time = reaction_time

    def update_velocity(self,velocity = (0,0,0,0,0,0)):
        for k,v in enumerate(velocity):
            self.velocity[k] = v



    def update_position(self,delta_time,increment=(0,0,0,0,0,0) ,environment=None):
        e = environment
        def f(dt,dx,x):
            x = list(x) # cast the position to a list so we can change it
            for k,v in enumerate(dx):
                x[k] += (v + dt*self.velocity[k])
            return x

        if e is None: # if an environment is
            for index,value in enumerate(increment):
                self.position[index] += value
                self.position[index] += self.velocity[index]*delta_time

        elif type(e) is not Environment:
            print 'Type Error: you must use an Environment object'

        elif e.is_valid_move(f(delta_time,increment,self.position)): #check to see if the move is valid
            self.position = f(delta_time,increment,self.position)

        else:
            print"not a valid move"


class Gripper(EndEffector):
    '''Is a simple parallel jaw gripper, has two states: Open/Closed'''
    def __init__(self):
        self.is_open = None

    def make_open(self):
        self.is_open = True

    def make_closed(self):
        self.is_open = False
        
class Environment(object):
    '''A voxel format that describes the valid places for a robot to be
    Work In Progress'''
    def is_valid_move(self,goal_coord):
        try:
            assert type(goal_coord) == ListType
        except AssertionError:
            goal_coord = list(goal_coord)
        # for testing purposes only, makes the move valid
        return True    
