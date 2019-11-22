import numpy as np
import itertools

#Resource class L
class Resources:
    def __init__(self,num_res, max_L, avg_ut, cap_L, cap_cost):
        ##How many resources are there
        self.amount = num_res
        ## How many units per resource available
        self.max = max_L
        ## What's the average usage per treatment pattern per period
        self.avgMatrix = avg_ut
        ## What's the desired amount of usage
        self.cap = cap_L
        ## What's the cost for going over this cap?
        self.cost = cap_cost

class Patterns:
    def __init__(self, num_patterns):
        ##How many treatment patterns are there
        self.amount = num_patterns
        self.statespace = []



class Specialties:
    def __init__(self, num_sp, max_spec):
        ## number of specialties
        self.amount = num_sp
        ## Maximum admissions per period
        self.max = max_spec
        self.actions = []
        self.__Actions(num_sp, max_spec)

    def Actions(self, amount, max):
        B=[]
        for i in range(len(max)):
            B.append([*range(max[i]+1)])
        A = itertools.product(*B)
        for action in A:
            self.actions.append(list(action))
    __Actions = Actions

##Number of specialties d
d= 2
## maximum admission per period max_S = [max in specialty 1, max in specialty 2]
max_S= np.array([2,2])

## NUMBER OF RESOURCES
num_res = 2
## max(L_j)
max_L = np.array([5,5])

## Number of treatment patterns
n=3
## avg resource utilization per period
## avg_ut = [[avg util. of res. 1 by E_1,avg ut of res. 1 by E_2], [avg ut of res. 2 by E_1,avg ut of res. 2 by E_2]]
avg_ut = np.array([[2.2,2.6],[2.6,2.2]])
## Utilization cap
cap_L = np.array([4,4])

##Cost for resource deviation
cap_cost = np.array([[1.0,1.6],[1.5,1.0],[1.0,1.0]])

## Probability configuration
## probabilities = [transitioning in specialty 1, transitioning in specialty 2]
trans_probs = np.array([[[0.4,0.1,0.5],[0.1,0.3,0.6],[0.0,0.0,1.0]],[[0.2,0.1,0.7],[0.1,0.2,0.7],[0.0,0.0,1.0]]])

##Entering probs = [entering in specialty 1, entering in specialty 2]
enter_probs = np.array([[0.5,0.5,0.0],[0.4,0.6,0.0]])

## We can put this in our resource, specialty and treatment pattern class
L = Resources(num_res, max_L, avg_ut, cap_L, cap_cost)
E = Patterns(n)
S = Specialties(d, max_S)

def calc_prob(state2, state1, action):
    for i in range(max(0,state2[0][0]-(sum(state1[0][0:2]))),min(state2[0][0],action[0])):
