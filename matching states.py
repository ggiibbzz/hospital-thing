from ast import literal_eval
statenspatie = open("statenspatie.txt", 'r')
statespacesan = open("statespacesan.txt",'r')

statenspatielijst = []
for state in statenspatie:
    listContent = state.rstrip()
    tupel = literal_eval(listContent)
    statenspatielijst.append(tupel)
print(statenspatielijst)

statespacesanlijst = []
for state in statespacesan:
    listContent = state.rstrip()
    tupel = literal_eval(listContent)
    statespacesanlijst.append(tupel)
print(statespacesanlijst)

uniquetupels = []
for state in statespacesanlijst:
    if state not in statenspatielijst:
        uniquetupels.append(state)
print(len(uniquetupels), uniquetupels)



statespacesan.close()