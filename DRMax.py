__author__ = 'jekramer'
import csv
profs = {}

with open('CharacterSkillsNoCost.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for name in reader.fieldnames:
        #FOR IRONS
        #if name != "Psionist":
        #FOR BAYWALKERS
        #if name != "Saw Bones" and name != "Primitive" and name != "Thug":
        #Restriction lists
            #if name != "Sniper":# and name != "Assassin" and name != "Hunter":# and name != "Spy" and name != "Thief" and name != "Scoundrel" and name != "Gambler":
            if name != "Tinker" and name != "Sniper":# and name != "Hook-up":
                profs[name] = set()
    for row in reader:
        for key in profs:
            test = profs[key]
            #FOR BAYWALKER
            #if row[key] != '' and row[key] != 'Analyze Creature' and row[key] != 'Double Tap' and row[key] != 'First Aide' and row[key] != 'Instruct' and row[key] != 'Literacy' and row[key] != 'Parry':
            #FOR IRONS
            #if row[key] != '' and row[key] != 'Disguise' and row[key] != 'Cover of Night' and row[key] != 'Vanish' and row[key] != 'Fade in a Crowd' and row[key] != 'Carry' and row[key] != 'Escape Bonds' and row[key] != 'Brawling' and row[key] != 'Iron Fists' and row[key] != 'Refuse' and row[key] != 'Rescue' and row[key] != 'Scrounge':
            #FOR NOA
            #if row[key] != '' and row[key] != 'Building Tomorrow' and row[key] != 'Challenge' and row[key] != 'Faith Healing' and row[key] != 'First Aide' and row[key] != 'Mind Resistance' and row[key] != 'Patch Job':
            #FOR PURE BLOOD
            if row[key] != '' and  row[key] != 'Backstab' and row[key] != 'Bolt Action' and row[key] != 'Charisma' and row[key] != 'Cheat' and row[key] != 'Check Value' and row[key] != 'Income' and row[key] != 'Literacy':
            #FOR REMENANTS
            #if row[key] != '':
            #FOR RETROGRADES
            #if row[key] != '' and row[key] != 'Barridcade' and row[key] != 'Cover of Night' and row[key] != 'Disguise' and row[key] != 'Escape Bonds' and row[key] != 'Feign Death' and row[key] != 'Melee Weapon Standard' and row[key] != 'Scrounge':
            #FOR ROVERS
            #if row[key] != '' and row[key] != 'Bartender Tongue' and row[key] != 'Check Your Sleeves' and row[key] != 'Head Shrink' and row[key] != 'Melee Weapon Small' and row[key] != 'Refuse' and row[key] != 'Scrounge':
                test.add(row[key])
            profs[key] = test

disjointDict = {}
#Set your current classes
firstClass = "Gambler"
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
