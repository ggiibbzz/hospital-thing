import numpy as np
##For matrix addition and multiplication

import itertools
##For cartesian products and such

import math
##For math stuff

from ast import literal_eval

# import time












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

    def isOverUt(self, state, E):
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
                        P += (state[l+d*n]*E.trans_probs[d][l][i])
                som += P*self.avgMatrix[res_ind][i]

            if som > self.max[res_ind]:
                return True
            else:
                pass
        return False

class Patterns:
    def __init__(self, num_patterns, trans_probs, enter_probs):
        ##How many treatment patterns are there
        self.amount = num_patterns
        self.transitions = dict()
        self.states = set()
        self.trans_probs = trans_probs
        self.enter_probs = enter_probs

    def addTransitions(self, specialty, treatmentPattern, size, transitions):
        self.transitions[(specialty, treatmentPattern, size)] = transitions

class Specialties:
    def __init__(self, num_sp, max_spec):
        ## number of specialties
        self.amount = num_sp
        ## Maximum admissions per period
        self.max = max_spec

        #Since self.max exists there is only a limited amount of actions possible
        self.actions = []
        self.actionDistributions = []
        self.__Actions(num_sp, max_spec)

    def Actions(self, amount, max):
        B=[]
        for i in range(len(max)):
            B.append([*range(max[i]+1)])
        A = itertools.product(*B)
        for action in A:
            self.actions.append(list(action))
    __Actions = Actions

    def addActionDistributions(self, actionDistributions):
        self.actionDistributions = actionDistributions











def outputFile(lijst, name):
    f = open(name+'.txt', "w+")
    for i in lijst:
        f.write(str(i)+"\n")
    f.close()















##ATTENTION: PARTITION IS AN AUXILIARY FUNCTION, IT DOESN'T ACTUALLY OUTPUT A PARTITION OF N IN D PARTS LIKE THIS:
##E.g. n=3 in d=3, [[3,0,0],[2,1,0],[2,0,1],[1,2,0],[1,1,1],[1,0,2],[0,3,0],[0,2,1],[0,1,2],[0,0,3]]

##Recursive algorithm for creating partitions of each integer UP TO n in d parts.
##E.g. n=3 in d=3: [0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [0, 1, 0], [1, 1, 0], [2, 1, 0], [0, 2, 0], [1, 2, 0], [0, 3, 0], [0, 0, 1], [1, 0, 1], [2, 0, 1], [0, 1, 1], [1, 1, 1], [0, 2, 1], [0, 0, 2], [1, 0, 2], [0, 1, 2], [0, 0, 3]
def partition(n, d, depth=0):
    if d == depth:
        return [[]]
    return [
        item + [i]
        for i in range(n+1)
        for item in partition(n-i, d, depth=depth+1)
        ]











#makes lists unique and preserves order!
#I am not using set() since it doesn't keep the order I use
def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]












#######











##Calculates the entering probability given the particular action distributed over the treatment patterns and the specialty
##E.g. if action = 3, then admstate could be [2,1,0] for specialty one.
def EnterProb(admstate, specialty, E):
    P = math.factorial(sum(admstate))
    for i in range(len(admstate)-1):
        if i == len(admstate)-1:
            P = P*(E.enter_probs[specialty][i])**(sum(admstate)-sum(admstate[:len(admstate)-2]))/math.factorial(sum(admstate)-sum(admstate[:len(admstate)-2]))
        else:
            P = P*(E.enter_probs[specialty][i])**(admstate[i])/(math.factorial(admstate[i]))
    return P












##Calculates the transition probability given the PARTICULAR(!) transition tuple over the treatment patterns and the specialty
##E.g. Say we want to go to state_(t+1): [0,2,2] from state_t [3,1,1] with action 0, then we have a two-tuple ([0,2,1],[0,0,1])
##Where the first component of the tuple represents x_11 = 0, x_12 = 2, x_13=1 and the second tuple: x_21=0, x_22=0 and x_23=1
def TransProbs(comptuples, specialty, E):
    ## i will signify in which treatment pattern we're at on time period t
    P=1
    for i in range(len(comptuples)):
        P = P*math.factorial(sum(comptuples[i]))
        for j in range(len(comptuples[i])):
            P = P * (E.trans_probs[specialty][i][j]) ** (comptuples[i][j]) / (math.factorial(comptuples[i][j]))
    return P














##ATTENTION, IN CASE THERE ARE MORE THAN ONE SPECIALTY DO NOT ATTEMPT TO CALCULATE THE PROBABILITY OF AN ENTIRE STATE
##YOU NEED TO SPLIT IT UP IN PARTS FOR EACH SPECIALTY. E.G. CalcProb IN CASE OF:
##first state [1,0,1,0,2,3], next state [2,3,0,0,2,2], action (4,2), WITH E.amount = 3 AND S.amount = 2
##MUST BE CALCULATED LIKE: CalcProb([2,3,0], [1,0,1], 4, 0, E)*CalcProb([0,2,2], [0,2,3], 2, 1, E)

##Given state_(t+1) (state2), state_t (state1), action and specialty this will calculate the probability of going from one state to another
##It will obviously use the functions given above (EnterProb() and TransProbs())
def CalcProb(state2, state1, actionnr, specialty, E):
    ##If the patients in the next state do not match the patients in each effective treatment pattern + actionnr return probability 0
    if sum(state2) != sum(state1[:len(state1)-1])+actionnr:
        return 0

    ## Else continue
    else:

        ##If state2 = (8,11,3), then B = [[0,1,2,3,4,5,6,7,8],[0,1,2,3,4,5,6,7,8,9,10,11]]
        B=[]

        ##List of all possible action distributions given an action
        ##E.g. if the action is 2, then C = [[2,0],[1,1],[0,2]]
        C=[]

        ##Targetlist is a list for all targets I want to reach by applying only transitions and their respective entering probability.
        ##One target is defined as state2 - (minus) action distribution
        ##E.g. if state2 = [2,2,2] and action = 1, then the possible action distributions are:
        ##[1,0,0] and [0,1,0] and thus the possible targets are: [1,2,2] and [2,1,2]
        ##So targetlist = [[[1,2,2],P([1,0,0])], [[2,1,2],P([0,1,0])]]
        targetlist=[]

        ##Make B from description I gave above
        ##If state2 = (8,11,3), then B = [[0,1,2,3,4,5,6,7,8],[0,1,2,3,4,5,6,7,8,9,10,11]] and nothing for discharge pattern
        for i in range(len(state2)-1):
            B.append([*range(state2[i]+1)])
        ##A is a cartesian product of the sets in B
        ##E.g. B = [[1,2],[7,8]], then A = {(1,7),(1,8),(2,7),(2,8)}
        A = itertools.product(*B)

        ##this creates the list of action distributions C of above
        for action in A:
            ##We add the discharge pattern which is 0
            action = list(action)+[0]
            ##If the sum of the amount of patients equal the action then add the action distribution to C
            if sum(action)== actionnr:
                C.append(action)

        ##Note that we could have created C by means of the partition() function above, but then we would have to trim
        ##C by taking out all the action distributions where there are too many people being added.

        ##Let us now begin to
        for action in C:
            ##Target is the target we want to hit by doing only transitions
            target = np.array(state2)-np.array(action)
            ##Now we add the target and its action probability to targetlist
            targetlist.append([target.tolist(),EnterProb(action, specialty, E)])


        ##Above we got all the probabilities you could obtain by adding patients in the next period (entering prob).
        ##Now we calculate the probabilities you can get by moving patients around.
        transition_prob_sums = []
        ##Now we want to work for each target alone
        for targ in targetlist:
            ##Create a list for transitions
            trans = []
            ##Create a list for the sums of transitions
            transsums = []


            ##Let us iterate over the elements in target, except for the last element since that is the discharge
            for j in range(len(targ[0])-1):
                ##list of transitions created by going over the partition created by varying component j
                lst3=[]
                ## To partition sumlist in a component for every j, we must create a new list. sumlist = [[...], [...], ..., [...]]
                for i in range(targ[0][j]+1):
                    ##Since i stands for how many patients we keep in a treatment pattern we need to calculate how many we have to distribute
                    n = state1[j]-i
                    d = len(state1)-1

                    ##This will partition the number n in d parts
                    ##E.g. n= 4, d=3, then [[n - sum(p)] + p for p in partition(n, d - 1)] gives:
                    ##[4,0,0],[3,1,0],[3,0,1],[2,2,0],[2,1,1],[2,0,2],[1,3,0],[1,2,1],[1,1,2],[1,0,3],[0,4,0],[0,3,1],
                    ##[0,2,2],[0,1,3],[0,0,4].
                    lst = [[n - sum(p)] + p for p in partition(n, d - 1)]
                    ##What we have done up until this point is, given a target distribution and initial state: E.g. Targ = [2,3,4,5] and InitState = [10,4,0,1]
                    ##We have taken a single non-discharge component j in Targ and let i be iterated in the range of Targ[j]
                    ##So, take j=1, then Targ[j]=3 and thus i is iterated in the range [0,1,2,3].
                    ##Next, we took n = InitState[j]-i and d the number of patterns-1, ! THIS IS NOT BECAUSE OF THE DISCHARGE PATTERN, BUT RATHER BECAUSE WE ARE NOT USING COMPONENT j!
                    ##So in our example, let us say we are in the 3rd iteration, then i = 2 and thus
                    ##n = 4-2 and d = 3. (I realise that recalculating the same number is inefficient/sloppy, but I do not
                    ##think it is very expensive or time consuming.) Now we have created lst, which in our case is:
                    ##lst = [[2,0,0],[1,1,0],[1,0,1],[0,2,0],[0,1,1],[0,0,2]]
                    ##What will we do with lst? Well essentially we have distributed n people over the other treatment patterns,
                    ##While we kept i people in treatment pattern j, therefore we want to add component j in each list in lst.
                    ##lst2 will therefore be:
                    ##lst2 = [[2,2,0,0],[1,2,1,0],[1,2,0,1],[0,2,2,0],[0,2,1,1],[0,2,0,2]]
                    lst2=[]
                    for lijst in lst:
                        lijst = lijst[0:j] + [i] + lijst[j:]
                        lst2.append(lijst)

                    ##lst3 is a superlist of lst2 for all components. this means that it has all of the elements of lst2 for all components i.
                    ##We need this list so we can can make the following cartesian product:
                    ##[transitions by varying component 0]x[trans component 1]x...x[trans component E.amount-1]
                    ##This is equivalent with
                    ##[lst3, j=0]x[lst3, j=1]x...x[lst3, j=len(targ[0])-1]
                    lst3 = lst3 + [element for element in lst2]
                ##trans = [[lst3, j=0],[lst3, j=1],...,[lst3, j=len(targ[0])-1]]
                trans.append(lst3)
            ##transprods is exactly the cartesian product set I wanted, its class is not accessible by the usual operation
            ##transprods[k], but you can iterate over transprods like we do in our for-loop
            transprods = itertools.product(*trans)
            for prod in transprods:
                ##This is where the inefficiency of CalcProb() comes in. I am manually checking if the sum of the
                ##distributions equal the sum of the people in the first state (that are not in the discharge state).
                ##For example: take my above Targ = [2,3,4,5] and InitState [10,4,0,1].
                ##Then a prod in transprods looks like: ([0,1,5,2],[0,2,0,0],[0,0,0,0]), what I want is that
                ##[0,1,5,2]+[0,2,0,0]+[0,0,0,0] equals Targ = [2,3,4,5], but in this case it does not, because
                ##[0,1,5,2]+[0,2,0,0]+[0,0,0,0] = [0,3,5,2] != [2,3,4,5]

                #som in our example is [0,3,5,2]
                som = sum([np.array(list(prod)[u]) for u in range(len(state2)-1)])

                #[0,3,5,2] != [2,3,4,5] and therefore, pass.
                if som.tolist() == targ[0]:
                    #If it accepts, then add the probability we were able to calculate through transprobs.
                    transsums.append([prod, TransProbs(prod, specialty, E)])
            ##transsums is the list of all possible combinations of transitions ! NOT POSSIBLE ACTION DISTRIBUTIONS !
            ##with their respective transition probability


            ##([1, 3, 4, 2], [1, 0, 0, 3], [0, 0, 0, 0]) is a prod where the if-statement is TRUE, therefore
            ##transsums is definitely not empty.


            #Initial probability is 0
            kans=0

            #For v in the range of transsums
            for v in range(len(transsums)):
                ##P(transsums[v][0])=transsums[v][1], now add it to the total probability
                kans = kans + transsums[v][1]

            ##Now transition_prob_sums is the total probability to go from state1 to Targ
            transition_prob_sums.append(kans)
            #Iterate until the end of targetlist

        #Finalsum will be our final probability and we start it at 0
        finalProb = 0
        for i in range(len(transition_prob_sums)):
            ##distrProb is the probability of going from state2 to targ times the probability of going from Targ to state1.
            ##essentially, the probability given a distribution of the action.
            distrProb = transition_prob_sums[i]*targetlist[i][1]
            ##Since we add up all the above probabilities, finalsum will be the total probability of reaching a state given an action
            finalProb = finalProb+distrProb
        return finalProb



























##Actionchecker: given a state, it will see if it's overutilized, and if it isn't then we return a tuple of all possible actions
##and a tuple of possible action distributions.
##E.g. suppose S.amount = 1 and E.amount = 3, S.max = 2
##If [1,2,3] is not overutilized, then actionChecker([1,2,3],L,E,S) = (((0,),(1,),(2,)),((0,0,0),(1,0,0),(0,1,0),(2,0,0),(1,1,0),(0,2,0)))
def actionChecker(state0, L, E, S):
    ##number of treatment patterns in a specialty
    n = E.amount
    ##All possible admission distributions given a state
    actionstatess = ()

    ##All possible actions
    allpossibleactions = ()
    ##If the initial state is overutilizing the resources, then do not add new people
    if L.isOverUt(state0, E) == True:
        allpossibleactions = ((0,) * S.amount,)
        actionstatess = ((0,) * n * S.amount,)
        return allpossibleactions, actionstatess
    else:
        if len(S.actionDistributions)==0:
            for action in S.actions:
                A = [0]*int(S.amount)
                for i in range(S.amount):
                    ##n-2 should actually be (n-1)-1 , that first n-1 because we do not want to add to the discharge pattern,
                    ##And the second because making a partition of the number k in n parts is calculated by
                    ##[[k - sum(p)] + p for p in partition(k, n - 1)]
                    A[i] = tuple([p +[0] for p in partition(action[i], n - 1)])

                # ##Suppose action = (2,3), and n = E.amount= 3 then A will equal
                # ##[([0,0,0],[1,0,0],[0,1,0],[2,0,0],[1,1,0],[0,2,0]),([0,0,0],[1,0,0],[0,1,0],[2,0,0],[1,1,0],[0,2,0],[3,0,0],[2,1,0],[1,2,0],[0,3,0])]
                # ##A will be a list of tuples of lists like above
                # A = [0]*int(S.amount)
                # actionstates=()
                # for i in range(S.amount):
                #     ##n-2 should actually be (n-1)-1 , that first n-1 because we do not want to add to the discharge pattern,
                #     ##And the second because making a partition of the number k in n parts is calculated by
                #     ##[[k - sum(p)] + p for p in partition(k, n - 1)]
                #     A[i] = tuple([[action[i] - sum(p)] + p +[0] for p in partition(action[i], n - 2)])
                #     print(i, action, action[i], A[i])
                # # ##B is a cartesian product of the tuples in A
                # # ##so A[0]xA[1]x...xA[S.amount]
                # # B = itertools.product(*A)
                # #
                # # ##statecouple could look like this: ([0,1], [1,2]) where [0,1] comes from A[0] and [1,2] comes from A[1]
                # # for statecouple in B:
                # #     ##Given a statecouple we are going to put them in one entire state, called state[]
                # #     state=[]
                # #     ##Let us add the discharge pattern (we add 0)
                # #     for statenr in range(S.amount):
                # #         state=state+statecouple[statenr]+[0]
                # #     ##We add state[] in the tuple actionstates as a tuple
                # #     actionstates = actionstates + (tuple(state),)
                # #
                # # action = tuple(action)
                # #
                # # #Tuple of possible states we can get to given an action
                # # actionstatess = actionstatess + actionstates
                actionstatess = A
                #
                # #Tuple of actions we can take
                # allpossibleactions = allpossibleactions + (action,)

            S.addActionDistributions(actionstatess)
    return tuple(S.actions), tuple(S.actionDistributions)


















##Given a state, transitioner will give all possible next states by only transitioning fron one treatment pattern to another,
##So we do not add patients. NO ACTION USED.
##E.g. transitioner((1,0,0,2,0,1), L, E, S), outputs:
##[([0, 1, 0], [0, 0, 1], [1, 0, 0]), ([0, 2, 0], [0, 1, 1], [0, 0, 2], [1, 1, 0], [1, 0, 1], [2, 0, 0])]
##list[tuple(list[],list[],list[]), tuple(list[],list[],list[],list[],list[],list[])]

def transitioner(state, L, E, S):
    #n is amount of treatment patterns
    n = E.amount

    #d is amount of specialties
    d = S.amount

    # print(11111, state)
    possibletransitions = []
    for specialty in range(d):
        #state_specialty takes the treatment patterns from one specialty
        state_specialty = state[n*specialty:n*(specialty+1)]

        ##This will be a list(lists obtained by varying component from 0 to n-1)
        trans_per_trans_i = []
        #for treatment pattern that is not the discharge pattern
        if (specialty, state_specialty, -1) in E.transitions.keys():
            poss_combs_of_transitions = E.transitions[(specialty,state_specialty, -1)]
        else:
            for treatment in range(n-1):
                trans_i = []
                if (specialty, treatment, state_specialty[treatment]) in E.transitions.keys():
                    trans_i = E.transitions[(specialty, treatment, state_specialty[treatment])]
                else:
                    ##i stands for how many patients we leave in a treatment pattern
                    ##And thus trans_i is the possible transitions we get if we vary i from 0 to state_specialty[treatment]
                    for i in range(state_specialty[treatment] + 1):
                        ##if i stands for how many people we leave, then state_specialty[treatment]-i stands for how many people we redistribute
                        lst = [[state_specialty[treatment]-i-sum(p)] + p for p in partition(state_specialty[treatment]-i, n - 2)]
                        ##suppose state_specialty = [2,50,1], treatment = 0, i=1, then lst = [[51,1],[50,2]]
                        lst2=[]
                        ##Take the same example, lst2 would be: [[1,51,1],[1,50,2]]
                        for lijst in lst:
                            lijst = lijst[0:treatment] + [i] + lijst[treatment:]
                            lst2.append(lijst)
                        trans_i = trans_i+lst2
                    E.addTransitions(specialty, treatment, state_specialty[treatment], trans_i)
                trans_per_trans_i.append(trans_i)

            ##All the possible combinations of redistributions from all possible components
            ##Cartesian product
            poss_combs_of_transitions_tuples = itertools.product(*trans_per_trans_i)

            ##The difference between this and poss_combs_of_transitions_tuples, is that this one will have the states added up to each other
            poss_combs_of_transitions = []


            for comb in poss_combs_of_transitions_tuples:
                #np.array() + np.array() returns a single np.array() by componentwise addition
                sumarray = np.array([0]*n)
                for treatment in range(n-1):
                    sumarray = sumarray + np.array(comb[treatment])
                    sumarray = sumarray.tolist()
                poss_combs_of_transitions.append(sumarray)
            E.addTransitions(specialty, state_specialty, -1, poss_combs_of_transitions)
        ##Start gluing the specialties together by putting all the combinations in a list
        possibletransitions.append(tuple(poss_combs_of_transitions))


    # ##Since each specialty has a different list for combinations, we will make a cartesian product of all the specialties
    # possibletransition_comb_tuples = itertools.product(*possibletransitions)
    #
    # ##Let us start putting all the different combinations in one entire state of dimension n*d
    # semiposs_trans = []
    # for comb in possibletransition_comb_tuples:
    #     sumlist = ()
    #     for i in range(len(possibletransitions)):
    #         sumlist = sumlist+tuple(comb[i])
    #     semiposs_trans.append(sumlist)
    return possibletransitions

















##Since transitioner only transitions and actionChecker only adds them lets combine those two
def posStates(state0, L, E, S):
    ##Remember that the second result in actionChecker is all the distributions of the action. so actions() here is a misnomer
    ##and does not mean the amount of people we add in each specialty, but rather the amount of people we add in each treatment pattern.
    ##Or in other words, actions() here actually means action distributions
    actions = actionChecker(state0, L, E, S)[1]
    ##len(actions) == 1 if and only if the only action distribution possible is (0,)*E.amount and thus we only need transitioner(state)
    if len(actions) == 1:
        possibletransitions = tuple(transitioner(state0, L, E, S))
        ##Since each specialty has a different list for combinations, we will make a cartesian product of all the specialties
        possibletransition_comb_tuples = itertools.product(*possibletransitions)

        ##Let us start putting all the different combinations in one entire state of dimension n*d
        semiposs_trans = []
        for comb in possibletransition_comb_tuples:
            sumlist = ()
            for i in range(len(possibletransitions)):
                sumlist = sumlist+tuple(comb[i])
            semiposs_trans.append(sumlist)
        everyposstate = semiposs_trans

    ##in the other case there exist non-zero action distributions
    else:
        #first we calculate all the possible states you can get by transitioning
        transitionstates = transitioner(state0, L, E, S)
        # print(444444)
        everyposstate_combs = []
        for specialty in range(len(transitionstates)):
            pos_states_specialty = []

            #This is the cartesian product of the set of transitions with the set of admissions for a specific specialty
            trans_and_act_per_specialty = itertools.product(transitionstates[specialty],actions[specialty])
            #now we add the two together component-wise
            for comb_prod in trans_and_act_per_specialty:
                # add transition up with an action distribution
                combination = np.array(comb_prod[0])+np.array(comb_prod[1])
                combination = combination.tolist()
                combination = tuple(combination)
                pos_states_specialty.append(combination)
            everyposstate_combs.append(pos_states_specialty)

        everyposstate_prod = itertools.product(*everyposstate_combs)
        everyposstate = ()
        for posstate_comb in everyposstate_prod:
            if posstate_comb not in E.states:
                E.states.add(posstate_comb)
                posstate = itertools.chain(*posstate_comb)
                everyposstate = everyposstate + (tuple(posstate),)
    everyposstate = set(everyposstate)
    # print(555555, everyposstate)
    return everyposstate


















##We are also interested in what the possible states are if we are given the action, I will not go into full detail here
##since all the methods were already used once
##The output will look something like this:
##[(state_specialty_0, state_specialty_1, ... , state_specialty_n), (state_specialty_0, state_specialty_1, ... , state_specialty_n), (state_specialty_0, state_specialty_1, ... , state_specialty_n), ...]
def posStatesGivenAction(state0, action, L, E, S):
    possTrans = transitioner(state0, L, E, S)
    n = E.amount
    A = []
    possActionDistrs = []
    for i in range(S.amount):
        A.append(tuple([[action[i]-sum(p)] + p + [0] for p in partition(action[i], n-2)]))
    possStates = []
    for specialty in range(S.amount):
        B = itertools.product(possTrans[specialty], A[specialty])
        possStates_Specialty = tuple()
        for combination in B:
            som = np.array(combination[0]) + np.array(combination[1])
            som = som.tolist()
            possStates_Specialty = possStates_Specialty + (som,)
        possStates.append(possStates_Specialty)
    possStates_combs = tuple([b for b in itertools.product(*possStates)])
    return possStates_combs

def stateSpace(state0, L, E, S):
    statelist = list(posStates(state0, L, E, S))
    nextstates = []
    for state in statelist:
        nextstates = nextstates + list(posStates(state, L, E, S))
    nextstates = statelist + nextstates
    nextstates = f7(tuple(nextstates))
    print(nextstates)

    while len(nextstates) > len(statelist):
        length = len(statelist)
        uniquestates = nextstates[len(statelist):]
        statelist = nextstates
        nextstates = []
        # i = 0
        for uniquestate in uniquestates:
            # i += 1
            nextstates = nextstates + list(posStates(uniquestate, L, E, S))
        nextstates = statelist + nextstates
        nextstates = f7(tuple(nextstates))
        print(nextstates)
    return nextstates

def costFunction(state, action, L, E, S):
    allPossStates = posStatesGivenAction(state, action, L, E, S)
    ##And now for the probabilities:
    totaalsom = 0
    for nextstate in allPossStates:
        n = E.amount
        ##We need to calculate how many people use resource Lj in nextstate
        som=0
        for res_numbr in range(L.amount):
            total_avgusage=0
            for tr_pat in range(n - 1):
                statesSum = 0
                for specialty in range(len(action)):
                    ##avg_ut = [[avg util. of res. 1 by E_1,avg ut of res. 1 by E_2], [avg ut of res. 2 by E_1,avg ut of res. 2 by E_2]]
                    ##avg_ut = np.array([[2.2,2.6],[2.6,2.2]])
                    statesSum += nextstate[specialty][tr_pat]
                total_avgusage += statesSum*L.avgMatrix[res_numbr][tr_pat]
            Oj = L.cost[0][res_numbr]*max(0, L.cap[res_numbr]-total_avgusage)
            Bj = L.cost[1][res_numbr]*max(0, total_avgusage-L.cap[res_numbr])
            Cj = L.cost[2][res_numbr]*max(0, total_avgusage-L.max[res_numbr])
            som += Oj+Bj+Cj
        P=1
        for specialty in range(len(action)):
             P = P*CalcProb(nextstate[specialty], state[n*specialty:n*(specialty+1)], action[specialty], specialty, E)
        totaalsom+=P*som
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
    avg_ut = np.array([[2.2,2.6,0],[2.6,2.2,0]])
    ## Utilization cap
    cap_L = np.array([4,4])

    ##Cost for resource deviation idleness, excess and over
    cap_cost = np.array([[1.0,1.6],[1.5,1.0],[1.0,1.0]])

    ## Probability configuration
    ## probabilities = [transitioning in specialty 1, transitioning in specialty 2]
    trans_probs = np.array([[[0.4, 0.1, 0.5], [0.1, 0.3, 0.6], [0.0, 0.0, 1.0]], [[0.2, 0.1, 0.7], [0.1, 0.2, 0.7], [0.0, 0.0, 1.0]]])
    ##Entering probs = [entering in specialty 1, entering in specialty 2]
    enter_probs = np.array([[0.5, 0.5, 0.0], [0.4, 0.6, 0.0]])

    ## We can put this in our resource, specialty and treatment pattern class
    L = Resources(num_res, max_L, avg_ut, cap_L, cap_cost)
    E = Patterns(n, trans_probs, enter_probs)
    S = Specialties(d, max_S)

    #Creates state space
    # start = time.time()
    # A = stateSpace((0,0,0,0,0,0),L,E,S)
    # end = time.time()
    # print(end - start)
    # print(len(A))
    # outputFile(A, "statenspatie")



    ##Since we do not want to recalculate the state space all the time we just save it externally and call it up
    statenspatie = open("statespace.txt", 'r')
    statespace = []
    for state in statenspatie:
        listContent = state.rstrip()
        tupel = literal_eval(listContent)
        statespace.append(tupel)
    statenspatie.close()

    # som = 0
    # alreadyused = set()
    # for state in statespace:
    #     if state[0:3] not in alreadyused:
    #         alreadyused.add(state[0:3])
    #         print(state[0:3])
    #         som += CalcProb(tuple(state[0:3]), (2, 5, 0), 0, 1, E)
    # print(som)

    ##Time for action space
    # statewithactions = []
    # for state in statespace:
    #     actions = actionChecker(state, L, E, S)[0]
    #     statewithactions.append((state, actions))
    # outputFile(statewithactions, "actionspace")

    print(costFunction((0,0,0,0,0,0),(1,1), L, E, S))
    # print(costFunction((0,0,0,1,2,5),(0,2),L,E,S))
main()