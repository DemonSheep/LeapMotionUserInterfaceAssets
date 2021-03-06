LeapMotionUserInterfaceAssets
=============================

A simple library for creating virtual control panels for Leap Motion

The Leap Motion Controller is a cool way to control your application, but linking all your projects functionality
to specific gestures can take a while.

This project provides a library of virtual controls such as:
  - [x] Buttons
  - [x] Sliders
  - [x] 2D and 3D position control (like a mouse)
  - [x] 2D and 3D orientation control (like a trackball)
  
You can also write your own custom interaction object from template and easily link it with rest! 

###How This Works

  Instead of looking at the entire field of view for the Leap Controller and determining what gestures to interpret,
  we divide up the space with "Interaction Objects". Basically Interaction Objects are a specific region in space
  that each look for their own gestures. If a hand is inside the volume of an Interaction Object, then gesture 
  recoginition code is executed and the user input parsed. Each Interaction Object modifies an internal state in 
  response to user gestures. This state can be read continously by other parts of your application or polled only when 
  the state changes.
  Each interaction object instance contains information on its size, shape, and orientation in space as well a directed graph composed of coroutines. The coroutines implement data filters, conditionals, and create side effects.
  
  
###Using Your Code:

  Each Interaction Object can be linked to a callback, or another Interaction Object. The callback is where you put your code that you want to run each
  time the Interaction Object is updated by user interaction. The KeyBinding class is the glue where Interaction Objects
  are linked with their callbacks
  
####Example:
    
      class KeyBinding(object):
      
        def __init__(self):
          // Each interaction Object is assigned a name and optionally a callback function
          self.some_button_callback = self._actual_callback_function()
          self.some_button_name = [ CubicButton(**kargs,call_back = self.some_button_callback) ]
          ...
          
          // We have list of every Interaction Element so we can iterate through and poll them
          self.UE_list = [self.some_button_name,...]
          
        //these are coroutines that receive stream data from Interaction Objects
        @coroutine
        def _actual_callback_function(self):
        
          //YOUR CODE HERE
          do_something()
          do_something_else()
          ...
        @coroutine
        def _another_callback(self):
          
          MyApp.do_something()
          MyApp.foo = 'bar'
          ...
          



