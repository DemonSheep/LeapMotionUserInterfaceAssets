# -*- coding: utf-8 -*-
"""
Created on Tue Jul 01 12:30:57 2014

@author: i4e

Thanks to Stack Overflow user HYRY for ploting code
http://stackoverflow.com/questions/11140163/python-matplotlib-plotting-a-3d-cube-a-sphere-and-a-vector
"""

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from itertools import product, combinations
fig = plt.figure()
ax = fig.gca(projection='3d')
ax.set_aspect("equal")

#draw a vector
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d

class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0,0), (0,0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0],ys[0]),(xs[1],ys[1]))
        FancyArrowPatch.draw(self, renderer)

x = Arrow3D([0,0.500000007],[0,-0.499999992549419],[0,-0.707106781186547], mutation_scale=20, lw=1, arrowstyle="-|>", color="k")


ax.add_artist(x)

plt.show()