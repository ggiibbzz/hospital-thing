import numpy as np
import itertools
import math
import sys
sys.setrecursionlimit(6000)

##Recursive algorithm for creating partitions of the integer n in d equal parts.
##E.g. n=5 in d=2: [5,0],[4,1],[3,2],[2,3],[1,4],[0,5]
def partition(n, d, depth=0):
    if d == depth:
        return [[]]
    return [
        item + [i]
        for i in range(n+1)
        for item in partition(n-i, d, depth=depth+1)
        ]

#makes lists unique and preserves order!
def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


#I'm keeping the next two as global variables since it is a pain to put them through multiple functions.
#######
## Probability configuration
## probabilities = [transitioning in specialty 1, transitioning in specialty 2]
trans_probs = np.array([[[0.8, 0.2], [0.0, 1.0]]])
##Entering probs = [entering in specialty 1, entering in specialty 2]
enter_probs = np.array([[1.0, 0.0]])
#######
bandwidth = 1


##Calculates the entering probability given the particular action distributed over the treatment patterns and the specialty
##E.g. if action = 3, then admstate could be [2,1,0] for specialty one.
def EnterProb(admstate, specialty):
    P = math.factorial(sum(admstate))
    for i in range(len(admstate)-1):
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
def CalcProb(state2, state1, actionnr, specialty):
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
        else:
            pass
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

    def isOverUt(self, state):
        ##We have to group all the treatment patterns together
        ## len(self.avgMatrix[0]) = n
        n= len(self.avgMatrix[0])
        for res_ind in range(self.amount):
            som = 0
            for i in range(len(self.avgMatrix[0])):
                P=0
                for d in range((len(state)//(n))):
                    ##avg_ut = np.array([[2.2,2.6],[2.6,2.2]])

                    for l in range(len(self.avgMatrix[0])):
                        P += (state[i+d*n]*trans_probs[d][l][i])
                som += P*self.avgMatrix[res_ind][i]

            if som > self.max[res_ind]*bandwidth:
                return True
            else:
                pass
        return False

class Patterns:
    def __init__(self, num_patterns):
        ##How many treatment patterns are there
        self.amount = num_patterns

class Specialties:
    def __init__(self, num_sp, max_spec):
        ## number of specialties
        self.amount = num_sp
        ## Maximum admissions per period
        self.max = max_spec

        #Since self.max exists there is only a limited amount of actions possible
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


def actionChecker(state0, L, E, S):
    ##number of treatment patterns in a specialty
    n = E.amount
    ##All possible admission distributions given a state
    actionstatess = ()
    allpossibleactions = ()
    for action in S.actions:
        if L.isOverUt(state0) == True:
            allpossibleactions = ((0,)*S.amount,)
            actionstatess = ((0,)*n*S.amount,)
        else:
            A = [0]*int(S.amount)
            actionstates=()
            for i in range(S.amount):
                A[i] = tuple(partition(action[i],n-1))
            B = itertools.product(*A)
            # print('A with action ' +str(action)+' equals '+str(A))

            for statecouple in B:
                state=[]
                addnr = 0
                for i in range(S.amount):
                    if sum(statecouple[i]) == action[i]:
                        addnr+=1
                if addnr == S.amount:
                    for statenr in range(S.amount):
                        state=state+statecouple[statenr]+[0]
                    actionstates = actionstates + tuple(state)
            action = tuple(action)
            actionstatess = actionstatess +  (actionstates,)
            allpossibleactions = allpossibleactions + (action,)
    return allpossibleactions, actionstatess

def outputFile(lijst, name):
    f = open(name+'.txt', "w+")
    for i in lijst:
        f.write(str(i)+"\n")
    f.close()

def costFunction(state, action, actiondistributions, L):
    ##We don't need to find all the states reachable with the action, since we're only looking for the worst case scenario
    possibledistributions=[]
    for i in range(len(actiondistributions)):
        if tuple(state) == tuple(actiondistributions[i][0]):
            possibledistributions = list(actiondistributions[i][1])
    states_nextperiod = []
    for distr in possibledistributions:
        staat = np.array(state)+np.array(distr)
        staat = staat.tolist()
        n = int(len(staat)/len(action))
        sumboolean = True
        for i in range(len(action)):
            if sum(distr[n*i:n*(i+1)]) == action[i]:
                pass
            else:
                sumboolean = False
        if sumboolean == True:
            states_nextperiod.append(staat)
    ## Now states_nextperiod contains all the states our action takes us to.
    ##And now for the probabilities:
    totaalsom = 0
    for nextstate in states_nextperiod:
        n = int(len(nextstate) / len(action))
        ##We need to calculate how many people use resource Lj in nextstate
        total_avgusage_per_resource = []
        som=0
        for res_numbr in range(L.amount):
            total_avgusage=0
            for specialty in range(len(action)):
                for tr_pat in range(n-1):
                    ##avg_ut = [[avg util. of res. 1 by E_1,avg ut of res. 1 by E_2], [avg ut of res. 2 by E_1,avg ut of res. 2 by E_2]]
                    ##avg_ut = np.array([[2.2,2.6],[2.6,2.2]])
                    total_avgusage += nextstate[tr_pat+(specialty*n)]*L.avgMatrix[res_numbr][tr_pat]
            Oj = L.cost[0][res_numbr]*max(0, L.cap[res_numbr]-total_avgusage)
            Bj = L.cost[1][res_numbr]*max(0, total_avgusage-L.cap[res_numbr])
            Cj = L.cost[2][res_numbr]*max(0, total_avgusage-L.max[res_numbr])
            som += Oj+Bj+Cj
        P=1
        for specialty in range(len(action)):
             P = P*CalcProb(nextstate[n*specialty:n*(specialty+1)], state[n*specialty:n*(specialty+1)], action[specialty], specialty)
        totaalsom+=P*som
    return totaalsom

def transitioner(state, L, E, S):
    n = E.amount
    d = S.amount
    possibletransitions = []
    for specialty in range(d):
        #State new looks at only one specialty
        state_specialty = state[n*specialty:n*(specialty+1)]
        trans_per_trans_i = []
        for treatment in range(n-1):
            ##i stands for how many patients we leave in E_treatment
            trans_i = []
            for i in range(state_specialty[treatment] + 1):
                lst = [[state_specialty[treatment]-i-sum(p)] + p for p in partition(state_specialty[treatment]-i, n - 2)]
                lst2=[]
                for lijst in lst:
                    lijst = lijst[0:treatment] + [i] + lijst[treatment:]
                    lst2.append(lijst)
                trans_i = trans_i+lst2
            trans_per_trans_i.append(trans_i)
        poss_combs_of_transitions_tuples = itertools.product(*trans_per_trans_i)
        poss_combs_of_transitions = []
        for comb in poss_combs_of_transitions_tuples:
            sumarray = np.array([0]*n)
            for treatment in range(n-1):
                sumarray = sumarray + np.array(comb[treatment])
                sumarray = sumarray.tolist()
            poss_combs_of_transitions.append(sumarray)
        ##Start gluing the specialties together
        possibletransitions.append(poss_combs_of_transitions)
    possibletransition_comb_tuples = itertools.product(*possibletransitions)
    semiposs_trans = []
    for comb in possibletransition_comb_tuples:
        sumlist = ()
        for i in range(len(possibletransitions)):
            sumlist = sumlist+tuple(comb[i])
        semiposs_trans.append(sumlist)

    # ##Discharge patterns excluded
    # disch = []
    # for specialty in range(d):
    #     disch = disch + [0]*(n-1)+[state[n-1+(n*specialty)]]
    # disch = np.array(disch)
    #
    # ##Add discharge to transitions
    # for i in range(len(semiposs_trans)):
    #     pos_i = np.array(semiposs_trans[i])
    #     pos_i = pos_i+disch
    #     semiposs_trans[i] = pos_i.tolist()
    # poss_trans = []
    # for semipos in semiposs_trans:
    #     if L.isOverUt(semipos) == False:
    #         poss_trans.append(semipos)
    return semiposs_trans

##Since transitioner only transitions and actionChecker only adds them lets combine those two
def posStates(state0, L, E, S):
    actions = actionChecker(state0, L, E, S)[1]
    if len(actions) == 1:
        everyposstate = tuple(transitioner(state0, L, E, S))
    else:
        transitionstates = transitioner(state0, L, E, S)
        everyposstate = ()
        for transition in transitionstates:
            for action in actions:
                combination = np.array(transition)+np.array(action)
                combination = combination.tolist()
                combination = tuple(combination)
                everyposstate = everyposstate + (combination,)
    return everyposstate


def stateSpace(state0, L, E, S):
    statelist = list(posStates(state0, L, E, S))
    nextstates = []
    for state in statelist:
        nextstates = nextstates + list(posStates(state, L, E, S))
    nextstates = statelist + nextstates
    nextstates = f7(tuple(nextstates))

    while len(nextstates) > len(statelist):
        uniquestates = nextstates[len(statelist):]
        statelist = nextstates
        nextstates = []
        i = 0
        for uniquestate in uniquestates:
            i += 1
            nextstates = nextstates + list(posStates(uniquestate, L, E, S))
            nextstates = f7(tuple(nextstates))
        nextstates = statelist + nextstates
        nextstates = f7(tuple(nextstates))
    return nextstates

def main():
    ##Number of specialties d
    d= 1
    ## maximum admission per period max_S = [max in specialty 1, max in specialty 2]
    max_S= np.array([2])

    ## NUMBER OF RESOURCES
    num_res = 1
    ## max(L_j)
    max_L = np.array([3])

    ## Number of treatment patterns
    n=2
    ## avg resource utilization per period
    ## avg_ut = [[avg util. of res. 1 by E_1,avg ut of res. 1 by E_2], [avg ut of res. 2 by E_1,avg ut of res. 2 by E_2]]
    avg_ut = np.array([[1.2,0]])
    ## Utilization cap
    cap_L = np.array([2])

    ##Cost for resource deviation idleness, excess and over
    cap_cost = np.array([[1.0],[1.5],[1.0]])

    ## We can put this in our resource, specialty and treatment pattern class
    L = Resources(num_res, max_L, avg_ut, cap_L, cap_cost)
    E = Patterns(n)
    S = Specialties(d, max_S)


    # print(posStates((4,0),L,E,S))
    # print(actionChecker((2,0),L,E,S))
    print(len(stateSpace((0,0), L, E, S)), stateSpace((0,0), L, E, S))


    # print(posStates((1, 0, 2, 3, 3, 1 ),L ,E ,S))
    # state= (0,)*S.amount*E.amount
    # state = (0,0,0,0,0,0)
    ##What is our stateList
    # statelist = stateSpace(state,[], L, E, S)
    # print(len(statelist), statelist)
    #What are the actions we can take for each statelist state
    # actionlist = actionChecker(state, L, E,S)
    # actiondistributions = actionlist[1]
    # print(actiondistributions)
    ##Put actionlist in file
    # outputFile(actionlist[0], 'actionlist')

    # cost= costFunction(state, action, actiondistributions, L)
    # print(cost)
    print('Remember we have allowed a factor of '+str(bandwidth)+' of the actual max utilization')


main()