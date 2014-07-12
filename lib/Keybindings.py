# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 15:39:48 2014

@author: Isaiah Bell
Copyright (c) 2014
Released under MIT License
"""

from InteractionObjects import CubicButton,Slider
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
        #define the callback
        self.nuke_universe = self._nuke_universe()
        #package the instance and the callback
        self.button_1 = CubicButton(CENTER=(0,200,0),callback = self.nuke_universe)


        '''
        #define the callback
        self.bar_func = self._bar_func()
        #package the instance and the callback
        self.slider_1 = [Slider(CENTER=(-150,300,0),WIDTH = 200, HEIGHT = 200,DEPTH = 400),self._bar_func]
        #define the callback
        self.adjust_gain = self._adjust_gain()
        #package the instance and the callback
        self.slider_2 = [Slider(CENTER=(150,300,0),WIDTH = 200, HEIGHT = 200,DEPTH = 400), self._adjust_gain]
        '''


        '''Make the list of all UI elements '''
        self.UE_list = [self.button_1]       
    
                               
    '''BUTTON CALLBACKS ************************************************'''     
                          
    @coroutine
    def _nuke_universe(self):
        try:
            while True:
                args,kwargs = (yield)
                print '*'*25
                #print 'Args:',args
                #print 'Kwargs:',kwargs
                print 'nukeing universe'
                print '*'*25
        except GeneratorExit:
            print 'button_nuke_universe closing!'

'''                
    @coroutine    
    def _bar_func(self):
        while True:
            slide = ['_']*20
            value = self.bar[0].slider_value
            slide.insert(value,'X')
            print "".join(slide),"gain:" ,self.bar[0].gain
    
    @coroutine    
    def _adjust_gain(self):
        while True:
            slide = ['-']*20
            value = self.gain_slider[0].slider_value
            slide.insert(value,'X')
            self.bar[0].gain = value/10.0
            print "".join(slide),'value:', value

'''
