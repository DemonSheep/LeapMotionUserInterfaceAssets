# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 15:39:48 2014

@author: Isaiah Bell
Copyright (c) 2014
Released under MIT License
"""

from InteractionObjects import CubicButton,Slider,PlanarPosition,ThreeDimensionPosition
from Coroutines import coroutine

class KeyBinding(object):
    '''
    Store a list of every interaction object and binds output to some other function call
    
    To add an interaction instance:
        name = [InteractionObject(), callback_for_interaction_instance()] 
    '''
    def __init__(self): # got rid of robot intance
        '''Define the virtual control panel in Leap interaction space and link to CALLBACKS

            Define the callback:
            =======================
                Create a class attribute that can be used as a target. 
                Note that the actual call back definitions are intended private attributes.
                Other coroutine will use callback_target to send data in.

                    self.callback_target = self._actual_callback()

            Package instance and callback:
            ===================================

        '''
        self.update_position = _self._update_position
        self.positon_sphere = ThreeDimensionPosition(self,CENTER = (0,180,0),WIDTH = 300,HEIGHT = 300,DEPTH = 300,NORMAL_DIRECTION = (0,1,0),callback = position_frame,shape = 'ellipsoid')

        '''Make the list of all UI elements '''

        self.UE_list = 
                               
    '''BUTTON CALLBACKS ************************************************'''

    @coroutine 
    def _update_position(self):


        while True:
            args,kwargs = (yield)




    def joint_control(self):
        
        


