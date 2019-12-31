import itertools


A = [([0,1],[0,2],[3,0]),([9,2],[8,3])]

B = [i for i in itertools.product(*A)]

print(B)