__author__ = 'jekramer'
import csv
import sqlite3
from collections import namedtuple
import kivy

from kivy.app import App
from kivy.uix.label import Label

# class MyApp(App):
#
# def build(self):
#         return Label(text='Hello World')
#
# if __name__ == '__main__':
#     MyApp().run()


conn = sqlite3.connect('DRMax.db')
c = conn.cursor()

# Set your strain
strain = "Iron Slaves"
# Set your current classes
firstClass = "Printer"
secondClass = ""

Skills = namedtuple('Skills', 'Skill, Cost')

StrainSkills = list()
OpenSkills = list()
profs = {}
# Get Strain Skills
c.execute('SELECT Skill,Cost FROM "Strain Skill List" WHERE Strain=?', (strain,))
for sk in map(Skills._make, c.fetchall()):
    StrainSkills.append(sk)

# Fetch set of blocked skills
c.execute('SELECT Skill '
          'FROM "Strain Skill Restrictions" '
          'WHERE '
          'Strain = ? ', (strain, ))

blockedSkillsSQL = c.fetchall()

blockedSkills = {}
for bs in blockedSkillsSQL:
    blockedSkills[bs[0]] = 1

# Get Open Skills
c.execute('SELECT Skill,Cost FROM "Open Skill List"')
for ok in map(Skills._make, c.fetchall()):
    if ok.Skill not in blockedSkills:
        OpenSkills.append(ok)

# Fetch set of allowable professions
if firstClass != "":
    # We have a profession already (perhaps two)
    c.execute('SELECT p.Profession,p.Skill,p.Cost '
              'FROM "Profession Skill List" p '
              'WHERE '
              'NOT EXISTS ('
              'SELECT s.Profession FROM "Strain Profession Restrictions" s '
              'WHERE s.Strain = ? '
              'AND p.Profession = s.Profession '
              'AND s."First Only" = "FALSE")', (strain, ))
else:
    # No Profession? OK, apply the whole list of restrictions
    c.execute('SELECT p.Profession,p.Skill,p.Cost '
              'FROM "Profession Skill List" p '
              'WHERE '
              'NOT EXISTS ('
              'SELECT s.Profession FROM "Strain Profession Restrictions" s '
              'WHERE s.Strain = ? '
              'AND p.Profession = s.Profession)', (strain, ))

possibleProfsSQL = c.fetchall()

for pp in possibleProfsSQL:  # take all this data, and push it into a dictionary of sets of named tuples ("Skills")
    if pp[0] not in profs:
        profs[pp[0]] = set()
    test = profs[pp[0]]
    skTup = Skills(pp[1], pp[2])
    if skTup.Skill not in blockedSkills:
        test.add(skTup)
    profs[pp[0]] = test


disjointDict = {}

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
                disjointDict[firstClass + ", " + prof2 + ", " + prof3] = len(set1 | set2 | set3)
            elif firstClass != "" and secondClass != "":
                disjointDict[firstClass + ", " + secondClass + ", " + prof3] = len(set1 | set2 | set3)
            else:
                disjointDict[prof1 + ", " + prof2 + ", " + prof3] = len(set1 | set2 | set3)

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
