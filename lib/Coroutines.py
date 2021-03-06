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
import numpy
#euler angles function needs the math
import math

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

'''############## Optimized for one pointable object only ##################'''
''' Coroutines with the prefix ** _single ** will only accept certain keys in kwargs.
    These are only looking for a single pointable instance and will yield if it is not present.
    This works by only taking the first pointable object off the applicable list.
    Use these types of coroutines when you only want a specific interaction to take place; 
    for example: a button that can only be pressed by the index finger of a right hand. The 
    assumption being that there will only be one operator at a time and therefor one right hand
    at a time. You should be aware of the risks of using ** _single ** coroutines however they are
    faster becasue they have no loops.

'''

@coroutine
def _single_enforce_specific_finger(target,finger_name):#input shuld be a string
    '''Take a hand instance and select one finger in the hand pass down the pipeline
    
    MODIFIES STREAM
    '''

    finger_names = {'thumb':0,'index':1,'middle':2,'ring':3,'pinky':4}
    finger_name = finger_name.lower() #convert user input to expected form
    my_finger_type = finger_names[finger_name] # get the type value for the SDK
    while True:
        args,kwargs = (yield)
        if 'hand' in kwargs.keys():
            hand = kwargs['hand']
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
        else: #we did not have a pointable list to look for fingers
            continue #return control up the pipeline
        target.send((args,kwargs))

@coroutine
def _single_finger_tip_position(target):
    '''
    MODIFIES STREAM
    '''
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
def _single_hand_palm_position(target):
    '''
    MODIFIES STREAM
    '''
    while True:
        args,kwargs = (yield)
        if 'hand' in kwargs.keys() and kwargs['hand']: # check for presence of pointables
            hand = kwargs['hand']
            #getting palm position is whole point of this coroutine
            palm_position = hand.palm_position
            #explicitly built list because it is so short
            kwargs['position'] = palm_position
        else:
            continue #no pointables were in list so stop pipe and yield up line
        target.send((args,kwargs))

@coroutine
def _single_select_a_hand(target,hand_name): #will take 'left' or 'right'
    '''
    MODIFIES STREAM
    '''
    if 'left' == hand_name.lower():
        hand_flag = True
    elif 'right' == hand_name.lower():
        hand_flag = False
    else:
        raise SyntaxError,"hand_name parameter must be either 'left' or 'right' "
    while True:
        args,kwargs = (yield)
        frame = args[1]
        for hand in frame.hands:
            if (hand.is_left and hand_flag):# do xor to
                kwargs['hand'] = hand
            elif hand.is_right ^ hand_flag: 
                kwargs['hand'] = hand
            else:
                continue
        target.send((args,kwargs))

@coroutine
def _single_check_bounding_box_pointable(target):
    '''Determine if a position given in Leap reference frame is inside 
    Interaction volume

    DOES NOT MODIFY STREAM

    Parameters:
    =============
        position = (x,y,z) position in Leap reference frame

    Requires:
    =============
        needs a class instance passed down throught args[0]
        class should have:
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

'''#################### End of single pointable optimized ######################'''

'''################### Begin multiple pointable support #####################'''
''' All functions in this section will operate on pointable_list
    Functions will not close the stream if they do not find what they are looking for
    If a user wants to terminate a stream based on empty condition for a list of pointables 
    an explicit call to _if_empty_then_terminate_stream('list_to_check') must be made.
    This supports more flexible design patterns with multiple posibilities for interaction
    such as mixing streams.
'''


@coroutine
def _hand_palm_position(target):
    '''
    MODIFIES STREAM
    '''
    while True:
        args,kwargs = (yield)
        if 'pointable_list' in kwargs.keys(): # check for presence of pointables
            for pointable in kwargs['pointable_list']: # loop through all the objects
                if pointable['type'] == 'HAND': #get only the hand pointable
                    hand = pointable['object'] #grab out the hand object, only for readability
                    #getting palm position is whole point of this coroutine
                    palm_position = hand.palm_position
                    #explicitly built list because it is so short
                    pointable['position'] = palm_position
                else: #type is wrong so we continue the loop
                    continue
        else:
            continue #no pointables were in list so stop pipe and yield up line
        target.send((args,kwargs))
                    
@coroutine
def _enforce_hand_sphere_radius(target,radius_limit):
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
        target.send((args,kwargs))

@coroutine
def _select_a_hand(target,hand_name): #will take 'left' or 'right'
    '''
    MODIFIES STREAM
    '''
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
                kwargs['pointable_list'].append({'object':hand,'type':'HAND'})
            elif hand.is_right ^ hand_flag: 
                kwargs['pointable_list'].append({'object':hand,'type':'HAND'})
            else:
                continue
        target.send((args,kwargs))

@coroutine
def _check_bounding_box_all_pointable(target):
    '''Determine if a position given in Leap reference frame is inside 
    Interaction volume

    MODIFIES STREAM

    Parameters:
    =============
        pointable_list = list of pointable objects to check against bounding box
            [{'object':pointable_id_1,'type':pointable_TYPE,'position':(x1,y1,z1)},...]

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
            pointable_list = kwargs['pointable_list']
        except KeyError:
            # we go to outer loop because there is nothing to process
            continue
        else:
            #clean up stream
            #del kwargs['pointable_list'] NOT CLEANING UP STREAM FOR NOW
            pass
        for local_pointable in pointable_list:
            # look in the second index of each pointable for the preprocessed position
            try:
                position = local_pointable['position']
            except KeyError:
                continue
            #HOTFIX because Leap.Vector does not support iteration
            temp = [position[0],position[1],position[2]]
            #translate the position to local origin
            local_position = self.convert_to_local_coordinates(temp,self.local_basis)
            # check the bounds of the volume with our local_position
            #center is in Leap coordinates so we are careful with
            if (-self.width/2) <= local_position[0] <= (self.width/2):
                if (-self.depth/2) <= local_position[1] <= (self.depth/2):
                    if (-self.height/2) <= local_position[2] <= (self.height/2): 
                        #the check passes so we append the pointable to the valid list
                        #pointable is a dictionary
                        #overwrite the position to local coordinates so other parts can use that
                        local_pointable['position'] = local_position
                        valid_pointable_list.append(local_pointable)
            #place a new field with the 
        kwargs['pointable_list'] = valid_pointable_list
        target.send((args,kwargs))

@coroutine
def _check_bounding_cylinder_all_pointable(target):
    '''Determine if a position given in Leap reference frame is inside 
    Interaction volume that is a cylinder with symetric axis along the local z

    MODIFIES STREAM

    Parameters:
    =============
        pointable_list = list of pointable objects to check against bounding box
            [{'object':pointable_id_1,'type':pointable_TYPE,'position':(x1,y1,z1)},...]

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
            pointable_list = kwargs['pointable_list']
        except KeyError:
            # we go to outer loop because there is nothing to process
            continue
        else:
            #clean up stream
            #del kwargs['pointable_list'] NOT CLEANING UP STREAM FOR NOW
            pass
        for local_pointable in pointable_list:
            # look in the second index of each pointable for the preprocessed position
            try:
                position = local_pointable['position']
            except KeyError:
                continue
            #HOTFIX because Leap.Vector does not support iteration
            temp = [position[0],position[1],position[2]]
            #translate the position to local origin
            local_position = self.convert_to_local_coordinates(temp,self.local_basis)
            # check the bounds of the volume with our local_position
            if (-self.height/2) <= local_position[2] <= (self.height/2): #do easy check first
                if ((local_position[0]/self.width)**2 + (local_position[1]/self.depth)**2) < self.radius:
                    #the check passes so we append the pointable to the valid list
                    #pointable is a dictionary
                    #overwrite the position to local coordinates so other parts can use that
                    local_pointable['position'] = local_position
                    valid_pointable_list.append(local_pointable)
            #place a new field with the 
        kwargs['pointable_list'] = valid_pointable_list
        target.send((args,kwargs))

@coroutine
def _check_bounding_ellipsoid_all_pointable(target):
    '''Determine if a position given in Leap reference frame is inside 
    Interaction volume that is an axis aligned ellipsoid. 
    Equation of ellipsoid:
        (x/(width/2)^2 + (y/(depth/2))^2 + (z/(height/2))^2 = 1

    To use a sphere simply set each of the axis constants to be equal.
        width = height = depth

    MODIFIES STREAM

    Parameters:
    =============
        pointable_list = list of pointable objects to check against bounding box
            [{'object':pointable_id_1,'type':pointable_TYPE,'position':(x1,y1,z1)},...]

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
            pointable_list = kwargs['pointable_list']
        except KeyError:
            # we go to outer loop because there is nothing to process
            continue
        else:
            #clean up stream
            #del kwargs['pointable_list'] NOT CLEANING UP STREAM FOR NOW
            pass
        for local_pointable in pointable_list:
            # look in the second index of each pointable for the preprocessed position
            try:
                position = local_pointable['position']
            except KeyError:
                continue
            #HOTFIX because Leap.Vector does not support iteration

            temp = [position[0],position[1],position[2]]
            #print temp
            #translate the position to local origin
            local_position = self.convert_to_local_coordinates(temp,self.local_basis)
            # check the bounds of the volume with our local_position
            #for brevity we use letters for the constants
            a = self.width/2
            b = self.depth/2
            c = self.height/2
            #print local_position
            if (local_position[0]/a)**2 + (local_position[1]/b)**2 + (local_position[2]/c)**2 < 1:
                #the check passes so we append the pointable to the valid list
                #pointable is a dictionary
                #overwrite the position to local coordinates so other parts can use that
                local_pointable['position'] = local_position
                valid_pointable_list.append(local_pointable)
            #place a new field with the 
        kwargs['pointable_list'] = valid_pointable_list
        target.send((args,kwargs))

@coroutine
def _prefer_older_pointable(target):
    '''Check the class instace if there is a pointable that is already interacting

    MODIFIES STREAM

    This will filter pointables that are valid in an interaction object and give 
    control priority to the pointable seen last frame. If the pointable id from 
    the previous frame does not match any of the visible pointable, the first pointable
    in the list of pointables will be accepted.

    Requirements:
    ====================
        needs a class instance passed down throught args[0]
        class should have:
            

    Stream Data:
    ==============
        this coroutine will look for pointable_list.
        will create a self.interacting_id if one does not exist already
            self.interacting_id = id of the pointable that was already interacting


    '''
    while True:
        args,kwargs = (yield)
        self = args[0]
        frame = args[1]
        #look for pointable list
        if 'pointable_list' in kwargs.keys() and kwargs['pointable_list']:
            #if there is a previuos detected pointable
            for pointable in kwargs['pointable_list']:
                #check the pointable id
                try:
                    if pointable['object'].id == self.interacting_id:
                        #overwrite the pointable list to only have our chosen poitnable 
                        kwargs['pointable_list'] = [pointable]
                        did_not_find_flag = False
                        #as soon as we find a valid pointable we stop
                        break
                    else:
                        #we move on to the next element
                        did_not_find_flag = True
                        continue
                except AttributeError:
                    #there was not a self.interacting_id
                    did_not_find_flag = True
                    #exit from the loop to the clean up clause
                    break
            if did_not_find_flag:
                #take the first pointable off the stack and make it the new interating_id
                pointable = kwargs['pointable_list'][0]
                self.interacting_id = pointable['object'].id
                #overwrite the pointable list to only include our chosen poitnable
                kwargs['pointable_list'] = [pointable]
        target.send((args,kwargs))

@coroutine
def _add_tools_to_pointable_list(target):
    '''Get all valid tools from frame and add to the pointable_list

    MODIFIES STREAM

    Parameters:
    =============
        frame = Leap.Frame object

    Pointable list formatting:
    ==============================
        {'object':pointable,'type':pointable_TYPE}

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
    '''Get all valid hands from frame and add them to the pointable_list

    MODIFIES STREAM

    Parameters:
    =============
        frame = Leap.Frame object

    Pointable list formatting:
    ==============================
        {'object':pointable,'type':pointable_TYPE}
    '''
    while True:
        args,kwargs = (yield)
        frame = args[1]
        if not 'pointable_list' in kwargs.keys():
            #if the list does not already exist then we add it in
            kwargs['pointable_list'] = []
        if frame.hands.is_empty:
            #the tool list is empty so we skip to end and dont add anything to list
            pass
        else:
            for hand in frame.hands:
                #collect the variables into one list to append
                kwargs['pointable_list'].append({'object':hand,'type':'HAND'})
        target.send((args,kwargs))   

@coroutine
def _pass_arguments(target):
    '''
    DOES NOT MODIFY STREAM
    '''
    while True:
        args,kwargs = (yield)
        #print 'Just passing through'
        #print kwargs
        target.send((args,kwargs))

@coroutine
def _sink():
    '''
    DOES NOT MODIFY STREAM
    '''
    while True:
        args,kwargs = (yield)
        print 'hit sink'

@coroutine
def _simple_one_axis_position_from_position(target,axis,resolution): #axis is string name of axis in local frame
    '''Take pointable position and clamp to local axis of Interaction object

    DOES NOT MODIFY STREAM

    Parameters:
    =============
        axis = 'x' or 'y' or 'z'  the string name of the axis.

    Requirements:
    ==================
        needs a class instance passed down throught args[0]
        class should have:
            self.clamped_(axis_name) = axis name will be the string name of axis 
                                    so if axis is x then self.clamped_x will be made to exist
            [self.gain] will be checked but will not coroutine fail if does not exist



    '''
    # do some preprocessign  to grab the indexes out of the position faster
    #rather than passing in
    if 'x' == axis.lower():
        axis_index = 0
        side_choice = lambda s: getattr(s,'width')
    elif 'y' == axis.lower():
        axis_index = 1
        side_choice = lambda s: getattr(s,'depth')
    elif 'z' == axis.lower():
        axis_index = 2
        side_choice = lambda s: getattr(s,'height')
    else:
        #poor soul did not use string form
        raise SyntaxError,"You must specify the axis in string form: 'x' 'y' or 'z' "
    while True:
        args,kwargs =  (yield)
        self = args[0]
        frame = args[1]
        #check that there is a position in stream with extra check to make sure it is non empty
        if kwargs['pointable_list'] and 'position' in kwargs['pointable_list'][0].keys():
            position = kwargs['pointable_list'][0]['position']
            try:
                gain = getattr(self,'gain')
            except AttributeError:
                #make gain the identity
                gain = self.gain_object.gain
            #get the side we will be working with
            side = side_choice(self)
            #BAD FLOATING POINT MATH not sure how to FIX?
            #calculate the size of the partition but cast to float
            partition = side/float(resolution)
            #calculate the output by the 
            output = int((position[axis_index]*gain+(side/2.0))/partition)
            #clamp the output to the size of the interaction box
            if output > side:
                output = side/partition -1 #this is hacky result of printing visualization
            elif output < 1:
                output = 1 #this is hacky result of printing visualization
            else:
                pass
            #take care of missing attribute and set output
            setattr(self,'clamped_'+axis.lower(),output)
            #print 'clamped_'+axis.lower(),output


        else:
            #there was not a position in stream so we yield control back up
            continue
        #this was an state update but we pass the stream on none the less
        target.send((args,kwargs))

@coroutine
def _enforce_palm_normal(target,allowable_angle):
    '''Find valid hand pointable and make sure the palm normal is within specified angle

    '''
    #convert angle into scalar dot product for easy comparison
    import math
    easy_scalar = math.cos(allowable_angle)
    def magnitude(vec):
        temp = math.sqrt(sum(i**2 for i in vec))
        return temp
    dot = lambda x,y: sum(x[i]*y[i] for i,v in enumerate(x))
    while True:
        args,kwargs = (yield)
        self = args[0]
        #check for the presence of valid pointables
        if 'pointable_list' in kwargs.keys() and kwargs['pointable_list']:
            for pointable in kwargs['pointable_list']:
                if 'type' in pointable.keys() and pointable['type'] == 'HAND':
                    palm_normal = pointable['object'].palm_normal
                    #manually unpack vector since Leap.Vector does not support iteration
                    palm_normal = [palm_normal[0],palm_normal[1],palm_normal[2]]
                    unit_palm_normal = [x/magnitude(palm_normal) for x in palm_normal]
                    #take dot product of the unit vectors
                    if abs(dot(self.normal_direction,unit_palm_normal)) < easy_scalar:
                        #the hand passes 
                        pointable['hand_aligned':True]
                    else:
                        continue

        target.send((args,kwargs))

@coroutine
def _look_for_keyTap_gesture(target,controller):
    #first enable the key tap gesture
    controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP )
    #then set  personal configs
    '''These are the defaults, uncomment to set specific
    controller.config.set("Gesture.KeyTap.MinDownVelocity", 50)
    controller.config.set("Gesture.KeyTap.HistorySeconds", 0.1)
    controller.config.set("Gesture.KeyTap.MinDistance",3.0)
    controller.config.save()
    '''

    #enter the loop
    while True:
        args,kwargs = (yield)

''' Make a unique token generator for nodes then create an instance'''

class TokenGenerator:
    def __init__(self):
        self.token_names = [0]
    #makes instances of it self to 
    def get_token(self):
        token = self.token_names[-1]+1
        self.token_names.append(token)
        return token

#I know globals are bad please FIX
tokenGenerator = TokenGenerator()


@coroutine
def _simple_switch_node(targetA,targetB,condition_A = True,condition_B = True):
    '''Create a node that splits the stream to two child nodes

    This is ment to be a general purpose coroutine node template that can be used
    straight away for simple branching flow control.

    EXTEND ME !! write your own for more intricate and nonlinear signal processing.

    Parameters:
    ==============
        targetA = the first child node
        targetB = the second child node
        condition_A = boolean expression controlling sending stream to targetA. If true
                      we send the stream on
        condition_B = boolean expression controlling sending stream to targetB. If true
                      we send the stream on.

    Operation:
    ============
        The node will evaluate each condition in turn and if true send the stream to that 
        fork. When control returns to the node after child processes run, the second
        brach conditional will be evaluated. Each conditional will be evaluated every time
        the coroutine is called so dynamic expressions are allowed

    '''
    #THIS IS A BAD HACk
    #not sure how to cleanly implement this or if we need two different versions of spliter node
    #will cast all conditions to callable objects 
    import types
    if not isinstance(condition_A, (types.FunctionType, types.BuiltinFunctionType, types.MethodType, types.BuiltinMethodType, types.UnboundMethodType)):
        condition_A = lambda : condition_A
    if not isinstance(condition_B, (types.FunctionType, types.BuiltinFunctionType, types.MethodType, types.BuiltinMethodType, types.UnboundMethodType)):
        condition_B = lambda : condition_B

    #get a unique identifier for this node in terms of the execution of the program
    tokenA = tokenGenerator.get_token()
    tokenB = tokenGenerator.get_token()
    while True:
        args,kwargs = (yield)

        #this needs to be laziliy evaluated HOW?????
        if condition_A():
            #add in the token to the stream
            kwargs['id_token'] = tokenA
            targetA.send((args,kwargs))
        #after control returns execution will return here
        if condition_B():
            kwargs['id_token'] = tokenB
            targetB.send((args,kwargs))
        #that's it for now, go to next loop

@coroutine
def _simple_joiner_node(target,merge = False,self_instance = None): #only has one output
    #if merge is false then we will discard all data except frame data
    #the self parameter will be set to None.
    #if merge is True then the instance will be set to self_instance
    from copy import deepcopy
    def _merge_data_streams_according_to_very_specific_structure(structureA,structureB):
        temp_struct = deepcopy(structureA)
        structureB = deepcopy(structureB)
        #for this specific function we expect a list of dicitonaries
        #we do not go deeper because this a special limited case
        not_in_A_but_in_B_list = []
        for item_in_A in structureA:
            #loop through all the items in structureB

            for index,item_in_B in enumerate(structureB):
                #check if the item is a list
                if item_in_A == item_in_B:
                    #we don't update but we do remove the found object
                    structureB.pop(index)
                #now we check for subsets 
                #we check if it is a dictionary
                try:
                    set_keys_A = set(item_in_A.keys())
                    set_keys_B = set(item_in_B.keys())   
                except AttributeError:
                    #try a list
                    try:
                        if item_in_A in item_in_B:
                            item_in_A = item_in_B
                            #remove the matching item once we find it
                            structureB.pop(index)
                            continue
                    except TypeError:
                        #you get here and this function should no longer be used
                        raise RuntimeError,'you need a different merge function'
                    else:
                        pass

                else:
                    set_difference = set_keys_B.difference(set_keys_A)
                    if set_difference:
                        try:
                            if item_in_A['object'] == item_in_B['object']:
                                for new_keys in set_difference:
                                    item_in_A[new_keys] = item_in_B[new_keys]
                        except KeyError:
                            #was not a pointable list
                            pass
                    elif not set_difference:
                        #try and see if the values are different
                        try:
                            #specific case for the pointable_list
                            if item_in_A['object'] != item_in_B['object']:
                                temp_struct.append(item_in_B)
                                #remove item_in_B once we have added it
                                structureB.pop(index)
                        except KeyError:
                            #this is not a pointable_list
                            pass
        return temp_struct
    #get a unique token for this node
    this_node_token = tokenGenerator.get_token()
    #set up a list to hold the token ids which we can use to detect odd behavior.
    #each join node should only have two static parent nodes. No change over life of program. 
    token_id_dict = {}
    #loop and wait for all nodes to check in.
    while True:
        argsT,kwargsT = (yield)
        #get the token id
        #argsT = deepcopy(argsT)
        #kwargsT = deepcopy(kwargsT)
        tokenT = kwargsT['id_token']
        if tokenT not in token_id_dict:             
            #check the length of the new list
            if len(token_id_dict) >=2:
                #there are more than two parent nodes
                raise RuntimeError,'you have three or more parent nodes pointing to same joiner node'
            else:
                #there are not two parent nodes so add this to token list 
                token_id_dict[tokenT] = [argsT,kwargsT] 
        elif tokenT in token_id_dict:
            token_id_dict[tokenT] = [argsT,kwargsT]          
        if len(token_id_dict) == 1:
            #we updated but there is only one token so
            continue
        else:
            parent_nodes = token_id_dict.keys()
            A = parent_nodes[0]
            B = parent_nodes[1]
            if not token_id_dict[A] or not token_id_dict[B]:
                continue



        #token is from a valid parent
        #ovewrite the previous data from that parent with new data
        token_id_dict[tokenT] = [argsT,kwargsT]
        #now that we have updated all the data
        #we know that there are only two parent nodes in the dict
        parent_nodes = token_id_dict.keys()
        A = parent_nodes[0]
        B = parent_nodes[1]

        args_A = token_id_dict[A][0]
        kwargs_A = token_id_dict[A][1]
        
        args_B = token_id_dict[B][0]
        kwargs_B = token_id_dict[B][1]

        #check if the frame ids are the same
        if args_A[1].id == args_B[1].id:
            #when the instances are not the same then we do not merge
            if merge and ((args_A[0] == args_B[0]) or self_instance):
                if kwargs_A == kwargs_B:
                    target.send((args_A,kwargs_A))
                    token_id_dict[A] = []
                    token_id_dict[B] = []
                    continue
                temp_kwargs = {}
                #we are merging and the frame is the same
                all_key_names = set(kwargs_A.keys() + kwargs_B.keys())
                #strip out the id token, we dont care about it
                all_key_names.remove('id_token')

                for key in all_key_names:
                    if key in kwargs_A:
                        if key in kwargs_B:
                            pass
                            #calculate the merge of the sub data structure'''
                            temp_kwargs[key] = _merge_data_streams_according_to_very_specific_structure(kwargs_A[key],kwargs_B[key])
                        else:
                            temp_kwargs[key] = kwargs_A[key]
                    elif key in kwargs_B:
                        temp_kwargs[key] = kwargs_B[key]
                #add the custom self intance
                if self_instance:
                    args_A[0] = self_instance
                #send the data on
                temp_kwargs
                target.send((args_A,temp_kwargs))
                token_id_dict[A] = []
                token_id_dict[B] = []
            elif args_A[0] != args_B[0] and not merge:
                args_S = (None,argsA[1])
                target.send((args_A, {'id_token':this_node_token}))
                token_id_dict[A] = []
                token_id_dict[B] = []
            else:
                #the instances are the same but we dont merge data
                target.send((args_A,{'id_token':this_node_token}))
                token_id_dict[A] = []
                token_id_dict[B] = []
            #else:
            #    pass
        #wipe the packet data

@coroutine
def _moving_average_box_position_output(target,axis,stdd_threshold = 1,buffer_length = 10):
    '''Smooth position output based on moving average and size of standard deviation

    Parameters:
    ==============
    axis            = string name of the axis to use. Output will be stored in parent 
                      object under "smoothed_"+axis.lower() 
    stdd_threshold  = the threshold at which the moving average is stopped and we directly
                      use the leap data values.

    '''
    
    if 'x' == axis.lower():
        axis_index = 0
        side_choice = lambda s: getattr(s,'width')
    elif 'y' == axis.lower():
        axis_index = 1
        side_choice = lambda s: getattr(s,'depth')
    elif 'z' == axis.lower():
        axis_index = 2
        side_choice = lambda s: getattr(s,'height')
    else:
        #poor soul did not use string form
        raise SyntaxError,"You must specify the axis in string form: 'x' 'y' or 'z' "
    position_buffer = []
    '''Below is the array that controls weights for convolving the position signal.
        Currently implemented as a moving average.
    '''
    weights = numpy.ones(buffer_length)/buffer_length
    #write to a log file for data analysis purposes
    filename = 'smoothed_position_log_'+axis.lower()+'.txt'
    f = open(filename,'w+') 
    while True:
            args,kwargs =  (yield)
            self = args[0]
            frame = args[1]
            #check that there is a position in stream with extra check to make sure it is non empty
            if kwargs['pointable_list'] and 'position' in kwargs['pointable_list'][0].keys():
                position = kwargs['pointable_list'][0]['position']
                temp = [position[0],position[1],position[2]]
                #print temp
                #translate the position to local origin
                local_position = self.convert_to_local_coordinates(temp,self.local_basis)
                try:
                    gain = getattr(self,'gain')
                except AttributeError:
                    #make gain the identity
                    gain = 1
                #add the latest position to end of the list     
                position_buffer.append(local_position[axis_index])
                while len(position_buffer) > buffer_length:
                    #remove elements from first of list
                    position_buffer.pop(0)
                #calculate the standard deviation of the new list
                std_dev = numpy.std(position_buffer)
                if std_dev < stdd_threshold:
                    output = numpy.convolve(position_buffer,weights,mode='valid')
                    if len(output) == 1:
                        output = float(output[0])
                    else:
                        output = numpy.mean(output)
                else:
                    output = local_position[axis_index]
                setattr(self,'smoothed_'+axis.lower(),output)
                #log file
                f.write(str([frame.timestamp,output])+'\n')
                #print 'smoothed_'+axis.lower(),output
            else:
                #there was not a position in stream so we yield control back up
                continue
            #this was an state update but we pass the stream on none the less
            target.send((args,kwargs))

@coroutine
def _simple_euler_angles_to_local_frame_from_palm_orientation(target):
    '''Calaculate the Euler Angles from the orientation of the palm

    '''

@coroutine
def _enforce_n_fingers_extended_per_hand(target, n = 1, strict = False):
    '''Check that some number of fingers are extended
    Thumbs count as fingers so n can be at most 5. This function will sanity check 
    and floor all n values to the integers 0,1,2,3,4,5

    Parameters:
    =============
        n = the number of fingers that must be extended.
        strict = flag to look for at least as many fingers (False) or exactly as many fingers (True)

    Hint: if you are looking to make sure that **k** fingers are closed then just set n=5-k and strict = True
    '''
    n = int(n) #cast to float 
    if 0< n < 5: pass
    elif n < 0: n = 0
    else: n = 5

    while True:
        args,kwargs = (yield)
        self = args[0]
        if kwargs['pointable_list']:
            for element in kwargs['pointable_list']:
                if element['type'] == 'HAND':
                    hand_direction = element['object'].direction
                    hand_direction = [hand_direction[i] for i in range(len(hand_direction))
                    self.convert_to_local_coordinates(hand_direction, basis = self.local_basis)
