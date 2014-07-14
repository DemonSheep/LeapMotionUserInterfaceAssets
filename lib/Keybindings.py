# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 15:39:48 2014

@author: Isaiah Bell
Copyright (c) 2014
Released under MIT License
"""

from InteractionObjects import CubicButton,Slider,PlanarPosition
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

        #define the callback
        self.bar_func = self._bar_func()
        #package the instance and the callback
        self.slider_1 = Slider(CENTER=(-150,300,0),WIDTH = 200, HEIGHT = 200,DEPTH = 400,callback = self.bar_func)
        #define the callback
        self.adjust_gain = self._adjust_gain()
        #package the instance and the callback
        self.slider_2 = Slider(CENTER=(150,300,0),WIDTH = 200, HEIGHT = 200,DEPTH = 400,callback = self.adjust_gain)

        self.planar_slide = self._planar_slide()
        #package the instance and the callback
        self.planar_1 = PlanarPosition(CENTER=(0,300,0),WIDTH = 400, HEIGHT = 200,DEPTH = 400,callback = self.planar_slide)

        '''Make the list of all UI elements '''
        #self.UE_list = [self.button_1,self.slider_1,self.slider_2]       
        self.UE_list = [self.planar_1]
                               
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
             
    @coroutine    
    def _bar_func(self):
        try:
            while True:
                args,kwargs = (yield)
                slide = ['_']*20
                value = self.slider_1.clamped_y
                slide.insert(value,'X')
                print "".join(slide),"gain:", self.slider_1.gain
        except GeneratorExit:
            print 'slider 1 closing'
    
    @coroutine    
    def _adjust_gain(self):
        try:
            while True:
                args,kwargs = (yield)
                slide = ['-']*20
                value = self.slider_2.clamped_y
                slide.insert(value,'X')
                print "".join(slide),'value:', value
        except GeneratorExit:
            print'slider_2 closing'

    @coroutine    
    def _planar_slide(self):
        from copy import deepcopy
        length = 30
        height = 20
        board = []
        for i in range(height):
            if i == 0 or i == height-1:
                board.append(["#"] * length)
            else:
                temp = ["#","#"]
                for i in range(length-2):
                    temp.insert(1," ")
                board.append(temp)
        def print_board(board):
            for row in board:
                print "".join(row)



        def player_position(board,x,y):
            board[y][x] = 'X'
            return board
        try:
            while True:
                args,kwargs = (yield)
                fresh_board = deepcopy(board)
                x = self.planar_1.clamped_x
                y = self.planar_1.clamped_y
                y = height -y
                print 'X:',x,"Y:",y
                fresh_board = player_position(fresh_board,x,y)
                print_board(fresh_board)
        except GeneratorExit:
            print'slider_2 closing'


