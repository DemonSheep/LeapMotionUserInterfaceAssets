import VectorMath
import unittest
import numpy
import math

class TestVectorOperations(unittest.TestCase):

    def setUp(self):
        self.x = (1,0,0)
        self.y = (0,1,0)
        self.z = (0,0,1)
        self.other = (1,1,1)
        self.really_close = (0,0,.99999999999)
        pass

    def test_orthagonal(self):
        
        x_prime = (-1,0,0)
        y_close = (0,-.9999999,0.00000000002)
        self.assertFalse (VectorMath.check_orthagonal(self.x,self.x) )
        self.assertFalse (VectorMath.check_orthagonal(self.x,x_prime) )
        self.assertTrue (VectorMath.check_orthagonal(self.x,y_close) )
    

       
    def test_basis_generation(self):
        expected_basis = [[0.0,0.0,-1.0],[0.0,1.0,0.0],[1.0,0.0,0.0]]
        gen_basis = VectorMath.generate_basis(self.x)
        for index,vector in enumerate(expected_basis):
            numpy.testing.assert_allclose(gen_basis[index],vector, atol = 1e-07)

        gen_basis2 = VectorMath.generate_basis((1,1,0))
        expected_basis2 = [[0.5,-0.5,-0.707106781],[-.5,0.5,-0.707106781],[0.707106781,0.707106781,0.0]]
        for index,vector in enumerate(expected_basis2):
            numpy.testing.assert_allclose(gen_basis2[index],vector, atol = 1e-07)

        
    def test_quaternion(self):
        PRACTICALLY_ZERO = 0.000000001
        myvector = (0,1,0,0)
        myquaternion = VectorMath.Quaternion.compose_quaternion(math.pi/6,(0,0,1))
        revolved = VectorMath.Quaternion.rotation(myvector,myquaternion)
        assert (math.cos(math.pi/6)-PRACTICALLY_ZERO) < revolved[0] < (math.cos(math.pi/6)+PRACTICALLY_ZERO)
        assert (math.sin(math.pi/6)-PRACTICALLY_ZERO) < revolved[1] < (math.sin(math.pi/6)+PRACTICALLY_ZERO)
        assert (0.0 -PRACTICALLY_ZERO < revolved[2] < 0.0 + PRACTICALLY_ZERO)
        #print revolved #[0.8660254037844387,0.49999999999999994,0.0]
        
    def test_cross_product(self):

        other = (1,1,1)
        cross, angle = VectorMath.cross_product(self.z,other)
        numpy.testing.assert_allclose([-math.sqrt(3)/3,math.sqrt(3)/3,0.0], cross, atol = 1e-07)
        numpy.testing.assert_allclose ([math.asin(math.sqrt(2.0/3))],[angle], atol = 1e-07)
        bad_vec = (0,0,0,1)
        #print 'This should say vector A is bad:'
        cross,angle = VectorMath.cross_product(bad_vec,self.z)
        #this bad vector argument should fail and return none for both values
        self.assertIsNone(cross)
        self.assertIsNone(angle)
        #print 'This should say vector B is bad:'
        cross,angle = VectorMath.cross_product(self.z,bad_vec)
        #this bad vector argument should fail and return none for both values        
        self.assertIsNone(cross)
        self.assertIsNone(angle)

        simple_x = (1,0)
        simple_y = (0,1)
        cross,angle = VectorMath.cross_product(simple_x,self.y)
        numpy.testing.assert_allclose(self.z,cross)
        numpy.testing.assert_allclose([math.pi/2],angle, atol = 1e-07)

        cross,angle = VectorMath.cross_product(self.z,simple_y)
        numpy.testing.assert_allclose([-1,0,0],cross)
        numpy.testing.assert_allclose([math.pi/2],angle, atol = 1e-07)


    def test_decompose_vector(self):
        mybasis = [self.x,self.y,self.z]
        myvector = (1,2,3)
        assert VectorMath.decompose_vector(myvector,mybasis) == [1,2,3]
        another_basis = [[1,2,3],[0,0,0],[0,0,0]]
        result = VectorMath.decompose_vector(myvector,another_basis)
        self.assertEquals(result,[14,0,0])

    def test_vector_rotation(self):
        really_close = (0,0,.99999999999)
        angle = math.pi/4
        # we will try to rotate a vector about itself
        this_quaternion = VectorMath.Quaternion.compose_quaternion(angle,self.z)
        result = VectorMath.Quaternion.rotation(really_close,this_quaternion)
        numpy.testing.assert_allclose(really_close,result)


if __name__ == '__main__':
    unittest.main()