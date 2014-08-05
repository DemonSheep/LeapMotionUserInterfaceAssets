# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 15:39:48 2014

@author: Isaiah Bell
Copyright (c) 2014
Released under MIT License
"""

from InteractionObjects import LargerPositionVelocityCombination,BlockingThreeDimensionPosition
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
        self.switch_node = self._control_distributer()
        self.containing_sphere = LargerPositionVelocityCombination(CENTER = (0,250,0),WIDTH = 400,HEIGHT = 400,DEPTH = 400,NORMAL_DIRECTION = (0,1,0),
                                                                    callback = self.switch_node,shape = 'ellipsoid')

        self.emergency_stop_callback = self._emergency_stop

        self.centering_gate = BlockingThreeDimensionPosition(CENTER = (0,250,0),WIDTH = 175,HEIGHT = 175,DEPTH = 175,NORMAL_DIRECTION = (0,1,0),
                                                            callback = self.emergency_stop_callback, embedded_parent = self.containing_sphere, shape = 'rectangle')

        '''Make the list of all UI elements '''

        self.UE_list = [self.centering_gate]
        ''' Make some flags for the GUI to hook into'''

        self.fee_flag = True
        self.pee_flag = False
        self.jc_flag = False
        self.gc_flag = False


    '''BUTTON CALLBACKS ************************************************'''

    @coroutine
    def _control_distributer(self):
        update_pos = self._update_position()
        joint_control = self._joint_control()
        pure_grip = self._pure_grip()
        while True:
            args,kwargs = (yield)
            if self.fee_flag or self.pee_flag:
                update_pos.send((args,kwargs))
            elif self.jc_flag:
                joint_control.send((args,kwargs))
            elif self.gc_flag:
                pure_grip.send((args,kwargs))
            else:
                print 'all flags are false'

        

    @coroutine 
    def _update_position(self):
        prev_x = 0
        prev_y = 0
        prev_z = 0
        prev_center = None
        UNIT_SCALE_FACTOR = 0.001
        #this is where we get the current position
        #for now we leave this as a tuple
        current_position = [0,0,0,0,0,0]
        while True:
            args,kwargs = (yield)
            print '*'*30
            x = self.containing_sphere.smoothed_x
            y = self.containing_sphere.smoothed_y
            z = self.containing_sphere.smoothed_z
            gain = self.containing_sphere.gain_object.gain
            print gain
            if prev_center is None:
                prev_center = self.containing_sphere.center
            #check that the center has not moved
            if self.containing_sphere.center != prev_center:
                #if it has moved then reupdate the prev components
                prev_center = self.containing_sphere.center
                prev_x,prev_y,prev_z = (0,0,0)
            
            delta_x = (x - prev_x)*self.containing_sphere.gain_object.gain
            delta_y = (y - prev_y)*self.containing_sphere.gain_object.gain
            delta_z = (z - prev_z)*self.containing_sphere.gain_object.gain
            #now update the previous point
            prev_x = x
            prev_y = y
            prev_z = z
            current_position[0] += delta_x
            current_position[1] += delta_y
            current_position[2] += delta_z
            if self.fee_flag:
                print 'fee',current_position
                #callback_ep('frame_end_effector',current_position)
            elif self.pee_flag:
                print 'pee', current_position
                #callback_ep('point_end_effector',current_position)


    @coroutine
    def _pure_grip(self):
        while True:
            foo = (yield)
            print 'in grip'

    def _emergency_stop(self):
        print 'emergency_stop'
        print 'Flag:',self.containing_sphere.hand_command_valid
        pass

    @coroutine
    def _joint_control(self):
        while True: 
            foo = (yield)
            print 'jc'
        


