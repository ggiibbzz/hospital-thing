import numpy as np
import itertools

##Recursive algorithm for creating partitions of the integer n in d equal parts.
def partition(n, d, depth=0):
    if d == depth:
        return [[]]
    return [
        item + [i]
        for i in range(n+1)
        for item in partition(n-i, d, depth=depth+1)
        ]


state2=np.array([2,3,4,2])
state1=[4,3,1,6]
actionnr = 3
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
    targetlist.append(target.tolist())

##Sumlist will be a list of lists of possible transitions for every target
sumlist= []

##Now we want to work for each target alone
for targ in targetlist:
    ##Create a list for transitions
    trans = []
    ##Create a list for the sums of transitions
    transsums = []
    ##Let us iterate over the elements in target, except for the last element since that is the discharge
    for j in range(len(targ)-1):
        ##list of transitions created by going over the partition created by varying component j
        lst3=[]
        ## To partition sumlist in a component for every j, we must create a new list. sumlist = [[...], [...], ..., [...]]
        for i in range(targ[j]+1):
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
        if som.tolist() == targ:
            transsums.append(prod)
        else:
            pass
    print(transsums)
print(targetlist)
