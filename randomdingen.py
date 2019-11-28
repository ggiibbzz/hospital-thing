def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

A = [(1, 0), (2, 0), (3, 0), (4, 0)]
Q = f7(((1,0),(2,0),(3,0),(4,0),(1,0),(5,0),(2,0),(6,0),(3,0),(7,0)))
G = Q[len(A):]
print(G)