import numpy as np

def load_recipe_list(fn):
    dtype=[('OBJNAME', 'S128'), ('OBJTYPE', 'S128'), ('GROUP1', 'i'), ('GROUP2', 'i'), ('EXPTIME', 'f'), ('RECIPE', 'S128'), ('OBSIDS', 'S1024'),  ('FRAMETYPES', 'S1024')]
    d = np.genfromtxt(fn, delimiter=",", names=True, comments="#",
                      dtype=dtype)
    recipe_list = []
    for row in d:
        recipe_name = row["RECIPE"].strip()
        obsids  = map(int, row["OBSIDS"].strip().split())
        frametypes  = row["FRAMETYPES"].strip().split()
        recipe_list.append((recipe_name, obsids, frametypes, row))

    return recipe_list

def make_recipe_dict(recipe_list):
    recipe_dict = {}
    for recipe_name, obsids, frametypes, row in recipe_list:
        recipe_dict.setdefault(recipe_name, []).append((obsids, frametypes, row))
    return recipe_dict

def get_multi_fnmatch_pattern(fnmatch_list):

    import re, fnmatch
    p_list = []
    for fnmatch1 in fnmatch_list:
        p = re.compile(fnmatch.translate(fnmatch1))
        p_list.append(p)

    def p_match(s, p_list=p_list):
        for p in p_list:
            if p.match(s): return True
        return False

    return p_match


class Recipes(object):
    def __init__(self, fn):
        self._fn = fn
        self.recipe_list = load_recipe_list(fn)
        self.recipe_dict = make_recipe_dict(self.recipe_list)

    def select_multi(self, recipe_names, starting_obsids=None):
        selected = []
        for recipe_name in recipe_names:
            _ = self.select_fnmatch(recipe_name, starting_obsids)
            selected.extend(_)

    def select(self, recipe_name, starting_obsids=None):
        if recipe_name == "ALL_RECIPES":
            recipes_selected = []
            for v in self.recipe_dict.values():
                recipes_selected.extend(v)
        elif recipe_name not in self.recipe_dict:
            return []
        else:
            recipes_selected = self.recipe_dict[recipe_name]

        if starting_obsids is None:
            return recipes_selected # self.recipe_dict[recipe_name]

        selected = []
        selected_obsids = []
        for _ in recipes_selected:
            obsids = _[0]
            if obsids[0] in starting_obsids:
                selected.append(_)
                selected_obsids.append(obsids[0])

        if len(selected_obsids) != len(starting_obsids):
            remained_obsids = set(starting_obsids) - set(selected_obsids)
            raise RuntimeError("some obsids is not correct : %s" % \
                               ", ".join(sorted(remained_obsids)))
        else:
            return selected

    def select_fnmatch(self, recipe_fnmatch, starting_obsids=None):

        if isinstance(recipe_fnmatch, str):
            recipe_fnmatch_list = [recipe_fnmatch]
        else:
            recipe_fnmatch_list = recipe_fnmatch

        p_match = get_multi_fnmatch_pattern(recipe_fnmatch_list)

        dict_by_1st_obsid = dict((recipe_item[1][0], recipe_item) \
                                 for recipe_item in self.recipe_list \
                                 if p_match(recipe_item[0]))

        if starting_obsids is None:
            starting_obsids = sorted(dict_by_1st_obsid.keys())

        selected = [dict_by_1st_obsid[s1] for s1 in starting_obsids]

        return selected
