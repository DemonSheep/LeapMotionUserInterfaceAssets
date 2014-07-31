import unittest
import Coroutines
from Coroutines import coroutine
from copy import deepcopy

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
            #print '*'*30
            #print 'ARGS:  ',args
            #print '#'*25
            #print 'KWARGS:  ',kwargs


    def setUp(self):
        self.end = self._sink_node()
        self.joiner_node_no_merge = Coroutines._simple_joiner_node(self.end)
        self.joiner_node_with_merge = Coroutines._simple_joiner_node(self.end,True)

        self.data1 = {'pointable_list':[
                                        {'object':'handthing1','type':'HAND','position':(0,1,3)},
                                        {'object':'fingerthing1','type':'FINGER'}
                                        ],
                    'id_token': 1
                    }
        self.data2 = {'pointable_list':[
                                        {'object':'handthing1','type':'HAND','position':(0,1,3)},
                                        {'object':'fingerthing1','type':'FINGER','position':(6,7,8),'foo':3},
                                        {'object':'fingerthing2','type':'FINGER','position':(61,71,81)},
                                        {'object':'fingerthing3','type':'FINGER','position':(50,50,50),'foo':5}
                                        ],
                    'random_data':'bigint1223434',
                    'id_token': 2
                    }
        self.data3 = {'pointable_list':[
                                        {'object':'handthing1','type':'HAND','position':(0,1,3)},
                                        {'object':'fingerthing1','type':'FINGER','position':(9,7,8)}
                                        ],
                    'random_data':'bigint1229999',
                    'id_token': 3
                    }

    def tearDown(self):
        pass

        

    def test_without_merging(self):
        #print 'running first test'
        target = self.joiner_node_no_merge
        args = ['self',fake_frame]
        kwargsA = self.data1
        kwargsB = self.data2
        target.send((args,kwargsA))
        target.send((args,kwargsB))

    def test_with_merging_and_specific_self(self):
        #print 'running third test'
        target = Coroutines._simple_joiner_node(self.end,merge = True, self_instance = 'selfK')
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
        end = self._sink_node()
        target = Coroutines._simple_joiner_node(end,True)
        args = ['self',fake_frame]
        kwargsA = dict(self.data1)
        kwargsB = dict(self.data2)
        kwargsC = dict(self.data3)
        target.send((args,kwargsA))
        target.send((args,kwargsB))
        with self.assertRaises(RuntimeError):
            target.send((args,kwargsC))

    def test_merge_one_sided_data(self):
        target = self.joiner_node_with_merge
        args = ['self',fake_frame]
        kwargsA = self.data1
        kwargsB = {'id_token':9999999}
        target.send((args,kwargsA))
        target.send((args,kwargsB))


class TestNodeDiamond(unittest.TestCase):

    @coroutine
    def _sink_node(self):
        while True:
            args,kwargs = (yield)
            self.assertEquals(kwargs['pointable_list'],self.data1['pointable_list'])
            #print '*'*30
            #print 'ARGS:  ',args
            #print '#'*25
            #print 'KWARGS:  ',kwargs

    def setUp(self):
        sink = self._sink_node()
        join = Coroutines._simple_joiner_node(sink,merge = True)

        targetA = Coroutines._pass_arguments(join)
        targetB = Coroutines._pass_arguments(join)
        self.source = Coroutines._simple_switch_node(targetA,targetB,condition_A = True,condition_B = True)
        self.data1 = {'pointable_list':[
                                {'object':'handthing1','type':'HAND','position':(0,1,3)},
                                {'object':'fingerthing1','type':'FINGER'},
                                {'object':'fingerthing6','type':'FINGER','position':(62,71,81)}
                                ],
                    'id_token': 10
                    }

    def test_diamond_node_pattern(self):
        args = ['selfZ',fake_frame]
        for i in range(10):
            kwargs = deepcopy(self.data1)
            self.source.send((args,kwargs))


class TestNodeNetWork(unittest.TestCase):

    @coroutine
    def _sink_node(self):
        while True:
            args,kwargs = (yield)
            self.assertEquals(kwargs['pointable_list'],self.data1['pointable_list'])
            #print '*'*30
            #print 'ARGS:  ',args
            #print '#'*25
            #print 'KWARGS:  ',kwargs


    def setUp(self):
            sink = self._sink_node()
            join3 = Coroutines._simple_joiner_node(sink,merge = True)
            join2 = Coroutines._simple_joiner_node(join3,merge = True)
            join1 = Coroutines._simple_joiner_node(join3,merge = True)

            targetA = Coroutines._pass_arguments(join1)
            targetB = Coroutines._pass_arguments(join2)
            targetC = Coroutines._pass_arguments(join2)
            targetD = Coroutines._pass_arguments(join1)

            split_2 = Coroutines._simple_switch_node(targetA,targetB,condition_A = True,condition_B = True)

            split_1 = Coroutines._simple_switch_node(targetC,targetD,condition_A = True,condition_B = True)

            self.source = Coroutines._simple_switch_node(split_1,split_2,condition_A = True,condition_B = True)
            self.data1 = {'pointable_list':[
                                    {'object':'handthing1','type':'HAND','position':(0,1,3)},
                                    {'object':'fingerthing1','type':'FINGER'},
                                    {'object':'fingerthing6','type':'FINGER','position':(62,71,81)}
                                    ],
                        'id_token': 10
                        }

    def test_mulitple_level_node_pattern(self):
        args = ['selfZ',fake_frame]
        kwargs = deepcopy(self.data1)
        self.source.send((args,kwargs))

if __name__ == '__main__':
    unittest.main()

#suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
#unittest.TextTestRunner(verbosity=2).run(suite)