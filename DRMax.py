__author__ = 'jekramer'

import sqlite3
from collections import namedtuple
import kivy

from kivy.app import App
from kivy.uix.boxlayout

class DRMax(App):
    pass

if __name__ == '__main__':
    DRMax().run()


# Set your strain
strain = "Iron Slaves"
# Set your current classes
firstClass = "Printer"
secondClass = ""
strainSkills = list()
openSkills = list()
profs = {}

Skills = namedtuple('Skills', 'Skill, Cost')


# Fetch Professions List
def fetch_professions():
    conn = sqlite3.connect('DRMax.db')
    c = conn.cursor()
    professions_out = list()

    # Get Professions
    c.execute('SELECT Profession FROM "Profession Skill List"')
    professions_sql = c.fetchall()

    for profession_row in professions_sql:
        if professions_out.count(profession_row) == 0:
            professions_out.append(profession_row)

    conn.close()
    return professions_out


# Fetch Strain List
def fetch_strains():
    conn = sqlite3.connect('DRMax.db')
    c = conn.cursor()
    strains_out = list()

    # Get Professions
    c.execute('SELECT Strain FROM "Strain Skill List"')
    strains_sql = c.fetchall()

    for strain_row in strains_sql:
        if strains_out.count(strain_row) == 0:
            strains_out.append(strain_row)

    conn.close()
    return strains_out


# Pull down skills from the DB
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

    for pp in possible_profs_sql:
        # take all this data, and push it into a dictionary of sets of named tuples ("Skills")
        if pp[0] not in profs_out:
            profs_out[pp[0]] = set()
        test = profs_out[pp[0]]
        temp_skill_tuple = Skills(pp[1], pp[2])
        if temp_skill_tuple.Skill not in blocked_skills:
            test.add(temp_skill_tuple)
        profs_out[pp[0]] = test

    conn.close()
    return open_skills_out, strain_skills_out, profs_out


# Find the maximal intersecting skill set
def maximal_skill_set(open_skills_in, strain_skills_in, profs_in, first_class_in="", second_class_in="",
                      include_open=False, include_strain=True):
    disjoint_dict = {}
    open_set = set()
    strain_set = set()
    if include_open:
        for open_skill in open_skills_in:
            open_set.add(open_skill.Skill)

    if include_strain:
        for strain_skill in strain_skills_in:
            strain_set.add(strain_skill.Skill)

    set1 = set()
    set2 = set()
    set3 = set()
    for prof1 in profs_in:
        set1.clear()
        if first_class_in != "":
            prof1 = first_class_in
        for prof_skill in profs_in[prof1]:
            set1.add(prof_skill.Skill)

        for prof2 in profs_in:
            set2.clear()
            if second_class_in != "":
                prof2 = second_class_in
            for prof_skill in profs_in[prof2]:
                set2.add(prof_skill.Skill)

            for prof3 in profs_in:
                set3.clear()
                for prof_skill in profs_in[prof3]:
                    set3.add(prof_skill.Skill)
                disjoint_dict[prof1 + ", " + prof2 + ", " + prof3] = len(set1 | set2 | set3 | open_set | strain_set)

    max_key = max(disjoint_dict, key=disjoint_dict.get)
    max_value = disjoint_dict[max_key]
    # print(max_key)
    print(max_value)
    max_combos = list()
    for key, val in disjoint_dict.items():
        if val == max_value:
            max_combos.append(key)
    max_filtered_combos = remove_duplicate_triples(max_combos)
    max_combos.clear()
    for combo in max_filtered_combos:
        max_skills = list(profs_in[combo[0]] | profs_in[combo[1]] | profs_in[combo[2]])
        max_skills.sort()
        max_combos.append(max_skills)

    return max_filtered_combos, max_combos


# Remove duplicates in a triple string (very specific for the output of maximal skill set now)
def remove_duplicate_triples(triple_list_in):
    filtered_list_out = list()
    step_list = list()
    for entry in triple_list_in:
        inner_list = entry.split(", ")
        inner_list.sort()
        step_list.append(inner_list)

    for entry in step_list:
        if filtered_list_out.count(entry) == 0:
            filtered_list_out.append(entry)

    return filtered_list_out


openSkills, strainSkills, profs = fetch_skills(strain, firstClass)
maxComboNames, maxSkillsInCombo = maximal_skill_set(openSkills, strainSkills, profs, firstClass, secondClass)

for name, skillset in zip(maxComboNames, maxSkillsInCombo):
    print(name, skillset)