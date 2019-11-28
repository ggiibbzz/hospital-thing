# policy configuration
## m - number of specialities; the next m lines - maximum admission capacity per period (maxS_d)
1
2
## k - number of resources; the next k lines - available capacity per period (maxL_j) of each resource L_j
1
3
## n - number of treatment patterns; the next n-1 line - average resource utilization per period L_ij (matrix [n-1][k])
2
1.2
## the next k lines - desired utilization level for each resource N_j
2
## the next 3 lines - cost for deviation from desired utilization level for each resource (idleness, excess and over cost)
1.0
1.5
1.0

# probability configuration (m matrices, each matrix (size [n][n]) is the transition probability for one speciality)
0.8	0.2
0.0	1.0

## entering probability (matrix size[n][m])
1.0
0.0
