__author__ = 'jekramer'
import csv
profs = {}

with open('CharacterSkillsNoCost.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for name in reader.fieldnames:
        #FOR IRONS
        if name != "Psionist":
        #Restriction lists
        #if name != "Sniper" and name != "Assassin" and name != "Spy" and name != "Thief" and name != "Scoundrel" and name != "Gambler":
            if name != "Tinker" and name != "Sniper": #and name != "Saw Bones":
                profs[name] = set()
    for row in reader:
        for key in profs:
            test = profs[key]
            #FOR NOA
            #if row[key] != '' and row[key] != 'Building Tomorrow' and row[key] != 'Challenge' and row[key] != 'Faith Healing' and row[key] != 'First Aide' and row[key] != 'Mind Resistance' and row[key] != 'Patch Job':
            #FOR IRONS
            if row[key] != '' and row[key] != 'Disguise' and row[key] != 'Cover of Night' and row[key] != 'Vanish' and row[key] != 'Fade in a Crowd' and row[key] != 'Carry' and row[key] != 'Escape Bonds' and row[key] != 'Brawling' and row[key] != 'Iron Fists' and row[key] != 'Refuse' and row[key] != 'Rescue' and row[key] != 'Scrounge':
            #FOR RETROGRADES
            #if row[key] != '' and row[key] != 'Barridcade' and row[key] != 'Cover of Night' and row[key] != 'Disguise' and row[key] != 'Escape Bonds' and row[key] != 'Feign Death' and row[key] != 'Melee Weapon Standard' and row[key] != 'Scrounge':
                test.add(row[key])
            profs[key] = test

disjointDict = {}
#Set your current classes
firstClass = "Printer"
secondClass = ""
for prof1 in profs:
    if firstClass != "":
        set1 = profs[firstClass]
    else:
        set1 = profs[prof1]
    for prof2 in profs:
        if secondClass != "":
            set2 = profs[secondClass]
        else:
            set2 = profs[prof2]
        for prof3 in profs:
            set3 = profs[prof3]
            if firstClass != "" and secondClass == "":
                disjointDict[firstClass+", "+prof2+", "+prof3] = len(set1 | set2 | set3)
            elif firstClass != "" and secondClass != "":
                disjointDict[firstClass+", "+secondClass+", "+prof3] = len(set1 | set2 | set3)
            else:
                disjointDict[prof1+", "+prof2+", "+prof3] = len(set1 | set2 | set3)

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
print(maxSkills)
