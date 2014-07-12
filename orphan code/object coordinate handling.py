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
        # when we initialize we set up local coordinates
        self.local_basis = VectorMath.generate_basis(normal_vector)


        '''These are values that have nothing to do with reference frame'''
        self.gain = 1


    
    def is_valid(self,position):
        '''Determine if a position given in Leap reference frame is inside 
        Interaction volume

        Parameters:
        =============
            position = (x,y,z) position in Leap frame of reference

        '''
        #convert Leap frame to local frame
        local_position = convert_to_local_coordinates(position, basis = self.local_basis)
        # check the bounds of the volume with our local_position
        if (self.center[0]-self.width/2) <= local_position[0] <= (self.center[0]+self.width/2):
            if (self.center[1]-self.depth/2) <= local_position[1] <= (self.center[1]+self.depth/2):
                if (self.center[2]-self.height/2) <= local_position[2] <= (self.center[2]+self.height/2):                       
                    return True
                
        return False

    def convert_to_local_coordinates(self,coordinates,basis = self.local_basis):
    	# find the relative vector from local origin to leap point
    	relative_vector = [value-self.center[index] for index,value in enumerate(coordinates)]
    	local_coordinates = VectorMath.decompose_vector(relative_vector,basis)
        return local_coordinates
