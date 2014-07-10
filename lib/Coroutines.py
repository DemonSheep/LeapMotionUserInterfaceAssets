
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
def _enforce_one_finger(target,finger_name):#input shuld be a string
    '''Take a hand instance and select one finger in the hand pass down the pipeline
    
    '''

    finger_names = {'thumb':0,'index':1,'middle':2,'ring':3,'pinky':4}
    finger_name = finger_name.lower() #convert user input to expected form
    my_finger_type = finger_names[finger_name] # get the type value for the SDK
    while True:
        args,kwargs = (yield)
        # if there is a hand in the stream then we will use that hand
        if 'hand' in kwargs.keys():
            # if the finger is not in the hand the below operaition will create an invalid finger object
            fingers = kwargs['hand'].fingers
            for test_finger in fingers:
                if test_finger.type() == my_finger_type:
                    finger = test_finger
            
            if finger.is_valid:
                kwargs['finger'] = finger #add the finger and overwrite any existing fingers
            else: #the finger we asked for did not exist in this hand
                continue #return control up the pipeline
        else: #we did not have a hand to look for fingers
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
        for hand in frame.hands:
            if (hand.is_left and hand_flag):# do xor to
                kwargs['hand'] = hand
            elif hand.is_right ^ hand_flag: 
                kwargs['hand'] = hand
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
            [[pointable_id_1,(x1,y1,z1),pointable_TYPE],[pointable_id_2,(x2,y2,z2),pointable_TYPE],....]

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
            position = local_pointable[1]
            local_position = self.convert_to_local_coordinates(position,self.local_basis)
            # check the bounds of the volume with our local_position
            if (self.center[0]-self.width/2) <= local_position[0] <= (self.center[0]+self.width/2):
                if (self.center[1]-self.depth/2) <= local_position[1] <= (self.center[1]+self.depth/2):
                    if (self.center[2]-self.height/2) <= local_position[2] <= (self.center[2]+self.height/2): 
                        #the check passes so we append the pointable to the valid list
                        #pointable is a list
                        #only grab the id = local_pointable[0] and the type name = local_pointable[2]
                        valid_pointable_list.append(local_pointable[0],local_pointable[2])
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
        #manually convert because there are bugs with Leap.Vector
        temp = [position[0],position[1],position[2]]
        local_position = self.convert_to_local_coordinates(temp, basis = self.local_basis)
        # check the bounds of the volume with our local_position
        if (self.center[0]-self.width/2) <= local_position[0] <= (self.center[0]+self.width/2):
            if (self.center[2]-self.depth/2) <= local_position[1] <= (self.center[2]+self.depth/2):
                if (self.center[1]-self.height/2) <= local_position[2] <= (self.center[1]+self.height/2): 
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
def _add_tools_to_pointable_position_list(target):
    '''Get all valid tools from frame and add their tips to the pointable_position_list

    Parameters:
    =============
        frame = Leap.Frame object

    Pointable list formatting:
    ==============================
        [pointable_id,(x,y,z),pointable_TYPE]

    '''
    while True:
        frame = args[1]
        if not 'pointable_position_list' in kwargs.keys():
            #if the list does not already exist then we add it in
            kwargs['pointable_position_list'] = []
        if frame.tools.is_empty:
            #the tool list is empty so we skip to end and dont add anything to list
            pass
        else:
            for tool in frame.tools:
                position = tool.tip_position
                pointable_id = tool.id
                pointable_TYPE = 'TOOL'

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



