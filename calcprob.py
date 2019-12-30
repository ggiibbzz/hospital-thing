import numpy as np
import itertools
import math
from ast import literal_eval
import time

#I'm keeping the next two as global variables since it is a pain to put them through multiple functions.
#######
## Probability configuration
## probabilities = [transitioning in specialty 1, transitioning in specialty 2]
trans_probs = np.array([[[0.4, 0.1, 0.5], [0.1, 0.3, 0.6], [0.0, 0.0, 1.0]], [[0.2, 0.1, 0.7], [0.1, 0.2, 0.7], [0.0, 0.0, 1.0]]])
##Entering probs = [entering in specialty 1, entering in specialty 2]
enter_probs = np.array([[0.5, 0.5, 0.0], [0.4, 0.6, 0.0]])
#######


def partition(n, d, depth=0):
    if d == depth:
        return [[]]
    return [
        item + [i]
        for i in range(n+1)
        for item in partition(n-i, d, depth=depth+1)
        ]

##Calculates the entering probability given the particular action distributed over the treatment patterns and the specialty
##E.g. if action = 3, then admstate could be [2,1,0] for specialty one.
def EnterProb(admstate, specialty):
    P = math.factorial(sum(admstate))
    for i in range(len(admstate)-1):
        if i == len(admstate)-1:
            P = P*(enter_probs[specialty][i])**(sum(admstate)-sum(admstate[:len(admstate)-2]))/math.factorial(sum(admstate)-sum(admstate[:len(admstate)-2]))
        else:
            P = P*(enter_probs[specialty][i])**(admstate[i])/(math.factorial(admstate[i]))
    return P

##Calculates the transition probability given the PARTICULAR(!) transition tuple over the treatment patterns and the specialty
##E.g. Say we want to go to state_(t+1): [0,2,2] from state_t [3,1,1] with action 0, then we have a two-tuple ([0,2,1],[0,0,1])
##Where the first component of the tuple represents x_11 = 0, x_12 = 2, x_13=1 and the second tuple: x_21=0, x_22=0 and x_23=1
def TransProbs(comptuples, specialty):
    ## i will signify in which treatment pattern we're at on time period t
    P=1
    for i in range(len(comptuples)):
        P = P*math.factorial(sum(comptuples[i]))
        for j in range(len(comptuples[i])):
            P = P * (trans_probs[specialty][i][j]) ** (comptuples[i][j]) / (math.factorial(comptuples[i][j]))
    return P

##Given state_(t+1), state_t, action and specialty this will calculate the probability of going from one state to another
##It will obviously use the functions given above (EnterProb() and TransProbs())

##ATTENTION: DO NOT INPUT ENTIRE STATE WITH DIFFERENT SPECIALTIES, JUST THE ONES FROM ONE SPECIALTY
def CalcProb(state2, state1, actionnr, specialty):
    print()
    if sum(state2) != sum(state1[:len(state1)-1])+actionnr:
        return 0
    else:
        B=[]
        C=[]

        ##Targetlist is a list for all targets I want to reach by applying only transitions.
        ##One target is state2-action
        targetlist=[]
        for i in range(len(state2)-1):
            B.append([*range(state2[i]+1)])
        A = itertools.product(*B)
        for action in A:
            action = list(action)+[0]
            if sum(action)== actionnr:
                C.append(action)
        for action in C:
            target = np.array(state2)-np.array(action)
            targetlist.append([target.tolist(),EnterProb(action, specialty)])
        transition_prob_sums = []
        ##Now we want to work for each target alone
        for targ in targetlist:
            ##Create a list for transitions
            trans = []
            ##Create a list for the sums of transitions
            transsums = []
            probsums = []
            ##Let us iterate over the elements in target, except for the last element since that is the discharge
            for j in range(len(targ[0])-1):
                ##list of transitions created by going over the partition created by varying component j
                lst3=[]
                ## To partition sumlist in a component for every j, we must create a new list. sumlist = [[...], [...], ..., [...]]
                for i in range(targ[0][j]+1):
                    ##Since i stands for how many patients we keep in a treatment pattern we need to calculate how many we have to distribute
                    # extend with n-sum(entries)
                    n = state1[j]-i
                    d = len(state1)-1
                    lst = [[n - sum(p)] + p for p in partition(n, d - 1)]
                    lst2=[]
                    for lijst in lst:
                        lijst = lijst[0:j] + [i] + lijst[j:]
                        lst2.append(lijst)
                    lst3 = lst3 + [element for element in lst2]
                trans.append(lst3)
            ##All cartesian product
            transprods = itertools.product(*trans)
            for prod in transprods:
                som = sum([np.array(list(prod)[u]) for u in range(len(state2)-1)])
                if som.tolist() == targ[0]:
                    transsums.append([prod, TransProbs(prod, specialty)])
                else:
                    pass
            kans=0
            for v in range(len(transsums)):
                kans = kans + transsums[v][1]
            transition_prob_sums.append(kans)
        finalsum = 0
        for i in range(len(transition_prob_sums)):
            secondtofinalprod = transition_prob_sums[i]*targetlist[i][1]
            finalsum = finalsum+secondtofinalprod
        return finalsum