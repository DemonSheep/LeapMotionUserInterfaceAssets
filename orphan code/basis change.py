# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 10:42:40 2014

@author: Isaiah Bell
"""
import math

'''THIS WORKS: DONT TOUCH**********************************************'''        
class Quaternion(object):
    
    @classmethod
    def magnitude(cls,vec):
        temp = math.sqrt(sum(i**2 for i in vec))
        return temp
    
    @classmethod
    def inverse(cls,quat):
        # find the conjugate and divde by magnitude
        n = cls.magnitude(quat)
        quat = list(quat) # cats to list so we can modify terms
        quat[0] =  quat[0]/n        
        quat[1] = -quat[1]/n
        quat[2] = -quat[2]/n
        quat[3] = -quat[3]/n
        return quat
        
    @classmethod    
    def multiply(cls,quatA,quatB):
        result =  [quatA[0]*quatB[0]-quatA[1]*quatB[1]-quatA[2]*quatB[2]-quatA[3]*quatB[3],
                   quatA[1]*quatB[0]+quatA[0]*quatB[1]-quatA[3]*quatB[2]+quatA[2]*quatB[3],
                   quatA[2]*quatB[0]+quatA[3]*quatB[1]+quatA[0]*quatB[2]-quatA[1]*quatB[3],
                   quatA[3]*quatB[0]-quatA[2]*quatB[1]+quatA[1]*quatB[2]+quatA[0]*quatB[3]]
        return result
        
    @classmethod
    def rotation(cls,vector,quaternion):
        # first turn vector into a quaternion if it is not already one        
        if len(vector) == 3:
            vector = list(vector) #cast to list so we can insert
            vector.insert(0,0) # insert a 0 for the real part of the quaternion
        else:
            assert len(vector) == 4 # make sure vector is a quaternion
        # compose the sandwitch product
        # calculate the inverse of the quaternion
        inverse = cls.inverse(quaternion)
        # compose the left side of sandwich
        left = cls.multiply(quaternion,vector)
        # multiply the left with the inverse
        result = cls.multiply(left,inverse)
        return result
        
    @classmethod
    def compose_quaternion(cls,angle,axis): #angle in radians
        # make sure we are working with a three vector
        assert len(axis)
        # check vector and ensure it is unit vector
        PRACTICALLY_ZERO = 0.000000001
        if 1.0 - PRACTICALLY_ZERO < cls.magnitude(axis) < 1.0 + PRACTICALLY_ZERO:
            normed_axis = axis
        else:
            mag = cls.magnitude(axis)
            normed_axis = [x/mag for x in axis]
        quat = [0,0,0,0]    
        quat[0] = math.cos(angle/2)
        quat[1] = math.sin(angle/2)*normed_axis[0]
        quat[2] = math.sin(angle/2)*normed_axis[1]
        quat[3] = math.sin(angle/2)*normed_axis[2]
        return quat
        
'''END OF THIS WORKS**********************************************'''        
            
    
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
    
def quaternion_test():
    PRACTICALLY_ZERO = 0.000000001
    myvector = (0,1,0,0)
    myquaternion = Quaternion.compose_quaternion(math.pi/6,(0,0,1))
    revolved = Quaternion.rotation(myvector,myquaternion)
    assert (math.cos(math.pi/6)-PRACTICALLY_ZERO) < revolved[1] < (math.cos(math.pi/6)+PRACTICALLY_ZERO)
    assert (math.sin(math.pi/6)-PRACTICALLY_ZERO) < revolved[2] < (math.sin(math.pi/6)+PRACTICALLY_ZERO)    
    
quaternion_test()




         