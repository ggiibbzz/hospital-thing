import numpy as np
import itertools
import math

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
bandwidth = 1
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
        ## self.avgMatrix[0] has length n-1 so len(self.avgMatrix[0])+1 = n
        n= len(self.avgMatrix[0])+1
        for res_ind in range(self.amount):
            sum = 0
            for i in range(len(self.avgMatrix[0])):
                for j in range(len(state)//(n)):
                    ##avg_ut = np.array([[2.2,2.6],[2.6,2.2]])
                    sum+=(state[i+j*n]*self.avgMatrix[res_ind][i])
            if sum > self.max[res_ind]*bandwidth:
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


# def actionSpace(state, L, E, S):
#     ##Possible actions (not particular to the state)
#     poss_acts = S.actions
#     ##All possible transitions from the state to another state
#     ##For this we need to work

def actionChecker(statelist, L, S):
    ##number of treatment patterns in a specialty
    # if isinstance(state, int)
    n = int(len(statelist[0])/S.amount)
    ##All possible admission distributions given a state
    actionwithactionstates = []
    for action in S.actions:
        A = [0]*int(S.amount)
        actionstates=[]
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
                else:
                    pass
            if addnr == S.amount:
                for statenr in range(S.amount):
                    state=state+statecouple[statenr]+[0]
                actionstates.append(state)

            else:
                pass
        actionwithactionstates.append((action, actionstates))
    ##now lets make actionspace
    statewithactionstates=[]
    statewithactiondistrs=[]
    for state in statelist:
        allpossacts = []
        allpossactsdistrs = []
        for action in S.actions:
            distrs=[]
            for i in range(len(actionwithactionstates)):
                if actionwithactionstates[i][0]== action:
                    distrs = actionwithactionstates[i][1]
                    # print('distrs for state '+str(state)+ ' with action ' +str(action)+ ' equals '+str(distrs))
                else:
                    pass

                for j in range(len(distrs)):
                    staat = np.array(state)+np.array(distrs[j])
                    staat = staat.tolist()
                    if L.isOverUt(staat) == False and distrs[j] != [0]*S.amount*n:
                        allpossacts.append(tuple(action))
                        allpossactsdistrs.append(tuple(distrs[j]))
        allpossacts.append((0,)*S.amount)
        allpossactsdistrs.append((0,)*S.amount*n)
        allpossactsnodupes = list(dict.fromkeys(allpossacts))
        allpossactsdistrsnodupes = list(dict.fromkeys(allpossactsdistrs))
        statewithactionstates.append([state, tuple(allpossactsnodupes)])
        statewithactiondistrs.append([state, tuple(allpossactsdistrsnodupes)])

    return [statewithactionstates, statewithactiondistrs]

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

                #### [[0, 1, 2, 0, 1, 0], [0, 1, 2, 0, 0, 1], [0, 1, 2, 1, 0, 0], [0, 0, 3, 0, 1, 0], [0, 0, 3, 0, 0, 1], [0, 0, 3, 1, 0, 0], [1, 0, 2, 0, 1, 0], [1, 0, 2, 0, 0, 1], [1, 0, 2, 1, 0, 0]]
                lst2=[]
                for lijst in lst:
                    lijst = lijst[0:treatment] + [i] + lijst[treatment:]
                    # # print('lijst '+str(lijst))
                    # lijst2 = np.array(lijst)
                    # discharge_pat = [0] * (n - 1) + [state_specialty[n-1]]
                    # # print('discharge_pat '+str(discharge_pat))
                    # discharge_pat = np.array(discharge_pat)
                    # lijst3 = lijst2 + discharge_pat
                    # lijst = lijst3.tolist()
                    # # print('som '+str(lijst))
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
    poss_trans = []
    for comb in possibletransition_comb_tuples:
        sumlist = []
        for i in range(len(possibletransitions)):
            sumlist = sumlist+comb[i]
        poss_trans.append(sumlist)

    ##Discharge patterns excluded
    disch = []
    for specialty in range(d):
        disch = disch + [0]*(n-1)+[state[n-1+(n*specialty)]]
    disch = np.array(disch)

    ##Add discharge to transitions
    for i in range(len(poss_trans)):
        pos_i = np.array(poss_trans[i])
        pos_i = pos_i+disch
        poss_trans[i] = pos_i.tolist()
    return poss_trans

def main():
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

    ##Cost for resource deviation idleness, excess and over
    cap_cost = np.array([[1.0,1.6],[1.5,1.0],[1.0,1.0]])

    ## We can put this in our resource, specialty and treatment pattern class
    L = Resources(num_res, max_L, avg_ut, cap_L, cap_cost)
    E = Patterns(n)
    S = Specialties(d, max_S)
    ##What is our stateList
    # statelist = stateSpace(L, E, S)
    ##Put statelist in file
    # outputFile(statelist, 'statelist')
    ##Put actionlist in file
    # outputFile(actionlist[0], 'actionlist')
    state = [1,0,1,1,0,3]
    ##Checks which transitions we can obtain given the first state and gives us back a statelist of states
    statelist = transitioner(state, L, E, S)
    print(statelist)
    # statelist = [state]
    ##What are the actions we can take for each statelist state
    # actionlist = actionChecker(statelist, L,S)
    # print(actionlist)
    # cost= costFunction(state, action, actiondistributions, L)
    # print(cost)
    print('Remember we have allowed a factor of '+str(bandwidth)+' of the actual max utilization')


main()