from django.conf import settings
import numpy as np
import pandas as pd


class States:
    """ A Collection of all States """
    NORMAL = 'normal'
    ALMOST_FLOODED = 'almost_flooded'
    FLOODED = 'flooded'


def get_state_str(value):
    """ get the state for which value is in """
    if value == 'N':
        return States.NORMAL
    elif value == 'A':
        return States.ALMOST_FLOODED
    else:
        return States.FLOODED

def get_state(value):
    """ get the state for which value is in """
    norm_value = value/settings.DRAIN_HEIGHT
    if norm_value < 0.75:
        return States.NORMAL
    elif 0.75 < norm_value < 0.98:
        return States.ALMOST_FLOODED
    else:
        return States.FLOODED


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
        criteria = [
            data['WaterLevel'].le(0.75), 
            data['WaterLevel'].between(0.75, 0.98), 
            data['WaterLevel'].ge(0.98)]
        state_values = [0, 1, 2]
        data['state'] = np.select(criteria, state_values, 0)
        data["next_state"] =  data["state"].shift()
        self.data = data
        self.states_dict = {"normal": 0, "almost_flooded":1, "flooded": 2}
        self.transitions =  {"normal": {}, "almost_flooded":{}, "flooded": {}}


    def generate(self):
        """ Generate the Transition Matrix """


        # Check for transitions between states and store count
        for i in self.states_dict.items():
            for j in self.states_dict.items():
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
        return list(self.states_dict.keys())
        

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
        self.index_dict = {self.states[index]: index for index in 
                           range(len(self.states))}
        self.state_dict = {index: self.states[index] for index in
                           range(len(self.states))}
 
    def next_state(self, current_state):
        """
        Returns the state of the random variable at the next time 
        instance.
 
        Parameters
        ----------
        current_state: str
            The current state of the system.
        """
        return np.random.choice(
             self.states, 
             p=self.transition_matrix[self.index_dict[current_state], :]
        )
 
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
        for _ in range(no_predictions):
            next_state = self.next_state(current_state)
            future_states.append(next_state)
            current_state = next_state
        return future_states
