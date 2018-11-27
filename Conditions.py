import NumericStringParser


class Condition(object):
    def __init__(self, cond_id, name, description, status=False):
        self.id = cond_id
        self.name = name
        self.description = description
        self.status = status

    def __set_name__(self, new_name):
        self.name = new_name

    def __set_description__(self, new_desc):
        self.description = new_desc

    def __setstate__(self, state):
        self.status = state

    @property
    def __getstate__(self):
        return self.status

    @property
    def __get__(self):
        return self.id, self.name, self.description, self.status

    @property
    def __get_id__(self):
        return self.id

    @property
    def __get_name__(self):
        return self.name

    @property
    def __get_desc__(self):
        return self.description

    def __print__(self):
        print(self.id, self.name, self.description, self.status)

    def __verify__(self, condition_name):

        if "up" in condition_name:
            result = self._get_up_variable_(condition_name)

        #evaulate a math formula
        else:
            result = self.eval_formula(condition_name)

    def _get_up_variable_(self, up_formula):
        variable = ''
        check_pos = up_formula.find('up')

        if up_formula[:check_pos].isdigit() or up_formula[:check_pos] in'dp':
            variable = up_formula[:check_pos]

        else:
            variable = up_formula[check_pos:]
        print(variable)

        return 1

    def eval_formula(self, formula):
        nsp = NumericStringParser.NumericStringParser()

        result = nsp.eval(formula)

        return result


class ConditionList(object):

    def __init__(self):
        self.conditions = []
        self.curr_cond = 0

    def __add__(self, other):
        self.conditions.append(other)

    def __remove__(self, id):
        del self.condition[id]

    def __iter__(self):
        return self

    def __next__(self):
        if self.curr_cond >= len(self.conditions):
            raise StopIteration
        else:
            self.curr_cond += 1
            return self.conditions[self.curr_cond - 1]

    def __getitem__(self, item):
        return self.conditions[item]
