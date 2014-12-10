__author__ = 'jekramer'

import sqlite3
from collections import namedtuple
import kivy

from kivy.app import App
from kivy.uix.label import Label

# class MyApp(App):
#
# def build(self):
# return Label(text='Hello World')
#
# if __name__ == '__main__':
# MyApp().run()


# Set your strain
strain = "Iron Slaves"
# Set your current classes
firstClass = "Printer"
secondClass = ""
strainSkills = list()
openSkills = list()
profs = {}

Skills = namedtuple('Skills', 'Skill, Cost')


def fetch_skills(strain_in, first_class_in=""):
    conn = sqlite3.connect('DRMax.db')
    c = conn.cursor()
    strain_skills_out = list()
    open_skills_out = list()
    blocked_skills = {}
    profs_out = {}

    # Get Strain Skills
    c.execute('SELECT Skill,Cost FROM "Strain Skill List" WHERE Strain=?', (strain_in,))
    for sk in map(Skills._make, c.fetchall()):
        strain_skills_out.append(sk)

    # Fetch set of blocked skills
    c.execute('SELECT Skill '
              'FROM "Strain Skill Restrictions" '
              'WHERE '
              'Strain = ? ', (strain_in, ))

    blocked_skills_sql = c.fetchall()

    for bs in blocked_skills_sql:
        blocked_skills[bs[0]] = 1

    # Get Open Skills
    c.execute('SELECT Skill,Cost FROM "Open Skill List"')
    for ok in map(Skills._make, c.fetchall()):
        if ok.Skill not in blocked_skills:
            open_skills_out.append(ok)

    # Fetch set of allowable professions
    if first_class_in != "":
        # We have a profession already (perhaps two)
        c.execute('SELECT p.Profession,p.Skill,p.Cost '
                  'FROM "Profession Skill List" p '
                  'WHERE '
                  'NOT EXISTS ('
                  'SELECT s.Profession FROM "Strain Profession Restrictions" s '
                  'WHERE s.Strain = ? '
                  'AND p.Profession = s.Profession '
                  'AND s."First Only" = "FALSE")', (strain_in, ))
    else:
        # No Profession? OK, apply the whole list of restrictions
        c.execute('SELECT p.Profession,p.Skill,p.Cost '
                  'FROM "Profession Skill List" p '
                  'WHERE '
                  'NOT EXISTS ('
                  'SELECT s.Profession FROM "Strain Profession Restrictions" s '
                  'WHERE s.Strain = ? '
                  'AND p.Profession = s.Profession)', (strain_in, ))

    possible_profs_sql = c.fetchall()

    for pp in possible_profs_sql:  # take all this data, and push it into a dictionary of sets of named tuples ("Skills")
        if pp[0] not in profs_out:
            profs_out[pp[0]] = set()
        test = profs_out[pp[0]]
        temp_skill_tuple = Skills(pp[1], pp[2])
        if temp_skill_tuple.Skill not in blocked_skills:
            test.add(temp_skill_tuple)
        profs_out[pp[0]] = test

    conn.close()
    return open_skills_out, strain_skills_out, profs_out


def maximal_skill_set(open_skills_in, strain_skills_in, profs_in):
    disjoint_dict = {}

    for prof1 in profs_in:
        if firstClass != "":
            set1 = profs_in[firstClass]
        else:
            set1 = profs_in[prof1]
        for prof2 in profs_in:
            if secondClass != "":
                set2 = profs_in[secondClass]
            else:
                set2 = profs_in[prof2]
            for prof3 in profs_in:
                set3 = profs_in[prof3]
                if firstClass != "" and secondClass == "":
                    disjoint_dict[firstClass + ", " + prof2 + ", " + prof3] = len(set1 | set2 | set3)
                elif firstClass != "" and secondClass != "":
                    disjoint_dict[firstClass + ", " + secondClass + ", " + prof3] = len(set1 | set2 | set3)
                else:
                    disjoint_dict[prof1 + ", " + prof2 + ", " + prof3] = len(set1 | set2 | set3)

    max_key = max(disjoint_dict, key=disjoint_dict.get)
    max_value = disjoint_dict[max_key]
    # print(max_key)
    print(max_value)
    for key, val in disjoint_dict.items():
        if val == max_value:
            print(key)
    max_list = max_key.split(", ")
    max_skills = list(profs_in[max_list[0]] | profs_in[max_list[1]] | profs_in[max_list[2]])
    max_skills.sort()
    print(max_skills)


openSkills, strainSkills, profs_in = fetch_skills(strain, firstClass)
maximal_skill_set(openSkills, strainSkills, profs)






