import numpy as np
import itertools

state2=[2,3,2]
state1=[3,3,5]
actionnr = 3
B=[]
C=[]
for i in range(len(state2)-1):
    B.append([*range(state2[i]+1)])
A = itertools.product(*B)
for action in A:
    action = list(action)+[0]
    if sum(action)== actionnr:
        C.append(action)
    else:
        pass
print(C)