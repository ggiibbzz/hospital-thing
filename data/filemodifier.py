invoer = open("config04_states.md", 'r')
uitvoer = open("statespacesan4.txt", 'w')

lineNr = 1
print(69)
for line in invoer:
    print(str(line))
    if lineNr > 2:
        lineContent = line.rstrip()
        tupel = str()
        letterIndex = 1
        afterHaak = False
        while lineContent[letterIndex-1] != ")":
            if lineContent[letterIndex] == "(":
                afterHaak = True
            print(lineContent[letterIndex])
            if afterHaak == True:
                tupel = tupel + lineContent[letterIndex]
            letterIndex+= 1
        print(tupel)
        uitvoer.write(str(tupel)+"\n")
    lineNr += 1
invoer.close()
uitvoer.close()