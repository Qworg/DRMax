__author__ = 'jekramer'

import sqlite3
from collections import namedtuple
import kivy
from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty


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
        if professions_out.count(profession_row[0]) == 0:
            professions_out.append(profession_row[0])

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
        if strains_out.count(strain_row[0]) == 0:
            strains_out.append(strain_row[0])

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
        max_skills = list()
        for a_profession in combo:
            for a_skill in profs_in[a_profession]:
                if [item[0] for item in max_skills].count(a_skill.Skill) == 0:
                    max_skills.append(a_skill)
                else:
                    # Already Exists!  Check costs
                    skill_index = [item[0] for item in max_skills].index(a_skill.Skill)
                    inserted_skill = max_skills.pop(skill_index)
                    if inserted_skill.Cost >= a_skill.Cost:
                        max_skills.append(a_skill)
                    else:
                        max_skills.append(inserted_skill)

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

class SelectionForm(BoxLayout):
    output_text_prop = StringProperty()
    open_skill_list_button_text = StringProperty()
    open_skill_list_on = BooleanProperty()


    def __init__(self, **kwargs):
        super(SelectionForm, self).__init__(**kwargs)
        self.output_text_prop = "Please be sure to select a strain first"
        self.open_skill_list_button_text = "Open Skill List Off"
        self.open_skill_list_on = False
        self.ids.solve_button.bind(on_press=self.solve_character)
        self.ids.open_skill_list_button.bind(on_press=self.open_skill_list_toggle)

    def solve_character(self, btn_pressed):
        print("Solving!")
        strain_skills = list()
        open_skills = list()
        profs = {}
        strain = self.ids.sspinner.getStrain()
        first_class = self.ids.pspinner1.getProfession()
        second_class = self.ids.pspinner2.getProfession()
        # print(self.ids.pspinner3.getProfession())
        open_skills, strain_skills, profs = fetch_skills(strain, first_class)
        max_combo_names, max_skills_in_combo = maximal_skill_set(open_skills, strain_skills, profs, first_class,
                                                                 second_class, self.open_skill_list_on)

        output_string = ""
        for name, skill_set in zip(max_combo_names, max_skills_in_combo):
            output_string = output_string + ', '.join(name) + '\n'
            for skill in skill_set:
                output_string = output_string + skill.Skill + ': ' + skill.Cost + '\n'
            output_string = output_string + '\n\n'

        self.output_text_prop = output_string
        return True

    def open_skill_list_toggle(self, btn_pressed):
        print("Toggle Open Skill List!")
        if self.open_skill_list_on:
            self.open_skill_list_on = False
            self.open_skill_list_button_text = "Open Skill List Off"
        else:
            self.open_skill_list_on = True
            self.open_skill_list_button_text = "Open Skill List On"
        return True

class StrainSpinner(Spinner):
    strain_list = ListProperty()
    strain_list = fetch_strains()
    strain_text = StringProperty()
    strain_text = "Select Strain"
    def __init__(self, **kwargs):
        super(StrainSpinner, self).__init__(**kwargs)
        self.bind(text=self.get_selected_value)

    def get_selected_value(self, object_out, *args):
        self.strain_text = args[0]
        return True

    def getStrain(self):
        if self.strain_text == "Select Strain":
            return ""
        else:
            return self.strain_text


class ProfessionSpinner(Spinner):
    professions_list = ListProperty()
    professions_list = fetch_professions()
    professions_text = StringProperty()
    professions_text = "Select Profession"
    def __init__(self, **kwargs):
        super(ProfessionSpinner, self).__init__(**kwargs)
        self.bind(text=self.get_selected_value)

    def get_selected_value(self, object_out, *args):
        self.professions_text = args[0]
        return True

    def getProfession(self):
        if self.professions_text == "Select Profession":
            return ""
        else:
            return self.professions_text


class DRMax(App):
    def build(self):
        return SelectionForm()

if __name__ == '__main__':
    DRMax().run()
