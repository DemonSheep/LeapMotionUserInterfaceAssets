Example Coroutine data processor implementation that will sit inside an InteractionObject class definition


        @coroutine
        def _ExampleClassCoRoutine(target,parameter1,parameter2,...,sink=None): # start with private name
            
            '''######################'''
            args,kwargs = yield
            self = args[0]
            frame_data = args[1]
            # the target to send data to
            target = kwargs['target']
            # if we have multiple targets
            # we use with for target in targets
            targets = kwargs['targets_list']

            hand_list = kwargs['hands']
            specific_hand = kwargs['hand']
            finger_list = kwargs['fingers']
            specific_finger = kwargs['finger']
            bool_flag_foo = kwargs['flag_foo']


    



