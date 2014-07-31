# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 15:38:58 2014

@author: Isaiah Bell
Copyright (c) 2014 
Released under MIT License
"""
import Leap
import time
import sys
import VectorMath
#figure out these import statements
import Coroutines
from Coroutines import coroutine

c = Leap.Controller  #reference the class
control = c() # create a new instance of class

def get_data():
    #test to see if controller is on
    if (c.is_connected): # read property object is_connected of controller class
        if (c.has_focus): # read property object has_focus of controller class
            return control.frame() # create a  new instace of frame


        else:
            print 'does not have focus\n'
            time.sleep(1)
    else:
        print "Sleeping, no connection\n"
        time.sleep(1)

class TimeKeeper(object):
    '''Keep track of time since last called

    Time is just a number, does not use system time.

    delta_time(current_time): returns time since delta_time() was last called.
    '''

    def __init__(self):
        self.now_time = 0
        self.prev_time = None
    def delta_time(self,current_time):
        self.now_time = current_time
        if self.prev_time is None:
            self.prev_time = self.now_time
            return (0, False)
        else:
            foo = self.now_time - self.prev_time
            self.prev_time = self.now_time #update the times
        return (foo,True)

class Buffer(object):
    '''Create a First In First Out bounded queue to store objects
        buffer_size (default = 10) is number of objects in queue
    '''
    def __init__(self, buffer_size = 10):
        self.queue = []
        self.buffer_size = 10

    def enqueue(self,some_object):
        '''
        Insert an object to beginning [index=0] of the queue
        Return True on success
        '''
        assert (self.buffer_size > 0), 'Can not have a negative index buffer'
        assert len(self.queue) >= 0, 'Queue must exist'
        if len(self.queue) == self.buffer_size:
            self.queue.pop()
            self.queue.insert(0,some_object)
            return True
        elif len(self.queue) < self.buffer_size:
            self.queue.insert(0,some_object)
            return True
        elif len(self.queue) > self.buffer_size:
            self.queue.insert(0,some_object)
            while len(self.queue) > self.buffer_size:
                self.queue.pop()
            return True
        else:
            return False

    def dequeue(self,index = -1):
        '''
        Remove and return the object in the queue at the specified index

        '''
        try:
            return self.queue.pop(index)
        except IndexError: # if the index is invalid  then nothing happens
            pass
            
'''HANDLE USER INPUT ######################################################## '''

class InteractionSpace(object):
    #create some global flag variables so different interation objects can talk.

    hand_command_valid = False

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
        self.normal_direction = NORMAL # keep this as a tuple, this should not be changing

        '''These values are in local coordinates'''
        self.width = WIDTH
        self.height = HEIGHT
        self.depth = DEPTH
        # when we initialize we set up local coordinates
        self.local_basis = VectorMath.generate_basis(self.normal_direction)


        '''These are values that have nothing to do with reference frame'''
        self.gain = 1

    def convert_to_local_coordinates(self,coordinates,basis):
    	# find the relative vector from local origin to leap point
    	relative_vector = [value-self.center[index] for index,value in enumerate(coordinates)]
    	local_coordinates = VectorMath.decompose_vector(relative_vector,basis)
        return local_coordinates

    @coroutine
    def _data_listener(self,target):
        while True:
            #this is where the class instance gets injected
            frame = (yield)
            args = [self,frame]
            kwargs = {}
            target.send((args,kwargs))

class CubicButton(InteractionSpace):
    '''Create a button that can be pressed by moving fingers through a touch plane
    The button is in the form of an axis aligned rectangular prism in space

    Attributes:
        center = (x,y,z) center of button is  equidistant from all sides
        width  = width of the button, measured along x-axis
        depth = depth of the button, measured along the y-axis
        height  = height of the button, measured along the z-axis
        press_direction = unit vector normal to press plane
        
    '''
    def __init__(self,CENTER = (0,0,0),WIDTH = 100,HEIGHT = 100,DEPTH = 100,PRESS_DIRECTION = (0,0,-1),callback = None):
        super(CubicButton,self).__init__(CENTER = CENTER,WIDTH = WIDTH, HEIGHT = HEIGHT, DEPTH = DEPTH, NORMAL = PRESS_DIRECTION)
        self.press_direction = PRESS_DIRECTION
        self.button_buffer = Buffer()    
        ###########################################
        if callback is None:
            callback = Coroutines._sink()
        '''Setup the data path'''
        update = self.updating_path(callback)
        valid_path = self.is_valid_path(update)
        self.data_listener = self._data_listener(valid_path)

            
    def is_valid_path(self,target):
        #send target to last member
        end = Coroutines._single_check_bounding_box_pointable(target)
        pipeA = Coroutines._single_finger_tip_position(end)
        pipeB = Coroutines._single_enforce_specific_finger(pipeA,'Index')
        beginning = Coroutines._single_select_a_hand(pipeB,'Right')
        return beginning

    
    def updating_path(self,callback):
        beginning = Coroutines._pass_arguments(callback)
        return beginning 

        
        
class Slider(InteractionSpace):
    '''Create a slider that producess a linear output with position
    
    Attributes:
        center = (x,y,z) center of button is  equidistant from all sides
        width  = width of the button, measured along x-axis
        depth = depth of the button, measured along the y-axis
        height  = height of the button, measured along the z-axis
        normal_direction = unit vector normal to slider plane
        enforce_slider_normal = [True]  
    '''
    def __init__(self,CENTER = (0,0,0),WIDTH = 100,HEIGHT = 100,DEPTH = 50,NORMAL_DIRECTION = (0,1,0),callback = None):
        super(Slider,self).__init__(CENTER=CENTER,WIDTH = WIDTH, HEIGHT = HEIGHT, DEPTH = DEPTH,NORMAL = NORMAL_DIRECTION )
        self.buff = Buffer()
        self.gain = 1
        # figure out which direction the slider works in
        # direction is the largest dimension orthagonal to normal_direction        
        if self.width >= self.depth:
            #integer to represent the index to clamp
            self.slider_direction = 'x'
        else:
            self.slider_direction = 'y'

        if callback is None:
            callback = Coroutines._sink()
        '''Setup the data path'''
        update = self.updating_path(callback)
        valid_path = self.is_valid_path(update)
        self.data_listener = self._data_listener(valid_path)                
               
    def is_valid_path(self,target):
        end = Coroutines._enforce_hand_sphere_radius(target,-50)
        pipeA = Coroutines._prefer_older_pointable(end)
        pipeB = Coroutines._check_bounding_box_all_pointable(pipeA)
        pipeC = Coroutines._hand_palm_position(pipeB)
        beginning = Coroutines._add_hands_to_pointable_list(pipeC)
        return beginning
                        
    def updating_path(self,callback):
        beginning = Coroutines._simple_one_axis_position_from_position(callback,self.slider_direction,20)
        return beginning
     
class PlanarPosition(InteractionSpace):
    '''Create a Planar Position sensor that producess a linear output with position in a plane
    
    Attributes:
    ==================
        center = (x,y,z) center of button is  equidistant from all sides
        width  = width of the button, measured along x-axis
        depth = depth of the button, measured along the y-axis
        height  = height of the button, measured along the z-axis
        normal_direction = unit vector normal to plane
        enforce_planar_normal = Boolean to determine whether hand orientation is 
            used to determine sucessful interaction.

    Behaviour:
    ==================
        The Planar object has two outputs, an x and y component of measured 
        movement in the PlanarPosition object's own reference frame. The  
        reference frame is determined from the normal vector. The raw input 
        from the Leap will be converted into local reference frame coordinates.
        '''

    def __init__(self,CENTER = (0,0,0),WIDTH = 100,HEIGHT = 100,DEPTH = 50,NORMAL_DIRECTION = (0,1,0),callback = None):
        super(PlanarPosition,self).__init__(CENTER=CENTER,WIDTH = WIDTH, HEIGHT = HEIGHT, DEPTH = DEPTH,NORMAL = NORMAL_DIRECTION)

        if callback is None:
            callback = Coroutines._sink()
        '''Setup the data path'''
        update = self.updating_path(callback)
        valid_path = self.is_valid_path(update)
        self.data_listener = self._data_listener(valid_path) 

    def is_valid_path(self,target):
        end = Coroutines._enforce_hand_sphere_radius(target,-50)
        pipeA = Coroutines._prefer_older_pointable(end)
        pipeB = Coroutines._check_bounding_box_all_pointable(pipeA)
        pipeC = Coroutines._hand_palm_position(pipeB)
        beginning = Coroutines._add_hands_to_pointable_list(pipeC)
        return beginning
                        
    def updating_path(self,callback):
        end = Coroutines._simple_one_axis_position_from_position(callback,'x',30)
        beginning = Coroutines._simple_one_axis_position_from_position(end,'y',20)
        #start = Coroutines._pass_arguments(beginning)

        return beginning
    

class ThreeDimensionPosition(InteractionSpace):
    '''Create a 3D Position sensor that producess a linear output with position in a plane
    
    Attributes:
    ==================
        center = (x,y,z) center of button is  equidistant from all sides
        width  = width of the button, measured along x-axis
        height = height of the button, measured along the y-axis
        depth  = depth of the button, measured along the z-axis
        normal_direction = unit vector normal to plane
        enforce_planar_normal = Boolean to determine whether hand orientation is 
            used to determine sucessful interaction.

    Behaviour:
    ==================
        The ThreeDimensionPosition object has three outputs, an x, y, and z component of measured 
        movement in the ThreeDimensionPosition object's own reference frame. The  
        reference frame is determined from the normal vector. The raw input 
        from the Leap will be converted into local reference frame coordinates.
        '''

    def __init__(self,CENTER = (0,0,0),WIDTH = 100,HEIGHT = 100,DEPTH = 50,NORMAL_DIRECTION = (0,1,0),callback = None,shape = 'rectangle'):
        super(ThreeDimensionPosition,self).__init__(CENTER=CENTER,WIDTH = WIDTH, HEIGHT = HEIGHT, DEPTH = DEPTH, NORMAL = NORMAL_DIRECTION)
        
        self.shape = shape

        if callback is None:
            callback = Coroutines._sink()
        '''Setup the data path'''
        update = self.updating_path(callback)
        valid_path = self.is_valid_path(update)
        self.data_listener = self._data_listener(valid_path) 

    def is_valid_path(self,target):
        end = Coroutines._enforce_hand_sphere_radius(target,-50)
        pipeA = Coroutines._prefer_older_pointable(end)
        #setup if stements by frequecy for speed
        #small startup performance hit is better than whole new class that changes one line
        if self.shape.lower() == 'rectangle': 
            pipeB = Coroutines._check_bounding_box_all_pointable(pipeA)
        elif self.shape.lower() == 'ellipsoid':
            pipeB = Coroutines._check_bounding_ellipsoid_all_pointable(pipeA)
        elif self.shape.lower() == 'cylinder':
            pipeB = Coroutines._check_bounding_cylinder_all_pointable(pipeA)
        else:
            raise RuntimeError,'need to pick a valid shape type'
        pipeC = Coroutines._hand_palm_position(pipeB)
        beginning = Coroutines._add_hands_to_pointable_list(pipeC)
        return beginning
                        
    def updating_path(self,callback):
        end = Coroutines._simple_one_axis_position_from_position(callback,'x',30)
        pipeA = Coroutines._simple_one_axis_position_from_position(end,'y',20)
        beginning = Coroutines._simple_one_axis_position_from_position(pipeA,'z',20)
        #start = Coroutines._pass_arguments(beginning)

        return beginning

class TwoDimensionConeAngle(InteractionSpace):
    '''Create a volume that 

    '''


'''##################### Custom Versions of Interaction Objects ############################'''

class BlockingThreeDimensionPosition(ThreeDimensionPosition):

    def __init__(self, CENTER = (0,0,0), WIDTH = 50,HEIGHT = 50,DEPTH = 50,NORMAL_DIRECTION = (0,1,0),
                callback = None, embedded_parent = None, shape = 'rectangle'):

        super(ThreeDimensionPosition,self).__init__(CENTER=CENTER,WIDTH = WIDTH, HEIGHT = HEIGHT, DEPTH = DEPTH, NORMAL = NORMAL_DIRECTION)
        
        self.shape = shape
        if embedded_parent is not None:
            self.actual_position_sensor = embedded_parent
        else:
            raise RuntimeError 

        self.interacting_id = None

        self.emergency_stop = callback

        #make sure that all child  elements get the emergency stop
        self.actual_position_sensor.emergency_stop = self.emergency_stop


        self.timer_block = self._timer_block()
        
        if callback is None:
            callback = Coroutines._sink()
        '''Setup the data path'''
        valid_path = self.is_valid_path()
        self.data_listener = self._data_listener(valid_path)


    def is_valid_path(self):
        #this is the branch for the updating and positon calcualting

        branch2pipeA = self.actual_position_sensor.custom_receive_hand_and_frame #NOTE on this line we are using a custom landing coroutine to process our custom stream
        targetA = self._check_for_preferred_pointable(branch2pipeA)
        #this is the branch for finding a new pointable to use for control
        branch1pipeC = Coroutines._prefer_older_pointable(self.timer_block)
        if self.shape.lower() == 'rectangle': 
            branch1pipeB = Coroutines._check_bounding_box_all_pointable(branch1pipeC)
        elif self.shape.lower() == 'ellipsoid':
            branch1pipeB = Coroutines._check_bounding_ellipsoid_all_pointable(branch1pipeC)
        elif self.shape.lower() == 'cylinder':
            branch1pipeB = Coroutines._check_bounding_cylinder_all_pointable(branch1pipeC)
        else:
            raise RuntimeError,'need to pick a valid shape type'
        branch1pipeA = Coroutines._hand_palm_position(branch1pipeB)
        targetB = Coroutines._add_hands_to_pointable_list(branch1pipeA)
        #wrapping the flags in lambda so we will evaluate them every loop
        hand_valid = lambda : InteractionSpace.hand_command_valid
        not_hand_valid = lambda : not InteractionSpace.hand_command_valid
        beginning = Coroutines._simple_switch_node(targetA,targetB,condition_A = hand_valid,condition_B = not_hand_valid)
        return beginning

    def updating_path(self,target):
        #overide because we dont want it doing anything unexpected
        pass

    @coroutine
    def _check_for_preferred_pointable(self,target):
        #here we look at all pointables in the frame and see if one of them was 
        while True:
            args,kwargs = (yield)
            frame = args[1]
            if self.interacting_id is not None:
                temp_dict = {x.id : x for x in frame.hands}
                if self.interacting_id in temp_dict:
                    hand = temp_dict[self.interacting_id]
                    #add the specific hand to pointable_list
                    kwargs['pointable_list'] = [{'object':hand,'type':'HAND'}]
                    target.send((args,kwargs))

                else:
                    #the preferred pointable was not visible so we stop control input.
                    InteractionSpace.hand_command_valid = False
                    #call the emergency stop option
                    self.emergency_stop()

    @coroutine
    def _timer_block(self):
        my_id = None
        start_time = None
        delay_in_microseconds = 1000000
        while True:
            args,kwargs = (yield)
            frame = args[1]
            if (not kwargs['pointable_list']) or InteractionSpace.hand_command_valid:
                continue

            if self.interacting_id == my_id:
                #check the time
                if start_time is not None:
                    if frame.timestamp - start_time > delay_in_microseconds:
                        InteractionSpace.hand_command_valid = True
                        #reset the counter so next tiem we will start counting again
                        start_time = None
                        position = kwargs['pointable_list'][0]['object'].palm_position
                        print 'setting center=',position
                        self.actual_position_sensor.center = (position[0],position[1],position[2])
                else:
                    start_time = frame.timestamp
            else:
                my_id = self.interacting_id
                start_time = frame.timestamp


class LargerPositionVelocityCombination(ThreeDimensionPosition):

    def __init__(self,CENTER = (0,0,0),WIDTH = 300,HEIGHT = 300,DEPTH = 300,NORMAL_DIRECTION = (0,1,0),callback = None,shape = 'ellipsoid'):

        super(ThreeDimensionPosition,self).__init__(CENTER=CENTER,WIDTH = WIDTH, HEIGHT = HEIGHT, DEPTH = DEPTH, NORMAL = NORMAL_DIRECTION)
        end = callback
        update = self.updating_path(end)
        valid_path = self.is_valid_path(update)
        self.custom_receive_hand_and_frame = self._custom_receive_hand_and_frame(valid_path)

        self.smoothed_x = None
        self.smoothed_y = None
        self.smoothed_z = None

    def is_valid_path(self,target):
        hand_meets_criteria = target
        hand_fails_test = Coroutines._sink()
        pipeA = self._custom_enforce_hand_sphere_radius(hand_meets_criteria,hand_fails_test,50)
        beginning = Coroutines._hand_palm_position(pipeA)
        return beginning

        

    def updating_path(self,target):
        join1 = Coroutines._simple_joiner_node(target,merge = False,self_instance = None)
        join2 = Coroutines._simple_joiner_node(join1,merge = False,self_instance = None)
        updateX = Coroutines._moving_average_box_position_output(join1,'x',stdd_threshold = 1,buffer_length = 10)
        updateY = Coroutines._moving_average_box_position_output(join2,'y',stdd_threshold = 1,buffer_length = 10)
        updateZ = Coroutines._moving_average_box_position_output(join2,'z',stdd_threshold = 1,buffer_length = 10)
        split1 = Coroutines._simple_switch_node(updateY,updateZ,condition_A = True,condition_B = True)
        base_split = Coroutines._simple_switch_node(updateX,split1,condition_A = True,condition_B = True)
        return base_split


    @coroutine
    def _custom_receive_hand_and_frame(self,target):
        count = 0
        while True:
            args,kwargs = (yield)
            #overwrite the class instance to current instance
            args[0] = self
            #print 'before:',InteractionSpace.hand_command_valid
            target.send((args,kwargs))
            #print 'after:',InteractionSpace.hand_command_valid

    @coroutine
    def _custom_enforce_hand_sphere_radius(self,targetA,targetB,radius_limit):
        '''Remove hand objects from pointable_list that do not meet sphere radius inequality

        MODIFIES STREAM

        Casts both sides of comparison to integers for speed.
        The sphere_radius will not be used in a precise enough context 
        to justify the use of floating point operations

        Parameters:
        ============
            radius_limit: limit of hand.sphere_radius will be filtered on
                positive number --> hand.sphere_radius > radius_limit
                negative number --> hand.sphere_radius < abs(radius_limit)

            targetA = target if hand sphere radius inequality is True
            targetB = target if hand sphere radius inequality is False

        '''
        try:
            int(radius_limit)
        except ValueError:
            raise SyntaxError, 'ValueError: Must use a digit parameter for radius_limit'

        if cmp(radius_limit,0) == -1:
            radius_limit = -radius_limit # convert to positive number
            #define a function that acts as closure over radius comparison type
            def check_hand_sphere_radius(sphere_radius,index):
                if sphere_radius > radius_limit: # the opposite of what we want
                    #remove the offending hand object
                    kwargs['pointable_list'].pop(index)

        if cmp(radius_limit,0) == 1:
            #define a function that acts as closure over radius comparison type
            def check_hand_sphere_radius(sphere_radius,index): 
                if sphere_radius < radius_limit: # the opposite of what we want
                    #remove the offending hand object
                    kwargs['pointable_list'].pop(index)

        while True:
            args,kwargs = (yield)
            #check for a pointable_list
            if 'pointable_list' in kwargs.keys() and (kwargs['pointable_list']):
                for index,pointable in enumerate(kwargs['pointable_list']):
                    #check to see if the pointable is a hand
                    if pointable['type'] == 'HAND':
                        hand = pointable['object'] # add refrence for readability
                        sphere_radius = hand.sphere_radius
                        check_hand_sphere_radius(sphere_radius,index)
                    else:
                        continue # was not a hand so continue to look for one
            else:
                continue # stop pipe and yield beacuse there was no valid pointables
            if not kwargs['pointable_list']:
                #if the list is empty, the inequality was false for every instance then we divert to targetB
                #in this case we see a fail as a signal to abort commands
                self.emergency_stop()
                InteractionSpace.hand_command_valid = False
                continue
            else:
                targetA.send((args,kwargs))
