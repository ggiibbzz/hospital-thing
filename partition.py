import numpy as np
import itertools
A = [[[1,2,3],[5,4,9],[3,1,2]],[[2,5,6],[1,2,9]]]
B = itertools.product(*A)
D = [3,7,9]
for b in B:
    print(list(b))
    C = sum([np.array(list(b)[i]) for i in range(len(A))])
    C = C.tolist()
    print(C)
    if C == D:
        print('jup')
    else:
        print('nope')