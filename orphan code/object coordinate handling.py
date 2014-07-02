"""
Created on Tue July 2 17:00:00 2014

@author: Isaiah Bell
Copyright (c) 2014 
Released under MIT License
"""

import VectorMath
''' test interaction object '''


class InteractionSpace(object):
    '''Define volumes and valid interations for human input

    Create a volume in space that control actions can be bound to.
    Valid interactions are defined in the scope of the InteractionSpace object.
    Each instance handles detection of gestures and should output a clear signal
    when a valid gesture is detected.

    '''
    def __init__(self,CENTER = (0,0,0),WIDTH = 0,HEIGHT = 0,DEPTH = 0,\
    			 NORMAL = (0,1,0)):
        
        '''These values are in Leap coordinates'''
        self.center = CENTER 
        self.normal = NORMAL # keep this as a tuple, this should not be changing

        '''These values are in local coordinates'''
        self.width = WIDTH
        self.height = HEIGHT
        self.depth = DEPTH

        '''These are values that have nothing to do with reference frame'''
        self.gain = 10
    
    def is_valid(self,frame_data):
        return True #temporary value for testing

    def convert_to_local_frame(vector)