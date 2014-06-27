# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 15:39:48 2014

@author: Isaiah Bell
Copyright (c) 2014
"""

from InteractionObjects import CubicButton,Slider

class KeyBinding(object):
    '''
    Store a list of every interaction object and binds output to some other function call
    
    To add an interaction instance:
        name = [InteractionObject(), callback_for_interaction_instance()] 
    '''
    def __init__(self,robot = None):
        self.robot = robot
        
        self.nuke_the_universe = [CubicButton(CENTER=(100,200,250)),self.nuke_universe]
        self.bar = [Slider(CENTER=(-150,300,0),WIDTH = 200, HEIGHT = 200,DEPTH = 400),self.bar_func]
        self.gain_slider = [Slider(CENTER=(150,300,0),WIDTH = 200, HEIGHT = 200,DEPTH = 400), self.adjust_gain]
        
        self.UE_list = [self.nuke_the_universe,self.bar,self.gain_slider]       
    
                               
    '''BUTTON CALLBACKS ************************************************'''                           
    
    def nuke_universe(self):
        print 'nukeing universe'
        
    def bar_func(self):
        slide = ['_']*20
        value = self.bar[0].slider_value
        slide.insert(value,'X')
        print "".join(slide),"gain:" ,self.bar[0].gain
        
    def adjust_gain(self):
        slide = ['-']*20
        value = self.gain_slider[0].slider_value
        slide.insert(value,'X')
        self.bar[0].gain = value/10.0
        print "".join(slide),
