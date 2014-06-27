LeapMotionUserInterfaceAssets
=============================

A simple library for creating virtual control panels for Leap Motion

The Leap Motion Controller is a cool way to control your application, but linking all your projects functionality
to specific gestures can take a while.

This project provides a library of virtual controls such as:
  - Buttons
  - Sliders
  - 2D and 3D position control (like a mouse) [WIP]
  - 2D and 3D orientation control (like a trackball) [WIP]
  
You can also write your own custom interaction object from template and easily link it with rest! 

###How This Works

  Instead of looking at the entire field of view for the Leap Controller and determining what gestures to interpret,
  we divide up the space with "Interaction Objects". Basically Interaction Objects are a specific region in space
  that each look for their own gestures. If a hand is inside the volume of an Interaction Object, then gesture 
  recoginition code is executed and the user input parsed. Each Interaction Object modifies an internal state in 
  response to user gestures. This state can be read continously by other parts of your application or polled only when 
  the state changes.
  
  
###Using Your Code:

  Each Interaction Object can be linked to a callback. The callback is where you put your code that you want to run each
  time the Interaction Object is updated by user interaction. The KeyBinding class is the glue where Interaction Objects
  are linked with their callbacks
  
####Example:
    
      class KeyBinding(object):
      
        def __init__(self):
          // Each interaction Object is assined a name and optionally a callback function
          self.some_button_name = [ CubicButton(**kargs), self.some_button_callback]
          ...
          
          // We have list of every Interaction Element so we can iterate thorugh and poll them
          self.UE_list = [self.some_button_name,...]
          
          
        def some_button_callback(self):
          
          do_something()
          do_something_else()
          ...
        
        def another_callback(self):
          
          MyApp.do_something()
          MyApp.foo = 'bar'
          ...
          



