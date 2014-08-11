# -*- coding: utf-8 -*-
"""
Created on Tue Jun 24 15:47:17 2014

@author: Isaiah Bell
Copyright 2014
Released under MIT License
"""

#Next bunch of lines are a hack
# Fix when I understand relative paths and modules
import sys
import os

sys.path.insert(0,os.path.dirname(__file__))

from lib.Keybindings import *
from lib.InteractionObjects import *
from lib.Robot import *
from lib.Coroutines import frame_broadcaster
import lib.Coroutines as Co

import Tkinter as tk


''' DEFINE KEYBOARD INTERRUPTS '''
import platform

my_os = platform.system()
if my_os == 'Windows':
    def start_sim():
            return None
    #create  the keyborad interupt case


''' TESTS ####################################################################'''

def buffer_test():
    buff = Buffer()
    buff.enqueue('foo')
    buff.enqueue((1,2,3))
    buff.enqueue(Buffer())
    buff.enqueue(4)
    print buff.queue
    print buff.dequeue()
    print "Try illegal access to index -1000:",buff.dequeue(-1000)
    print buff.queue
    for i in range(buff.buffer_size+10):
        buff.enqueue(i)
        print buff.queue


def button_test():
    button = CubicButton(HEIGHT = 200)
    print button.center
    print button.width
    print button.height
    print button.depth
    print button.press_direction
    
def handler_test():
    button = CubicButton()
    interaction_list = [button,button]
    print button
    print interaction_list
    print button.is_valid(1)
    
def key_bind_test():
    keybind = KeyBinding()
    print keybind.nuke_the_universe[0].center
    
def slider_run_test():
    
    print 'finished node'
    keybind = KeyBinding()
    targets = []
    for thing in keybind.UE_list:
        targets.append(thing.data_listener)
    for i in range(400):
        x = key_interrupt()
        if x:
            print 'key is:',x.decode()
        frame_broadcaster(targets) 
        time.sleep(.05)
        print i

    
def button_run_test():
    keybind = KeyBinding()
    # only take the first  element since that is our button
    button = keybind.UE_list[0]
    target = button.data_listener
    for i in range(400):
        frame_broadcaster([target]) 
        time.sleep(.05)
        print i

    
''' RUN TESTS HERE ############################################################'''

import Tkinter as tk

class MainWindow(tk.Frame):
    def __init__(self, parent,targets,keybind_object):
        tk.Frame.__init__(self, parent)

        self.direction = None
        self.count = 0
        self.keybind = keybind_object
        #leap_service on flag
        self.leap_frame_broadcasting_on = False
        #ball position coordinates
        #x and y are set to be the starting positon of the ball
        self.prev_x = 200
        self.prev_y = 200
        self.prev_z = None

        start_button = tk.Button(self, text="Start", fg="green")
        start_button.pack( side = tk.LEFT )
        start_button.bind("<Button-1>",self.start_button)

        pause_button = tk.Button(self, text="Pause", fg="red")
        pause_button.pack( side = tk.LEFT )
        pause_button.bind("<Button-1>",self.pause_button)

        self.window_width = 400
        self.window_height = 400
        self.canvas = tk.Canvas(width=self.window_width, height=self.window_height)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_oval(190, 190, 210, 210, 
                                tags=("ball",),
                                outline="red", fill="red")

        self.canvas.create_line(0, 200, 400, 200,tags =("line"), fill="red", dash=(4, 4))
        self.canvas.create_line(200, 0, 200, 400,tags =("line"), fill="red", dash=(4, 4))

        for i in range():
            self.canvas.create_line(-50,i*50,450,i*50,tags=("back_grid"), fill = "blue", dash = (4,4))
            self.canvas.create_line(i*50,-50,i*50,450,tags=("back_grid"), fill = "blue", dash = (4,4))

        self.canvas.bind("<Any-KeyPress>", self.on_press)
        self.canvas.bind("<Any-KeyRelease>", self.on_release)
        self.canvas.bind("<1>", lambda event: self.canvas.focus_set())

        self.animate(targets)

    def pause_button(self,event):
        self.leap_frame_broadcasting_on = False
        InteractionSpace.hand_command_valid = False
        print 'Paused'

    def start_button(self,event):
        self.leap_frame_broadcasting_on = True
        print 'Starting......'

    def on_press(self, event):
        delta = {
            "Right": (1,0),
            "Left": (-1, 0),
            "Up": (0,-1),
            "Down": (0,1)
        }
        self.direction = delta.get(event.keysym, None)
        #keybinding for pause
        if event.keysym == 'p':
            self.pause_button(event)
        #keybinding for start
        elif event.keysym == 's':
            self.start_button(event)

    def on_release(self, event):
        self.direction = None

    def animate(self,targets):
        if self.leap_frame_broadcasting_on:
            frame_broadcaster(targets)

        x = self.keybind.containing_sphere.smoothed_x
        y = self.keybind.containing_sphere.smoothed_y
        z = self.keybind.containing_sphere.smoothed_z
        valid_flag = InteractionSpace.hand_command_valid
        #update the ball position
        if x is not None and y is not None:
            x = int(x*self.keybind.containing_sphere.gain_object.gain + self.window_width/2)
            if x < 0:
                x = 0
            elif x > self.window_width:
                x = self.window_width
            y = int(y*self.keybind.containing_sphere.gain_object.gain + self.window_height/2)
            if y < 0:
                y = 0
            elif y > self.window_height:
                y = self.window_height

            delta_x = x - self.prev_x
            self.prev_x = x
            delta_y = y - self.prev_y
            self.prev_y = y
            self.canvas.move("ball",delta_x,-delta_y)


        if self.direction is not None:
            self.canvas.move("ball", *self.direction)

               

        self.after(50, self.animate,targets)

if __name__ == "__main__":
    start_sim() # initalize the sending node
    keybind = KeyBinding()
    root = tk.Tk()
    frame = tk.Frame(root)
    frame.pack
    bottomframe = tk.Frame(root)
    bottomframe.pack( side = tk.BOTTOM,expand=True)

    increment_gain_button = tk.Button(bottomframe, text="increment gain", fg="black")
    increment_gain_button.pack( side = tk.LEFT )
    increment_gain_button.bind("<Button-1>",lambda event: keybind.containing_sphere.gain_object.increase_gain())
    decrement_gain_button = tk.Button(bottomframe, text="decrement gain", fg="black")
    decrement_gain_button.pack( side = tk.LEFT )
    decrement_gain_button.bind("<Button-1>",lambda event: keybind.containing_sphere.gain_object.decrease_gain())
    
    targets = []
    for thing in keybind.UE_list:
        targets.append(thing.data_listener)

    MainWindow(root,targets,keybind).pack(fill="both", expand=True,side = tk.TOP)
    root.mainloop()