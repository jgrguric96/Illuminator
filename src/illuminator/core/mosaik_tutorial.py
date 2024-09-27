
"""
From the mosiak tutorial
"""
from typing import Any


# a new model most be a class

###############################################
class Model:


    def __init__(self, init_val=0): # with any mumbers of arguments (considered as model_parameters)

        self.val = init_val
        self.delta = 1


    def step(self):

        self.val = self.val + self.delta

        return self.val


###############################################



# Create and configure a simulator for the model

import mosaik_api_v3

META = {
'type': 'hybrid',
    'models': {
        'ExampleModel': { # this name does not have to match the class name
            'public': True,
            'params': ['init_val'],
            'attrs': ['delta', 'val'],
            'trigger': ['delta'],
        },
    },
}

######################################################


# create a simulator with configuration META, and the Model class
# it must be a subclass of mosaik_api_v3.Simulator

class Simulator(mosaik_api_v3.Simulator):
    def __init__(self):
        super().__init__(META)
        self.eid_prefix = 'Model_'
        self.entities = {}  # Maps EIDs to model instances
        self.time = 0

    def init(self) -> dict: # this is used for initialization tasks, if any. It must return 'self.meta'

        return self.meta

    def create(self, num: int, model: str, init_val: Any) -> list: # use to create a number of instances of the same MODEL. If the model has model parameters, their initial values might be passed here,
        # model parameters must appead in META
        next_eid = len(self.entities)
        entities = [] # NOTE: this is not the same as self.entities

        for i in range(next_eid, next_eid + num):
            model_instance = Model(init_val)
            eid = '%s%d' % (self.eid_prefix, i)
            self.entities[eid] = model_instance
            entities.append({'eid': eid, 'type': model}) # QUESTION: what is model here?

        return entities # must return a list of entities
    
    def step(self, time, inputs, max_advance): # max_advance is for special cases. 

        # inputs: a dictionary with input values from other simulators (if there are any)

        # time (current simulation time)
        #tells your simulator to perform a simulation step. 
        # It receives its current simulation time, a dictionary with input values from other simulators (if there are any), 
        # and the time until the simulator can safely advance its internal time without creating a causality error

        # inputs: a dictionary with input values from other simulators (if there are any)
            # {'Model_0': {
            #     'delta': {'src_id_0': 23},
            # },
            # 'Model_1': {
            #     'delta': {'src_id_1': 42},
            #     'val': {'src_id_1': 20},
            # }
            # }

        self.time = time
        # Check for new delta and do step for each model instance:
        for eid, model_instance in self.entities.items():
            if eid in inputs: # inputs are values from other simulators, must be a dictionary
                attrs = inputs[eid]
                for attr, values in attrs.items():
                    new_delta = sum(values.values())
                model_instance.delta = new_delta # NOTE: this modifies the value in the model instance

            model_instance.step()

        return time + 1  # Step size is 1 second. This update the currrent simulation time
    

