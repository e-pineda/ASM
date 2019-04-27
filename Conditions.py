class Condition(object):
    def __init__(self, cond_id, name, description, status=False, is_monitored=False):
        self.id = cond_id
        self.name = name
        self.description = description
        self.status = status
        self.is_monitored = is_monitored

    def __set_name__(self, new_name):
        self.name = new_name

    def __set_description__(self, new_desc):
        self.description = new_desc

    def __setstate__(self, state):
        self.status = state

    def __set_monitor__(self, abool):
        self.is_monitored = abool

    @property
    def __getstate__(self):
        return self.status

    @property
    def __get__(self):
        return self.id, self.description, self.status

    @property
    def __get_id__(self):
        return self.id

    @property
    def __get_name__(self):
        return self.name

    @property
    def __get_desc__(self):
        return self.description

    @property
    def __get_monitor__(self):
        return self.monitor

    def __print__(self):
        print(self.id, self.name, self.description, self.status)


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
            self.curr_cond = 0
            raise StopIteration
        else:
            self.curr_cond += 1
            return self.conditions[self.curr_cond - 1]

    def __getitem__(self, item):
        return self.conditions[item]

    def __get_condition_name__(self, name):
        for condition in self.conditions:
            if condition.__get_name__ == name:
                return condition.__get_id__
