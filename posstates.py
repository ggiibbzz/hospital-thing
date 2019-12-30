if L.isOverUt(state) is True:
    everyPossState = Transitions(state0, L, E, S)
else:
    actions = Actions()
    transitions = Transitions(state0, L, E, S)
    everyPossState = tuple()
    for trans in transitions:
        for action in actions:
            combination = np.array(transition)+np.array(action)
            combination = combination.tolist()
            combination = tuple(combination)
            everyposstate = everyposstate + (combination,)
return everyposstate