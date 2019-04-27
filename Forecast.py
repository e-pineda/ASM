import random


class Forecast(object):
    def __init__(self, forecast_params, id):
        self.id = id
        self.forecast_params = forecast_params
        self.condition_list = self.forecast_params["bit_list"]
        self.max_bits = 80

        self.__init_monitor__()

        self.shift = [None for i in range(self.max_bits)]
        self.mask = [None for i in range(self.max_bits)]
        self.n_mask = [None for i in range(self.max_bits)]
        self.__init_mask__()

        self.forecast = 0
        self.lagged_forecast = None
        self.variance = 999999999
        self.real_variance = self.forecast_params["new_forecast_var"]
        self.strength = None

        self.a = None
        self.b = None
        self.c = None

        self.spec_factor = None
        self.bit_cost = self.forecast_params["bit_cost"]
        self.last_active = 1
        self.last_used = 1
        self.specificity = 0
        self.count = 0

        self.cond_words = self.forecast_params["cond_words"]
        self.cond_bits = self.forecast_params["cond_bits"]
        self.n_nulls = self.forecast_params["n_nulls"]
        
    # ----------------------
    def __init_monitor__(self):
        self.conditions = {condition: 0 for condition in self.condition_list}
        # print("INIT MONITOR LIST: ", self.conditions)

    def __init_mask__(self):
        for bit in range(self.max_bits):
            self.shift[bit] = (bit % 16) * 2
            self.mask[bit] = 3 << self.shift[bit]
            self.n_mask[bit] = ~self.mask[bit]

    # ----------------------
    def __set_cond_words__(self, new_val):
        self.cond_words = new_val

    def __set_cond_bits__(self, new_val):
        self.cond_bits = new_val

    def __set_conditions__(self, new_conditions):
        self.conditions = new_conditions

    def __set_condition_id__(self, id, value):
        self.conditions[value] = self.conditions[id]
        del self.conditions[id]

    def __set_condition_val__(self, id, new_value=None, to_three=None):
        if to_three is not None:
            self.conditions[id] = 3
        elif new_value is not None:
            self.conditions[id] = new_value
        else:
            self.conditions[id] = random.randint(1, 2)

    @property
    def __get_conditions__(self):
        return self.conditions

    def __get_condition__(self, id):
        # print("CONDITION LIST: ", self.conditions)
        for condition in self.conditions:
            if condition == id:
                # print("CONDITION: ",condition, self.conditions.get(id))
                return condition, self.conditions.get(id)

    def __get_condition_by_pos__(self, pos):
        for counter, condition in enumerate(self.conditions):
            # print("COUNTER: ", counter, condition, self.conditions.get(condition))
            if counter == pos:
                # print("FINAL COUNTER: ", counter, condition, self.conditions.get(condition))
                return condition, self.conditions.get(condition)

    @property
    def __get_values__(self):
        return self.shift, len(self.shift)

    # ----------------------
    def switch_bits(self, id):
        if self.conditions[id] == 1:
            self.conditions[id] = 2
        else:
            self.conditions[id] = 1

    def mask_bit(self, id):
        self.conditions[id] &= self.n_mask[id]


    ############################################################################
    def __set_n_nulls__(self, x):
        self.n_nulls = x

    def __set_bit_cost__(self, x):
        self.bit_cost = x

    def __set_a__(self, x):
        self.a = x

    def __set_b__(self, x):
        self.b = x

    def __set_c__(self, x):
        self.c = x

    def __set_spec_factor__(self, x):
        self.spec_factor = x

    def __set_specificity__(self, x):
        self.specificity = x

    def __set_variance__(self, x):
        self.variance = x

    def __set_real_variance__(self, x):
        self.real_variance = x

    def __set_last_active__(self, x):
        self.last_active = x

    def __set_last_used__(self, x):
        self.last_used = x

    def __set_count__(self, x):
        self.count = x

    def __set_strength__(self, x):
        self.strength = x

    def __set_lagged_forecast__(self, x):
        self.lagged_forecast = x

    def __set_forecast__(self, x):
        self.forecast = x

    @property
    def __get_a__(self):
        return self.a

    @property
    def __get_b__(self):
        return self.b

    @property
    def __get_c__(self):
        return self.c

    @property
    def __get_spec_factor__(self):
        return self.spec_factor

    @property
    def __get_specificity__(self):
        return self.specificity

    @property
    def __get_variance__(self):
        return self.variance

    @property
    def __get_real_variance__(self):
        return self.real_variance

    @property
    def __get_last_active__(self):
        return self.last_active

    @property
    def __get_last_used__(self):
        return self.last_used

    @property
    def __get_count__(self):
        return self.count

    @property
    def __get_strength__(self):
        return self.strength

    @property
    def __get_lagged_forecast__(self):
        return self.lagged_forecast

    @property
    def __get_forecast__(self):
        return self.forecast

    @property
    def __get_id__(self):
        return self.id

    def increment_specificity(self):
        self.specificity += 1

    def decrement_specificity(self):
        self.specificity -= 1

    def increment_count(self):
        self.count += 1

    def update_spec_factor(self):
        self.spec_factor = (self.cond_bits - self.specificity) * self.bit_cost

    def update_forecast(self, price, dividend):
        self.lagged_forecast = self.forecast
        self.forecast = self.a * (price+dividend) + self.b * dividend + self.c
        return self.forecast
