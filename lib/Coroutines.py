
import Leap
import time
import sys
sys.path
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
    my_finger_name.lower() #convert user input to expected form
    my_finger_type = finger_names[my_finger_name] # get the type value for the SDK
    while True
        args,kwargs = (yield)
        # if there is a hand in the stream then we will use that hand
        if 'hand' in kwargs.keys():
            # if the finger is not in the hand the below operaition will create an invalid finger object
            finger = kwargs.hand.fingers.finger_type(my_finger_type)
            if finger[0].is_valid:
                kwargs['finger'] = finger #add the finger and overwrite any existing fingers
            else: #the finger we asked for did not exist in this hand
                yield #return control up the pipeline
        else: #we did not have a hand to look for fingers
            yield #return control up the pipeline

@coroutine
def _finger_tip_position(target):
    while True:
        args,kwargs = (yield)
        if 'finger' in kwargs.keys():
            try:
                assert kwargs.['finger'].is_valid == True #make sure finger object is a valid one
                finger = kwargs.['finger']
                del kwargs['finger'] # clean up
            except AssertionError:
                #there was a finger position but there was not a valid finger object
                #restart  the loop
                continue
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
        for hand in frame:
            if not (hand.is_left ^ hand_flag):# do xor to
                kwargs['hand'] = hand
            elif hand.is_right ^ hand_flag: 
                kwargs['hand'] = hand
            else:
                continue
        target.send((args,kwargs))

@coroutine
def _check_bounding_box(target):
    '''Determine if a position given in Leap reference frame is inside 
    Interaction volume

    Parameters:
    =============
        position = (x,y,z) position in Leap frame of reference

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
        #get the position from stream
        position = kwargs['position']
        #clean up the stream
        del kwargs['position']
        local_position = self.convert_to_local_coordinates(position, basis = self.local_basis)
        # check the bounds of the volume with our local_position
        if (self.center[0]-self.width/2) <= local_position[0] <= (self.center[0]+self.width/2):
            if (self.center[1]-self.depth/2) <= local_position[1] <= (self.center[1]+self.depth/2):
                if (self.center[2]-self.height/2) <= local_position[2] <= (self.center[2]+self.height/2): 
                    #the check passes so we send on the data to next step                      
                    target.send((args,kwargs))
                
