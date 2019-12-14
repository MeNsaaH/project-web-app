from django.conf import settings
import numpy as np
import pandas as pd
from numpy.linalg import matrix_power
from functools import partial


class States:
    """ A Collection of all States and Related functions"""
    NORMAL = 'normal'
    ALMOST_FLOODED = 'almost_flooded'
    FLOODED = 'flooded'
    
    INDICES = {NORMAL: 0, ALMOST_FLOODED: 1, FLOODED: 2}
    NAMES = dict((v,k) for k,v in INDICES.items())
    SHORT_NAMES = {'N': NORMAL, 'A': ALMOST_FLOODED, 'F': 'FLOODED'}
    TRANSITIONS = {NORMAL: {}, ALMOST_FLOODED: {}, FLOODED: {}}
    
    normal_criteria = lambda data: data.le(0.75)
    almost_flooded_criteria = lambda data: data.between(0.75, 0.98)
    flooded_criteria = lambda data: data.gt(0.75)
    # Some serious abuse of class methods around here ¯\_(ツ)_/¯ 
    
    @classmethod
    def get_criteria(cls, data):
        return [
            States.normal_criteria(data),
            States.almost_flooded_criteria(data),
            States.flooded_criteria(data)
        ]
    
    @classmethod
    def get_states(cls, data, type="index"):
        """ return the states for data """
        x = cls.INDICES.values() if type == "index" else cls.INDICES.keys()
        return np.select(cls.get_criteria(data), list(x), 0)
    
    @classmethod
    def get_state_str(cls, value):
        """ get the state for which value is in """
        return cls.SHORT_NAMES[value]
    
    @classmethod
    def get_state(cls, value):
        """ get the state for which value is in """
        index = cls.get_states(pd.DataFrame([value])[0])
        return cls.NAMES[index[0]]


def min_max_scaler(X, max_height):
    """ Return min-max scaler for the dataframe """
    min_ = 0
    max_ = 1
    X_std = (X - X.min(axis=0)) / (max_height - X.min(axis=0))
    return X_std * (max_ - min_) + min_


class TransitionMatrix:
    """ Generates the Transition Matrix for the given Dataset """
    
    def __init__(self, data, max_height=settings.DRAIN_HEIGHT):
        """ Initialize the necessary Variables """
        
        # Normalize Water Level data using MinMax Algorithm
        data["WaterLevel"] = min_max_scaler(data["WaterLevel"].values, max_height)
        data['state'] = States.get_states(data["WaterLevel"])
        data["next_state"] = data["state"].shift()
        self.data = data
        self.transitions = States.TRANSITIONS

    def generate(self):
        """ Generate the Transition Matrix """

        # Check for transitions between states and store count
        for i in States.INDICES.items():
            for j in States.INDICES.items():
                self.transitions[i[0]][j[0]] = self.data[
                        (self.data["state"] == i[1]) & (self.data["next_state"] == j[1])].shape[0]

        # Calculate the Probability of Transition based on data from transtions
        df = pd.DataFrame(self.transitions)
        for i in range(df.shape[0]):
            df.iloc[i] = df.iloc[i]/(df.iloc[i].sum() or 1)
        return df.values

    @property
    def values(self):
        """ Return the Transtion Matrix """
        return self.generate()
    
    @property
    def states(self):
        return list(States.INDICES.keys())
        
    def representation(self):
        return pd.DataFrame(self.transitions)

    
class MarkovChainPredictor:
    """ The Markov Chain Model Predictor """

    def __init__(self, transition_matrix, states):
        """
        Initialize the MarkovChain instance.
 
        Parameters
        ----------
        transition_matrix: 2-D array
            A 2-D array representing the probabilities of change of 
            state in the Markov Chain.
 
        states: 1-D array 
            An array representing the states of the Markov Chain. It
            needs to be in the same order as transition_matrix.
        """
        self.transition_matrix = np.atleast_2d(transition_matrix)
        self.states = states
 
    def get_current_state_vector(self, current_state):
        v_state = np.zeros([len(States.INDICES.keys())])
        v_state[States.INDICES[current_state]] = 1
        return v_state

    def next_state(self, current_state, time_step=1):
        """
        Returns the state of the random variable at the next time 
        instance.
 
        Parameters
        ----------
        current_state: str
            The current state of the system.
        """
        current_state_vector = self.get_current_state_vector(current_state)
        a = current_state_vector.dot(matrix_power(self.transition_matrix, time_step))
        return States.NAMES[np.argmax(a)]
 
    def generate_states(self, current_state, no_predictions=10):
        """
        Generates the next states of the system.
 
        Parameters
        ----------
        current_state: str
            The state of the current random variable.
 
        no: int
            The number of future states to generate.
        """
        future_states = []
        for i in range(no_predictions):
            next_state = self.next_state(current_state, time_step=i+1)
            future_states.append(next_state)
        return future_states
