import Conditions


class Params(object):
    def __init__(self, conditions):
        self.params = {}
        self.conditions = conditions

        self.num_forecasts = 100
        self.cond_bits = 12
        self.cond_words = int((self.cond_bits + 15) / 16)
        self.min_count = 2
        self.individual = 1

        self.tau = 75
        self.lamb = .5
        self.max_bid = 10
        self.bit_prob = .1
        self.sub_range = 1

        self.a_min = .7
        self.a_max = 1.2
        self.a_range = self.a_max - self.a_min

        self.b_min = 0
        self.b_max = 0
        self.b_range = self.b_max - self.b_min

        self.c_min = -10
        self.c_max = 19
        self.c_range = self.c_max - self.c_min

        self.new_forecast_var = 4
        self.init_var = 4
        self.bit_cost = .005

        self.max_dev = 500
        self.pool_fraction = .2
        self.new_fraction = .2

        self.n_nulls = 4
        self.long_time = 4000

        # GA
        self.first_ga_time = 100
        self.ga_freq = 1000
        self.ga_prob = 1 / self.ga_freq

        self.n_pool = self.num_forecasts * self.pool_fraction
        self.n_new = self.num_forecasts * self.new_fraction

        self.n_pool_max = -1
        if self.n_pool > self.n_pool_max:
            self.n_pool_max = self.n_pool

        self.n_new_max = -1
        if self.n_new > self.n_new_max:
            self.n_new_max = self.n_new

        self.n_cond_max = -1
        if self.cond_words > self.n_cond_max:
            self.n_cond_max = self.cond_words

        self.end_list = -2
        self.all = -3
        self.set_prob = -4
        self.bad_input = -5
        self.not_found = -6
        self.eq = 0
        self.null_bit = -1

        if (1 + self.bit_cost * (self.cond_bits - self.n_nulls)) <= 0:
            print("The bitcost is too negative")

        self.special_bits = {"null" : self.null_bit, "end": self.end_list, ".": self.end_list, "all": self.all,
                             "allbits": self.all, "p": self.set_prob, "P": self.set_prob, "???": self.bad_input,
                             "Null": self.not_found}

        self.monitor_conditions = ["pr/d>1/4", "pr/d>1/2", "pr/d>3/4", "pr/d>7/8", "pr/d>1", "pr/d>9/8", "p>p5",
                                   "p>p20", "p>p100", "p>p500", "on", "off"]
        self.bit_list = [None for i in range(len(self.monitor_conditions))]
        self.__gen_bit_list__()
        self.prob_list = [self.bit_prob for i in range(self.cond_bits)]

    @property
    def __get_prob_list__(self):
        return self.prob_list

    @property
    def __get_bit_list__(self):
        return self.bit_list

    def __copy_prob_list__(self, new_list):
        self.prob_list.clear()
        for i in range(len(new_list)):
            self.prob_list[i] = new_list[i]

    def __copy_bit_list__(self, new_list):
        self.bit_list.clear()
        for i in range(len(new_list)):
            self.bit_list[i] = new_list[i]

    def __gen_bit_list__(self):
        for i, name in enumerate(self.monitor_conditions):
            self.bit_list[i] = self.conditions.__get_condition_id__(name)
            # print("Counter: ", i, "Name: ", name, "ID: ", self.bit_list[i])

    @property
    def __copy__(self):
        self.params["num_forecasts"] = self.num_forecasts
        self.params["cond_bits"] = self.cond_bits
        self.params["cond_words"] = self.cond_words
        self.params["min_count"] = self.min_count
        self.params["individual"] = self.individual

        self.params["tau"] = self.tau
        self.params["lamb"] = self.lamb
        self.params["max_bid"] = self.max_bid

        self.params["bit_prob"] = self.bit_prob
        self.params["sub_range"] = self.sub_range

        self.params["a_min"] = self.a_min
        self.params["a_max"] = self.a_max
        self.params["a_range"] = self.a_range

        self.params["b_min"] = self.b_min
        self.params["b_max"] = self.b_max
        self.params["b_range"] = self.b_range

        self.params["c_min"] = self.c_min
        self.params["c_max"] = self.c_max
        self.params["c_range"] = self.c_range

        self.params["new_forecast_var"] = self.new_forecast_var
        self.params["init_var"] = self.init_var
        self.params["bit_cost"] = self.bit_cost

        self.params["max_dev"] = self.max_dev
        self.params["pool_fraction"] = self.pool_fraction
        self.params["new_fraction"] = self.new_fraction
        self.params["n_nulls"] = self.n_nulls

        self.params["n_pool"] = self.n_pool
        self.params["n_new"] = self.n_new

        self.params["bit_list"] = self.bit_list
        self.params["prob_list"] = self.prob_list

        self.params["first_ga_time"] = self.first_ga_time
        self.params["ga_freq"] = self.ga_freq
        self.params["ga_prob"] = self.ga_prob

        self.params['long_time'] = self.long_time

        return self.params
