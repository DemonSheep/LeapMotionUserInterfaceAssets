import unittest
import Coroutines
from Coroutines import coroutine

#data1
class FakeFrame(object):
    def __init__(self):
        self.id = 9999999

fake_frame = FakeFrame()

class TestNodeJoining(unittest.TestCase):

    @coroutine
    def _sink_node(self):
        while True:
            args,kwargs = (yield)
            print '*'*30
            print 'ARGS:  ',args
            print '#'*25
            print 'KWARGS:  ',kwargs


    def setUp(self):
        end = self._sink_node()
        self.joiner_node_no_merge = Coroutines._simple_joiner_node(end)
        self.joiner_node_with_merge = Coroutines._simple_joiner_node(end,True)

        self.data1 = {'pointable_list':[
                                        {'object':'handthing1','type':'HAND','position':(0,1,3)},
                                        {'object':'fingerthing1','type':'FINGER'}
                                        ],
                    'id_token': 1
                    }
        self.data2 = {'pointable_list':[
                                        {'object':'handthing1','type':'HAND','position':(0,1,3)},
                                        {'object':'fingerthing1','type':'FINGER','position':(6,7,8)}
                                        ],
                    'random_data':'bigint1223434',
                    'id_token': 2
                    }

        

    def test_without_merging(self):
        #print 'running first test'
        target = self.joiner_node_no_merge
        args = ['self',fake_frame]
        kwargsA = self.data1
        kwargsB = self.data2
        target.send((args,kwargsA))
        target.send((args,kwargsB))


    def test_with_merging(self):
        #print 'running second test'
        target = self.joiner_node_with_merge
        args = ['self',fake_frame]
        kwargsA = dict(self.data1)
        kwargsB = dict(self.data2)
        target.send((args,kwargsA))
        target.send((args,kwargsB))


    def test_to_many_parents(self):
        pass




if __name__ == '__main__':
    unittest.main()

#suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
#unittest.TextTestRunner(verbosity=2).run(suite)