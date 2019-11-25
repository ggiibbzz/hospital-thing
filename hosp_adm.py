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


#I'm keeping the next two as global variables since it is a pain to put them through multiple functions.
#######
## Probability configuration
## probabilities = [transitioning in specialty 1, transitioning in specialty 2]
trans_probs = np.array([[[0.4, 0.1, 0.5], [0.1, 0.3, 0.6], [0.0, 0.0, 1.0]], [[0.2, 0.1, 0.7], [0.1, 0.2, 0.7], [0.0, 0.0, 1.0]]])
##Entering probs = [entering in specialty 1, entering in specialty 2]
enter_probs = np.array([[0.5, 0.5, 0.0], [0.4, 0.6, 0.0]])
#######



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
        ## self.avgMatrix[0] has length n-1 so len(self.avgMatrix[0])+1 = n
        n= len(self.avgMatrix[0])+1
        for res_ind in range(self.amount):
            sum = 0
            for i in range(len(self.avgMatrix[0])):
                for j in range(len(state)//(n)):
                    ##avg_ut = np.array([[2.2,2.6],[2.6,2.2]])
                    sum+=(state[i+j*n]*self.avgMatrix[res_ind][i])
            if sum > self.max[res_ind]*1.1:
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


def actionSpace(statelist, L, S):
    ##number of treatment patterns in a specialty
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
def stateSpace(L, E, S):
    ##Find maximum amount of people in a single treatment pattern
    max_ut = max(L.max)
    min_avg_ut = max(L.max)
    for i in range(len(L.avgMatrix)):
        if min(L.avgMatrix[i])<min_avg_ut:
            min_avg_ut = min(L.avgMatrix[i])
    ##max_ut//min_avg_ut will be an upper bound
    N=max_ut//min_avg_ut
    N=N*1.5
    B = [*range(int(N))]
    A = itertools.product(B, repeat= E.amount-1)
    C=[]
    for semistate in A:
        semistate = list(semistate)+[0]
        C.append(semistate)
    D = itertools.product(C, repeat= S.amount)
    statespace = []
    for state in D:
        staat=[]
        for i in range(len(state)):
            staat = staat+state[i]
        if L.isOverUt(list(staat)) == False:
            statespace.append(staat)
    return statespace

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
        for specialty in range(len(action)):
            totaalsom += CalcProb(nextstate[n*specialty:n*(specialty+1)], state[n*specialty:n*(specialty+1)], action[specialty], specialty)*som
    return totaalsom

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
    statelist = stateSpace(L, E, S)
    ##Put statelist in file
    outputFile(statelist, 'statelist')
    ##What is our actionlist
    actionlist = actionSpace(statelist, L,S)
    actiondistributions = actionlist[1]
    print(actiondistributions)
    ##Put actionlist in file
    # outputFile(actionlist[0], 'actionlist')
    state = [0,0,0,1,1,0]
    action = [0,1]
    cost= costFunction(state, action, actiondistributions, L)
    print(cost)
    print('Remember we have allowed a factor of 1.1 of the actual max utilization')


main()