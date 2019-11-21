import itertools
B = [3,5]
for i in range(len(B)):
    B[i] = [*range(B[i]+1)]
print(B)
#B= ([*range(3+1)],[*range(5+1)])
#print(B)
A = itertools.product(*B)
for i in A:
    i = list(i)
    print(list(i))