"""
Created on Tue Jul 9 8:00:00 2014

@author: Isaiah Bell
Copyright (c) 2014 
Released under MIT License
"""
import Leap
import time
import sys
import VectorMath

c = Leap.Controller  #reference the class
control = c() # create a new instance of class

def get_data():
    # test to see if controller is on
    if (c.is_connected): # read property object is_connected of controller class
        if (c.has_focus): # read property object has_focus of controller class
            return control.frame() # create a  new instace of frame
        else:
            print 'does not have focus\n'
            time.sleep(1)
    else:
        print "Sleeping, no connection\n"
        time.sleep(1)
        
def coroutine(func):
    def wrapper(*args,**kwargs):
        cc = func(*args,**kwargs)
        cc.next()
        return cc
    return wrapper

def frame_broadcaster(targets):
    frame = get_data()
    for target in targets:
        #loop over all our interaction objects and send them the frame data
        target.send(frame)

@coroutine
def _enforce_specific_finger(target,finger_name):#input shuld be a string
    '''Take a hand instance and select one finger in the hand pass down the pipeline
    
    '''

    finger_names = {'thumb':0,'index':1,'middle':2,'ring':3,'pinky':4}
    finger_name = finger_name.lower() #convert user input to expected form
    my_finger_type = finger_names[finger_name] # get the type value for the SDK
    while True:
        args,kwargs = (yield)
        # if there are pointables we will look for hands
        if 'pointable_list' in kwargs.keys() and kwargs['pointable_list']:
            #there is an object to do
            for pointable in kwargs['pointable_list']:
                if 'HAND' == pointable[1]:
                    hand = pointable[0]
                    # if the finger is not in the hand the below operaition will create an invalid finger object
                    fingers = hand.fingers
                    for test_finger in fingers:
                        if test_finger.type() == my_finger_type:
                            finger = test_finger
                            if finger.is_valid:
                                kwargs['finger'] = finger #add the finger and overwrite any existing fingers
                                break # there can only be one of each finger per hand, no pont in looking for more
                        else: #the finger we asked for is not the finger we are lookig at
                            continue #jump to next finger
                else:
                    continue # jump to next pointable and see if hand
        else: #we did not have a pointable list to look for fingers
            continue #return control up the pipeline
        target.send((args,kwargs))

@coroutine
def _finger_tip_position(target):
    while True:
        args,kwargs = (yield)
        if 'finger' in kwargs.keys():
            try:
                assert kwargs['finger'].is_valid == True #make sure finger object is a valid one
            except AssertionError:
                #there was a finger position but there was not a valid finger object
                #restart  the loop
                continue
            else:
                finger = kwargs['finger']
                del kwargs['finger'] # clean up
            #bone(3) is the code of TYPE_DISTAL, we are getting the tip of the finger
            finger_position = finger.bone(3).next_joint # get the position of the very end
            kwargs['position'] = finger_position
            target.send((args,kwargs))
        else:
            raise SyntaxError, r"You must send a finger object in stream: kwargs['finger'] = finger_object"

@coroutine
def _hand_palm_position(target):
    while True:
        args,kwargs = (yield)
        if 'pointable_list' in kwargs.keys(): # check for presence of pointables
            if not ('pointable_position_list' in kwargs.keys()):
                kwargs['pointable_position_list'] = [] # create the dictionary entry
            for pointable in kwargs['pointable_list']: # loop through all the objects
                if pointable[1] == 'HAND': #get only the hand pointable
                    hand = pointable[0] #grab out the hand object, only for readability
                    #getting palm position is whole point of this coroutine
                    palm_position = hand.palm_position
                    #explicitly built list because it is so short
                    kwargs['pointable_position_list'].append([pointable[0],pointable[1],palm_position])
                else: #type is wrong ss we continue the loop
                    continue
        else:
            continue #no pointables were in list so stop pipe and yield up line
        target.send((args,kwargs))
                    
@coroutine
def _enforce_hand_sphere_radius(target,radius_limit):
    '''Remove hand objects from pointable_list that do not meet sphere radius inequality

    Casts both sides of comparison to integers for speed.
    The sphere_radius will not be used in a precise enough context 
    to justify the use of floating point operations

    Parameters:
    ============
        radius_limit: limit of hand.sphere_radius will be filtered on
            positive number -> hand.sphere_radius > radius_limit
            negative number -> hand.sphere_radius < abs(radius_limit)

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
                if pointable[1] == 'HAND':
                    hand = pointable[0] # add refrence for readability
                    sphere_radius = hand.sphere_radius
                    check_hand_sphere_radius(sphere_radius,index)
                else:
                    continue # was not a hand so continue to look for one
        else:
            continue # stop pipe and yield beacuse there was no valid pointables
        target.self((args,kwargs))

@coroutine
def _select_a_hand(target,hand_name): # will take 'left' or 'right'
    if 'left' == hand_name.lower():
        hand_flag = True
    elif 'right' == hand_name.lower():
        hand_flag = False
    else:
        raise SyntaxError,"hand_name parameter must be either 'left' or 'right' "
    while True:
        args,kwargs = (yield)
        frame = args[1]
        if not('pointable_list' in kwargs.keys()):
            kwargs['pointable_list'] = []
        else:
            pass

        for hand in frame.hands:
            if (hand.is_left and hand_flag):# do xor to
                kwargs['pointable_list'].append([hand,'HAND'])
            elif hand.is_right ^ hand_flag: 
                kwargs['pointable_list'].append([hand,'HAND'])
            else:
                continue
        target.send((args,kwargs))

@coroutine
def _check_bounding_box_all_pointable(target):
    '''Determine if a position given in Leap reference frame is inside 
    Interaction volume

    Parameters:
    =============
        pointable_position_list = list of pointable objects to check against bounding box
            [[pointable_id_1,pointable_TYPE,(x1,y1,z1)],[pointable_id_2,pointable_TYPE,(x2,y2,z2)],....]

    Requires:
    =============
        must be passed a class instance that has following properties
            tuple self.center = (x,y,z)
            int self.width
            int self.depth
            int self.height
            function self.convert_to_local_coordinates()

    '''
    #convert Leap frame to local frame
    while True:
        args,kwargs = (yield)
        self = args[0]
        frame = args[1]
        #make a temporary list to store valid pointables
        valid_pointable_list = []
        #get the position from stream
        try:
            pointable_position_list = kwargs['pointable_position_list']
        except KeyError:
            # we go to outer loop because there is nothing to process
            continue
        else:
            #clean up stream
            del kwargs['pointable_position_list']
        for local_pointable in pointable_position_list:
            # look in the second index of each pointable for the preprocessed position
            position = local_pointable[2]
            #HOTFIX because Leap.Vector does not support iteration
            temp = [position[0],position[1],position[2]]
            #translate the position to local origin
            temp = [value - self.center[index] for index,value in enumerate(temp)]
            local_position = self.convert_to_local_coordinates(temp,self.local_basis)
            # check the bounds of the volume with our local_position
            #center is in Leap coordinates so we are careful with
            if (self.width/2) <= local_position[0] <= (self.width/2):
                if (self.depth/2) <= local_position[1] <= (self.depth/2):
                    if (self.height/2) <= local_position[2] <= (self.height/2): 
                        #the check passes so we append the pointable to the valid list
                        #pointable is a list
                        #only grab the id = local_pointable[0] and the type_name = local_pointable[1]
                        valid_pointable_list.append(local_pointable[0:2])
                        continue
            #place a new field with the 
            kwargs['valid_pointable_list'] = valid_pointable_list
            target.send((args,kwargs))

@coroutine
def _check_bounding_box_single_pointable(target):
    '''Determine if a position given in Leap reference frame is inside 
    Interaction volume

    Parameters:
    =============
        position = (x,y,z) position in Leap reference frame

    Requires:
    =============
        must be passed a class instance that has following properties
            tuple self.center = (x,y,z)
            int self.width
            int self.depth
            int self.height
            function self.convert_to_local_coordinates()

    '''
    #convert Leap frame to local frame
    while True:
        args,kwargs = (yield)
        self = args[0]
        frame = args[1]
        #make sure that we get a position
        assert ('position' in kwargs.keys()) == True
        position = kwargs['position']
        #HOTFIX because Leap.Vector does not support iteration
        temp = [position[0],position[1],position[2]]
        local_position = self.convert_to_local_coordinates(temp, basis = self.local_basis)
        # check the bounds of the volume with our local_position
        if (-self.width/2) <= local_position[0] <= (self.width/2):
            if (-self.depth/2) <= local_position[1] <= (self.depth/2):
                if (-self.height/2) <= local_position[2] <= (self.height/2): 
                    #the check passes so we send on the data to next step
                    target.send((args,kwargs))

@coroutine
def _prefer_older_pointable(target):
    '''Check the class instace if there is a pointable that is already interacting

    Requirements:
    ====================
        needs a class instance passed down throught args[0]
        class should have
            self.interacting_id = id of the pointable that was already interacting


    '''
    while True:
        args,kwargs = (yield)
        self = args[0]
        frame = args[1]

@coroutine
def _add_tools_to_pointable_list(target):
    '''Get all valid tools from frame and add to the pointable_list

    Parameters:
    =============
        frame = Leap.Frame object

    Pointable list formatting:
    ==============================
        [pointable,pointable_TYPE]

    '''
    while True:
        frame = args[1]
        if not 'pointable_list' in kwargs.keys():
            #if the list does not already exist then we add it in
            kwargs['pointable_list'] = []
        if frame.tools.is_empty:
            #the tool list is empty so we skip to end and dont add anything to list
            pass
        else:
            for tool in frame.tools:
                pointable = tool
                pointable_TYPE = 'TOOL'
                #collect the variables into one list to append
                kwargs['pointable_list'].append([pointable,pointable_TYPE])
        target.send((args,kwargs))

@coroutine
def _add_hands_to_pointable_list(target):
    '''Get all valid hands from frame and add their palm to the pointable_position_list

    Parameters:
    =============
        frame = Leap.Frame object

    Pointable list formatting:
    ==============================
        [pointable,pointable_TYPE]

    '''
    while True:
        frame = args[1]
        if not 'pointable_position_list' in kwargs.keys():
            #if the list does not already exist then we add it in
            kwargs['pointable_position_list'] = []
        if frame.hands.is_empty:
            #the tool list is empty so we skip to end and dont add anything to list
            pass
        else:
            for hand in frame.hands:
                pointable = hand
                pointable_TYPE = 'HAND'
                #collect the variables into one list to append
                kwargs['pointable_list'].append([pointable,pointable_TYPE])
        target.send((args,kwargs))   

@coroutine
def _pass_arguments(target):
    while True:
        args,kwargs = (yield)
        #print 'Just passing through'
        target.send((args,kwargs))

@coroutine
def _sink():
    while True:
        args,kwargs = (yield)
        print 'hit sink'

@coroutine
def _simple_one_axis_position_from_position(target,axis): #axis is string name of axis in local frame
    pass

