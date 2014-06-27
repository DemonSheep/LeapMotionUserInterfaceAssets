# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 10:42:40 2014

@author: Isaiah Bell
"""
import math

class Some(object):
    
    def __init__(self,center = (0,0,0),normal = (0,0,1),reference_normal = (0,1,0)):

        self.center = center
        self.k_hat = normal

        self.DELTA = 0.000001  #comparsion we use for float math
        
    def check_orthagonal(self,vectorA,vectorB):
        assert len(vectorA) == len (vectorB)
        dot = lambda x,y: sum(x[i]*y[i] for i,v in enumerate(x))
        if abs(dot(vectorA,vectorB)) < self.DELTA:
            return True # the vectors are orthagonal
        else: 
            return False # the vectors are not orthagonal
            
            
    def generate_basis(self,n,d): # where n is normal vector and d is direction
        k = 0
        
        for index,value in enumerate(n):
            k += n[index]*d[index]
        k = float(k)
#        print k
        print d
        r= []
        for index, value in enumerate(d): 
            r.append(d[index] - k * n[index])
        mag = lambda vec: math.sqrt(sum(i**2 for i in vec))
        temp = mag(r)
        for index,value in enumerate(r):
            r[index] = r[index]/temp
        return r
        
        
''' ***************************** TESTS *******************************'''

def orthagonal_test():        
    s = Some()
    x = (1,0,0)
    x_ = (-1,0,0)
    y = (0,-.9999999,0.00000000002) 
    assert (s.check_orthagonal(x,x) == False)
    assert (s.check_orthagonal(x,x_) == False)
    assert (s.check_orthagonal(x,y) == True)
    
    
def basis_test():
    s = Some()
    x = (1,0,0)
    y = (0,1,0)
    z = (0,0,1)
    other = (-.1,12,1)
    print s.generate_basis(y,other)
    
basis_test()



         