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

import Tkinter as tk


''' DEFINE KEYBOARD INTERRUPTS '''
import platform

my_os = platform.system()
if my_os == 'Windows':
    def start_sim():
            return None
    #create  the keyborad interupt case
    import msvcrt
    def key_interrupt():
        if msvcrt.kbhit():
            character = msvcrt.getch()
        else:
            character = False
        return character

elif my_os == 'Linux':

    import tty,sys,termios
    def key_interrupt():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd,termios.TCSADRAIN,old_settings)
        return ch

    try:
        from lib.Test_Callbacks import start_sim
    except ImportError:
        def start_sim():
            return None

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
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.direction = None

        self.canvas = tk.Canvas(width=400, height=400)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.create_oval(190, 190, 210, 210, 
                                tags=("ball",),
                                outline="red", fill="red")

        self.canvas.create_line(0, 200, 400, 200,tags =("line"), fill="red", dash=(4, 4))

        self.canvas.bind("<Any-KeyPress>", self.on_press)
        self.canvas.bind("<Any-KeyRelease>", self.on_release)
        self.canvas.bind("<1>", lambda event: self.canvas.focus_set())

        self.animate()

    def on_press(self, event):
        delta = {
            "Right": (1,0),
            "Left": (-1, 0),
            "Up": (0,-1),
            "Down": (0,1)
        }
        self.direction = delta.get(event.keysym, None)

    def on_release(self, event):
        self.direction = None
        print 'release'

    def animate(self):
        if self.direction is not None:
            self.canvas.move("ball", *self.direction)
        self.after(50, self.animate)

if __name__ == "__main__":
    start_sim() # initalize the sending node
    
    root = tk.Tk()
    frame = tk.Frame(root)
    frame.pack
    bottomframe = tk.Frame(root)
    bottomframe.pack( side = tk.TOP,expand=True, )
    
    greenbutton = tk.Button(bottomframe, text="Brown", fg="brown")
    greenbutton.pack( side = tk.LEFT )
    redbutton = tk.Button(bottomframe, text="Red", fg="red")
    redbutton.pack( side = tk.RIGHT,ipady = 10)
    blackbutton = tk.Button(bottomframe, text="Black", fg="black")
    blackbutton.pack( side = tk.BOTTOM)


    MainWindow(root).pack(fill="both", expand=True,side = tk.BOTTOM)
    root.mainloop()