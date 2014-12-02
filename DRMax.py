__author__ = 'jekramer'
import csv
profs = {}

with open('CharacterSkillsNoCost.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for name in reader.fieldnames:
        if name != "Psionist":
            profs[name] = set()
    for row in reader:
        for key in profs:
            test = profs[key]
            if row[key] != '' and row[key] != 'Disguise' and row[key] != 'Cover of Night' and row[key] != 'Vanish' and row[key] != 'Fade in a Crowd' and row[key] != 'Carry' and row[key] != 'Escape Bonds' and row[key] != 'Brawling' and row[key] != 'Iron Fists' and row[key] != 'Refuse' and row[key] != 'Rescue' and row[key] != 'Scrounge':
                test.add(row[key])
            profs[key] = test

disjointDict = {}
for prof1 in profs:
    set1 = profs["Printer"]
    for prof2 in profs:
        set2 = profs[prof2]
        for prof3 in profs:
            set3 = profs[prof3]
            disjointDict["Printer"+", "+prof2+", "+prof3] = len(set1 | set2 | set3)
            #print(len(set1 | set2 | set3))

maxKey = max(disjointDict, key=disjointDict.get)
maxVal = disjointDict[maxKey]
# print(maxKey)
print(maxVal)
for key, val in disjointDict.items():
    if val == maxVal:
        print(key)
maxList = maxKey.split(", ")
maxSkills = list(profs[maxList[0]] | profs[maxList[1]] | profs[maxList[2]])
maxSkills.sort()
#print(profs[maxList[0]] | profs[maxList[1]] | profs[maxList[2]])
print(maxSkills)
