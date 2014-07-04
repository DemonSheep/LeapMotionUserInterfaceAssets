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
sys.path
import VectorMath

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
        if index == -1:
            return self.queue.pop()
        else:
            try:
                return self.queue.pop(index)
            except IndexError: # if the index is invalid  then nothing happens
                pass
            
'''HANDLE USER INPUT ######################################################## '''
class InteractionHandler(object):
    
    def __init__(self):
        mybuffer = Buffer()
        mytimer = TimeKeeper()
    
    def poll_interface_elements(self,list_of_elements,frame_data):
        if frame_data:        
            temp_list = []        
            for element in list_of_elements:
                try:
                    if element[0].is_valid(frame_data):
                        temp_list.append(element)
                except AttributeError as error:
                    print error
                    
        return temp_list
        
    def run_interaction_detection(self,list_of_valid_elements,frame_data):      
        if list_of_valid_elements:  
            for element in list_of_valid_elements:
                #print element                
                element[0].update(frame_data) # run the button call back
                #print element[1]                
                element[1]()
                    

class InteractionSpace(object):
    '''Define volumes and valid interations for human input

    Create a volume in space that control actions can be bound to.
    Valid interactions are defined in the scope of the InteractionSpace object.
    Each instance handles detection of gestures and should output a clear signal
    when a valid gesture is detected.

    '''
    def __init__(self,CENTER = (0,0,0),WIDTH = 0,HEIGHT = 0,DEPTH = 0,NORMAL = (0,1,0)):
        self.center = CENTER
        self.width = WIDTH
        self.height = HEIGHT
        self.depth = DEPTH
        self.gain = 10
        self.normal = NORMAL # keep this as a tuple, this should not be changing
    
    def is_valid(self,frame_data):
        return True #temporary value for testing

    def convert_to_local_frame(vector)



class CubicButton(InteractionSpace):
    '''Create a button that can be pressed by moving fingers through a touch plane
    The button is in the form of an axis aligned rectangular prism in space

    Attributes:
        center = (x,y,z) center of button is  equidistant from all sides
        width  = width of the button, measured along x-axis
        height = height of the button, measured along the y-axis
        depth  = depth of the button, measured along the z-axis
        press_direction = unit vector normal to press plane
        
    '''
    def __init__(self,CENTER = (0,0,0),WIDTH = 100,HEIGHT = 100,DEPTH = 50,PRESS_DIRECTION = (0,0,-1)):
        super(CubicButton,self).__init__(CENTER = CENTER,WIDTH = WIDTH, HEIGHT = HEIGHT, DEPTH = DEPTH )
        self.press_direction = PRESS_DIRECTION
        self.button_buffer = Buffer()       
        
        
    def is_valid(self,frame_data):
        return False #temp value for testing
    
    def update(self,frame_data):
        '''
        This is where the button decides if the user is interacting with it
        '''        
        self.button_buffer.enqueue(frame_data)
        
        
class Slider(InteractionSpace):
    '''Create a slider that producess a linear output with position
    
    Attributes:
        center = (x,y,z) center of button is  equidistant from all sides
        width  = width of the button, measured along x-axis
        height = height of the button, measured along the y-axis
        depth  = depth of the button, measured along the z-axis
        normal_direction = unit vector normal to slider plane
        enforce_slider_normal = [True]  
    '''
    def __init__(self,CENTER = (0,0,0),WIDTH = 100,HEIGHT = 100,DEPTH = 50,NORMAL_DIRECTION = (0,1,0)):
        super(Slider,self).__init__(CENTER=CENTER,WIDTH = WIDTH, HEIGHT = HEIGHT, DEPTH = DEPTH )
        self.normal_direction = NORMAL_DIRECTION
        self.enforce_slider_normal = True
        self.angle_limit = 15 # angle of cone from normal
        self.slider_value = 0
        self.buff = Buffer()
        self.gain = 1
        self.hand_id = None
        # figure out which direction the slider works in
        # direction is the largest dimension orthagonal to normal_direction        
        if self.normal_direction[0] != 0:
            if self.depth >= self.height: #prefer flat sliders
                self.long_side = [self.depth,2]
            else:
                self.long_side = [self.heigh,1]
        elif self.normal_direction[1] != 0:
            if self.width >= self.depth:
                self.long_side = [self.width,0]
            else:
                self.long_side = [self.depth,2]
        else:
            if self.width >= self.height: # prefer flat sliders
                self.long_side = [self.width, 0]
            else:
                self.long_side = [self.height,1]
                
            
                
        
        
    def is_valid(self,frame_data):
        for hand in frame_data.hands:
            if (self.center[0]-self.width/2) <= hand.palm_position[0] <= (self.center[0]+self.width/2):
                if (self.center[1]-self.height/2) <= hand.palm_position[1] <= (self.center[1]+self.height/2):
                    if (self.center[2]-self.depth/2) <= hand.palm_position[2] <= (self.center[2]+self.depth/2):
                        self.frame_data = frame_data
                        self.buff.enqueue(frame_data)
                        self.hand_id = hand.id                        
                        return True
                
        return False
            
                        
    def update(self,not_used):
        NUMBER_OF_SPOTS = 20   
        if self.enforce_slider_normal is True:
            
            '''
            Calculate the angle mismatch from between the palm normal and the slider normal
            if the two vectors are not parallel within angle_limit AND oriented opposite directions
                then nothing will happen
            
            '''
            for hand in self.frame_data.hands:            
                if hand.id == self.hand_id:                    
                    palm_normal = hand.palm_normal
                    slider_normal = Leap.Vector(*self.normal_direction)
                    angle = 180-self.angle_limit
                    if hand.sphere_radius >= 50:
                        if palm_normal.angle_to(slider_normal)*57.3 >= angle:
                            if self.long_side[0] == self.depth:
                                temp = (-hand.palm_position[self.long_side[1]])/(self.long_side[0]/NUMBER_OF_SPOTS)*self.gain +NUMBER_OF_SPOTS/2
                            else:
                                temp = hand.palm_position[self.long_side[1]]/(self.long_side[0]/NUMBER_OF_SPOTS)*self.gain +NUMBER_OF_SPOTS/2
                            self.slider_value = int(temp)
                            
                        else:
                            print 'not aligned'
                            return
                else:
                    pass
        else:
            for hand in self.frame_data.hands:            
                if hand.id == self.hand_id: 
                    if hand.sphere_radius >= 50:            
                        if self.long_side[0] == self.depth:
                            temp = -hand.palm_position[self.long_side[1]]/(self.long_side[0]/NUMBER_OF_SPOTS)*self.gain +NUMBER_OF_SPOTS/2
                        else:
                            temp = hand.palm_position[self.long_side[1]]/(self.long_side[0]/NUMBER_OF_SPOTS)*self.gain +NUMBER_OF_SPOTS/2
                        self.slider_value = int(temp)
                else:
                    pass
            
        
class PlanarPosition(InteractionSpace):
        '''Create a Planar Position sensor that producess a linear output with position in a plane
    
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
        The Planar object has two outputs, an x and y component of measured 
        movement in the PlanarPosition object's own reference frame. The  
        reference frame is determined from the normal vector. The raw input 
        from the Leap will be converted into local reference frame coordinates.
        '''
    def __init__(self,CENTER = (0,0,0),WIDTH = 100,HEIGHT = 100,DEPTH = 50,NORMAL_DIRECTION = (0,1,0)):
        super(PlanarPosition,self).__init__(CENTER=CENTER,WIDTH = WIDTH, HEIGHT = HEIGHT, DEPTH = DEPTH)

    def is_valid(self,frame_data):
        #in this version of is_valid
        for hand in frame_data.hands:
            position = hand.palm_position
            if super(PlanarPosition,self).is_valid(position):
                #!!scSIDE EFFECTS!! update state