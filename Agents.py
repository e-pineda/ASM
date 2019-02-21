import random
import itertools
import Assets
import Conditions
import Forecast


class Agent(object):
    def __init__(self, id=None, name=None, agent_type=None, forecast_params=None, conditions=None,
                 price=None, dividend=None, int_rate=None, min_holding=None, init_cash=None, position=None, min_cash=None):
        self.id = id
        self.name = name
        self.agent_type = agent_type
        self.tolerance = .8

        self.demand = None
        self.profit = None
        self.wealth = None
        self.position = position
        self.cash = init_cash
        self.init_cash = init_cash
        self.min_holding = min_holding
        self.min_cash = min_cash
        self.int_rate = int_rate
        self.int_rate_ep = int_rate + 1
        self.price = price
        self.dividend = dividend

        # self.risk_preference =

        self.time = 0
        self.forecast_value = None
        self.lagged_forecast = None
        self.mean = None
        self.deviation = None
        self.variance = None
        self.median_strength = None
        self.pd_coefficient = None
        self.offset = None
        self.divisor = None
        self.ga_count = 0

        # Copy of conditions
        self.world_conditions = {}

        self.conditions_list = conditions
        self.format_world_conditions()

        # Copy of Forecast parameters
        self.forecast_params = forecast_params
        self.forecasting_rules = []
        self.active_rules = []
        self.old_active_rules = []
        self.strongest_rule = None
        self.__init_forecasts__()

        # Assets
        self.risky_assets = Assets.RiskyAssets()
        self.bonds = Assets.Bonds()

    # --------------------------
    @property
    def __get_strongest_rule__(self):
        return self.strongest_rule

    @property
    def __get_pos__(self):
        return self.position

    @property
    def __get_profit__(self):
        return self.profit

    @property
    def __get_name__(self):
        return self.name

    @property
    def __get_wealth__(self):
        return self.wealth

    @property
    def __get_cash__(self):
        return self.cash

    @property
    def __get_num_forecasts__(self):
        return len(self.forecasting_rules)

    @property
    def __get_median_strength__(self):
        return self.median_strength

    @property
    def __get_id__(self):
        return self.id

    @property
    def __get_rules__(self):
        return self.forecasting_rules

    @property
    def __get_mask__(self):
        return self.strongest_rule.__get_values__

    @property
    def __get_conditions__(self):
        return self.world_conditions

    @property
    def __get_time__(self):
        return self.time

    @property
    def __get_forecast__(self):
        return self.forecast

    @property
    def __get_demand__(self):
        return self.demand

    @property
    def __get_deviation__(self):
        return abs(self.deviation)

    @property
    def __get_bits__(self):
        return self.forecast_params['cond_bits']

    @property
    def __get_forecasts__(self):
        return self.forecasting_rules
    # --------------------------

    def __set_pos__(self, new_position):
        self.position = new_position

    def __set_int_rate__(self, new_rate):
        self.int_rate = new_rate
        self.int_rate_ep = self.int_rate + 1

    def __set_min_holding__(self, new_holding, new_cash):
        self.min_holding = new_holding
        self.min_cash = new_cash

    def __set_init_cash__(self, new_cash):
        self.initial_cash = new_cash

    def __set_holdings__(self):
        self.profit = 0
        self.wealth = 0
        self.cash = self.init_cash
        self.position = 0

    def __set_price__(self, new_price):
        self.price = new_price

    def __set_dividend__(self, new_div):
        self.dividend = new_div

    def __set_time__(self, time):
        self.time = time

    def __set_conditions__(self, conditions):
        self.conditions_list = conditions
        self.format_world_conditions()

    def __set_profit__(self, x):
        self.profit = x

    def __set_demand__(self, x):
        self.demand = x

    def __set_cash__(self, x):
        self.cash = x
    # --------------------------

    def give_risky_asset(self, asset):
        self.risky_assets.add_risky_asset(asset)

    def get_risky_asset_info(self):
        r_assets = iter(self.risky_assets)
        info = ''
        for asset in (r_assets):
            info += "Name: " + self.name + "\n"
            info += "Has: " + str(len(self.risky_assets)) + " asset(s)" + "\n"
            info += asset.__getinfo__()
        return info

    # --------------------------
    def __init_forecasts__(self):
        num_forecasts = self.forecast_params["num_forecasts"]

        self.median_strength = 0
        self.variance = self.forecast_params["init_var"]

        self.mean = self.price + self.dividend

        self.forecast_value = self.mean
        self.lagged_forecast = self.mean

        # Default rule with all 0's
        forecast = self.__gen_forecast__()
        self.forecasting_rules.append(forecast)
        self.strongest_rule = forecast

        for i in range(int(num_forecasts)):
            # print("\n---INIT FORECASTS---")
            forecast = self.__gen_forecast__()
            forecast = self.randomize_conditions(forecast)
            self.forecasting_rules.append(forecast)

    def __gen_forecast__(self):
        a_val = self.forecast_params["a_min"] + .5 * (1 - self.forecast_params["sub_range"]) * self.forecast_params[
            "a_range"]
        a_subrange = self.forecast_params["sub_range"] * self.forecast_params["a_range"]
        a_rand = a_val + random.uniform(0, 1) * a_subrange

        b_val = self.forecast_params["b_min"] + .5 * (1 - self.forecast_params["sub_range"]) * self.forecast_params[
            "b_range"]
        b_subrange = self.forecast_params["sub_range"] * self.forecast_params["b_range"]
        b_rand = b_val + random.uniform(0, 1) * b_subrange

        c_val = self.forecast_params["c_min"] + .5 * (1 - self.forecast_params["sub_range"]) * self.forecast_params[
            "c_range"]
        c_subrange = self.forecast_params["sub_range"] * self.forecast_params["c_range"]
        c_rand = c_val + random.uniform(0, 1) * c_subrange

        forecast_obj = Forecast.Forecast(self.forecast_params)

        forecast_obj.__set_forecast__(0)
        forecast_obj.__set_lagged_forecast__(self.mean)
        forecast_obj.__set_variance__(self.forecast_params['new_forecast_var'])
        forecast_obj.__set_real_variance__(self.forecast_params["new_forecast_var"])
        forecast_obj.__set_strength__(0)

        forecast_obj.__set_a__(a_rand)
        forecast_obj.__set_b__(b_rand)
        forecast_obj.__set_c__(c_rand)
        return forecast_obj

    def randomize_conditions(self, forecast_object):
        bit_list = self.forecast_params["bit_list"]
        prob_list = self.forecast_params["prob_list"]

        # print("---RANDOM FORECASTS---")
        # print("Prob List: ", prob_list)
        # print("Conditions: ", forecast_object.__get_conditions__)
        # print("Spec Factor: ", forecast_object.__get_spec_factor__)
        # print('------')

        for counter, id in enumerate(forecast_object.__get_conditions__):
            if id == 0 or id == 1:
                continue
            if bit_list[counter] < 0:
                forecast_object.__set_condition_val__(id, to_three='yeet')

            elif random.uniform(0, 1) < prob_list[counter]:
                # print("Case 2", counter)
                forecast_object.__set_condition_val__(id, random.randint(1, 2))
                forecast_object.increment_specificity()

        forecast_object.update_spec_factor()
        # print("Conditions: ", forecast_object.__get_conditions__, len(forecast_object.__get_conditions__))
        # print("Spec Factor: ", forecast_object.__get_spec_factor__)
        return forecast_object

    # --------------------------
    def credit_earnings_and_taxes(self):
        self.cash = (self.price * self.int_rate - self.dividend) * self.position
        if self.cash < self.min_cash:
            self.cash = self.min_cash

        self.wealth = self.cash + self.price * self.position

    def constrain_demand(self, slope, trial_price):
        # if trader wants to buy
        if self.demand > 0:
            if self.demand*trial_price > self.cash - self.min_cash:
                if self.cash - self.min_cash > 0:
                    self.demand = self.cash - self.min_cash / trial_price
                    slope = -self.demand / trial_price
                else:
                    self.demand = 0
                    slope = 0

        # if trader wants to sell
        elif self.demand < 0 and self.demand + self.position < self.min_holding:
            self.demand = self.min_holding - self.position
            slope = 0

        return slope, trial_price
    # --------------------------

    def format_world_conditions(self):
        try:
            index = 0
            for condition in self.conditions_list:
                if condition.__getstate__ == False:
                    val = 0
                else:
                    val = 1
                self.world_conditions[index] = val
                index += 1

        except AttributeError as e:
            print("LOOOK AT ME", e, self.conditions_list)
    # --------------------------

    # GIVE INFORMATION BEFORE AGENTS PREPARE
    def prepare_trading(self):
        forecast_var = 0
        max_strength = -1e50
        min_var = 1e50
        best_forecast = None
        n_active = False
        min_count = self.forecast_params['min_count']

        # activate GA if necessary
        if self.time >= self.forecast_params["first_ga_time"] and random.uniform(0,1) < self.forecast_params["ga_prob"]:
            self.activate_ga()

        self.lagged_forecast = self.forecast_value

        self.update_active_list()

        # Find the best forecast
        for forecast in self.active_rules:
            forecast.__set_last_active__(self.time)

            forecast.increment_count()
            if forecast.__get_count__ >= min_count:
                n_active = True

                if forecast.__get_real_variance__ < min_var:
                    min_var = forecast.__get_real_variance__
                    best_forecast = forecast

        # some forecasts are active
        if n_active:
            self.pd_coefficient = best_forecast.__get_a__
            self.offset = (best_forecast.__get_b__ * self.dividend) + best_forecast.__get_c__
            if self.forecast_params["individual"] == 1:
                forecast_var = best_forecast.__get_variance__
            else:
                forecast_var = self.variance
            best_forecast.__set_last_used__(self.time)

        # no forecasts are active
        else:
            count_sum, self.pd_coefficient, self.offset = 0, 0, 0
            min_count = self.forecast_params['min_count']

            for forecast in self.forecasting_rules:
                if forecast.__get_count__ >= min_count:
                    weight = forecast.__get_strength__
                    count_sum += weight
                    self.offset += (forecast.__get_b__ * self.dividend + forecast.__get_c__) * weight
                    self.pd_coefficient += forecast.__get_a__ * weight

                if count_sum > 0:
                    self.offset /= count_sum
                    self.pd_coefficient /= count_sum
                else:
                    self.offset = self.mean

                forecast_var = self.variance
            self.divisor = self.forecast_params["lamb"] * forecast_var

    def update_active_list(self):
        self.old_active_rules = self.active_rules
        self.active_rules.clear()

        # Move formerly active rules to old rules list and update their lagged forecast values
        for forecast in self.old_active_rules:
            forecast.__set_lagged_forecast__(forecast.__get_forecast__)

        for forecast in self.forecasting_rules:
            matches = 0
            forecast_conditions = forecast.__get_conditions__
            world_conditions = self.obtain_world_conditions(forecast_conditions)

            # print("-----------------TEST---------------------")
            # print(forecast_conditions)
            # print(world_conditions)

            for id, value in forecast_conditions.items():
                if value == 0:
                    # print("Base Case")
                    matches += 1
                    continue

                elif (value == 1 and world_conditions[id] == 0) or (value == 2 and world_conditions[id] == 1):
                    # print("MATCH", id, world_conditions[id])
                    matches += 1
                    continue

                else:
                    pass
                    # print("MISMATCH", id, world_conditions[id])

            if matches / len(forecast_conditions) >= self.tolerance:
                self.active_rules.append(forecast)
        # print("UPDATE TEST", len(self.active_rules))

    def obtain_world_conditions(self, forecast_conditions):
        keys_forecast = set(forecast_conditions)
        keys_world = set(self.world_conditions)
        intersection = keys_world & keys_forecast

        necessary_world_conditions = {key: self.world_conditions[key] for key in intersection}
        return necessary_world_conditions

    def calc_demand_slope(self, slope, trial_price):
        forecast = (trial_price + self.dividend) * self.pd_coefficient + self.offset

        if forecast >= 0:
            self.demand = -((trial_price * self.int_rate_ep - forecast) / self.divisor + self.position)
            slope = (self.pd_coefficient - self.int_rate_ep) / self.divisor
            # print("FORecast", forecast, self.demand, slope)
        else:
            forecast = 0
            self.demand = -(trial_price * self.int_rate_ep / self.divisor + self.position)
            slope = -self.int_rate_ep / self.divisor


        # LIMIT MAX BID
        if self.demand > self.forecast_params["max_bid"]:
            self.demand = self.forecast_params["max_bid"]
            slope = 0

        elif self.demand < -self.forecast_params["max_bid"]:
            self.demand = -self.forecast_params["max_bid"]
            slope = 0

        slope, trial_price = self.constrain_demand(slope, trial_price)
        return slope, trial_price

    def update_performance(self):
        tau = self.forecast_params['tau']
        a = 1 / tau
        b = 1 - a

        for forecast in self.active_rules:
            forecast.update_forecast(self.price, self.dividend)

        if tau == 100000:
            a = 0
            b = 0

        max_dev = self.forecast_params['max_dev']
        forecast_target = self.price + self.dividend

        self.deviation = forecast_target - self.lagged_forecast

        if abs(self.deviation) > max_dev:
            self.deviation = max_dev
        self.mean = b * self.mean + a * forecast_target

        if self.time < tau:
            self.variance = self.forecast_params['init_var']
        else:
            self.variance = b * self.variance + a*self.deviation*self.deviation

        if self.time > 0:
            for forecast in self.old_active_rules:
                last_forecast = forecast.__get_lagged_forecast__
                self.deviation = (forecast_target - last_forecast) * (forecast_target - last_forecast)

                if self.deviation > max_dev:
                    self.deviation = max_dev

                if forecast.__get_count__ > 0:
                    forecast.__set_real_variance__(b * forecast.__get_real_variance__ + a * self.deviation)
                else:
                    c = 1 / 1 + forecast.__get_count__
                    real_var = (1 - c) * forecast.__get_real_variance__ + c * self.deviation
                    forecast.__set_real_variance__(real_var)

    def bit_distribution(self):
        pass

    def f_moments(self):
        pass
    # --------------------------

    # GA

    # Add new rules and
    def activate_ga(self):
        print("ENTERED GA")
        self.ga_count += 1

        # Sort current rules based on their strength and find median strength
        sorted_rules, median_strength = self.sort_strengths()
        average_strength = self.average_strength()

        for i in range(20):
            parents = self.tournament_select(sorted_rules)
            new_rule = self.cross_over(parents, median_strength)
            finalized_rule = self.set_forecast_params(new_rule, median_strength, average_strength)
            sorted_rules.append(finalized_rule)

        sorted_rules = sorted(sorted_rules, key=lambda forecast: forecast.__get_strength__, reverse=True)

        final_rules = self.forecasting_rules[:1] + sorted_rules[:99]
        self.forecasting_rules.clear()
        self.forecasting_rules = final_rules

        # GENERALIZE THE RULES

    # 1. FUNCTION TO SORT RULES BASED ON THEIR REAL STRENGTH
    def sort_strengths(self):
        unsorted_rules = []
        for index, forecast in enumerate(self.forecasting_rules):
            # BIG ###############################################################
            if forecast.__get_count__ != 0:
                if forecast.__get_spec_factor__ is None:
                    forecast.update_spec_factor()
                strength = self.forecast_params['max_dev'] - forecast.__get_variance__ + forecast.__get_spec_factor__
                forecast.__set_variance__(forecast.__get_real_variance__)
                forecast.__set_strength__(strength)
                if index > 0:
                    unsorted_rules.append(forecast)

        sorted_rules = sorted(unsorted_rules, key=lambda forecast:forecast.__get_strength__)
        # print(len(sorted_rules))
        median_strength = sorted_rules[int(len(sorted_rules) / 2)].__get_strength__
        return sorted_rules, median_strength

    def average_strength(self):
        mean_variance = 0
        madv = 0
        a_ave, b_ave, c_ave, sum_c = 0, 0, 0, 0

        for forecast in self.forecasting_rules:
            variance = forecast.__get_variance__
            mean_variance += variance
            if forecast.__get_count__ > 0 and variance != 0: #########################BIG
                sum_c += 1 / variance
                a_ave += forecast.__get_a__ / variance
                b_ave += forecast.__get_b__ / variance
                c_ave += forecast.__get_c__ / variance

        mean_variance = mean_variance / self.forecast_params['num_forecasts']

        for forecast in self.forecasting_rules:
            madv += abs(forecast.__get_variance__ - mean_variance)

        average_strength = madv / self.forecast_params['num_forecasts']

        self.forecasting_rules[0].__set_a__(a_ave / sum_c)
        self.forecasting_rules[0].__set_a__(b_ave / sum_c)
        self.forecasting_rules[0].__set_a__(c_ave / sum_c)

        return average_strength

    def set_forecast_params(self, new_forecast, median_strength, average_strength):
        default_forecast = self.forecasting_rules[0]

        new_forecast.__set_real_variance__(self.forecast_params['max_dev'] - new_forecast.__get_strength__ + new_forecast.__get_spec_factor__)

        if new_forecast.__get_real_variance__ < default_forecast.__get_variance__ - average_strength:
            new_forecast.__set_real_variance__(default_forecast.__get_variance__ - average_strength)

            new_strength = self.forecast_params['max_dev'] - (default_forecast.__get_variance__ - average_strength) + new_forecast.__get_spec_factor__
            new_forecast.__set_strength__(new_strength)

        if new_forecast.__get_real_variance__ <= 0:
            new_forecast.__set_real_variance__(self.forecast_params['max_dev'] - median_strength + new_forecast.__get_spec_factor__)
            new_forecast.__set_strength__(median_strength)

        new_forecast.__set_variance__(new_forecast.__get_real_variance__)
        new_forecast.__set_last_active__(self.time)
        new_forecast.__set_count__(0)

        return new_forecast

    # 2. FUNCTION TO TOURNAMENT SELECT A PARENT FOR THE REMAINING 20%
    def tournament_select(self, sorted_rules):
        parents = random.sample(sorted_rules, 2)
        return parents

    def cross_over(self, parents, median_strength):
        parent_1 = parents[0]
        parent_2 = parents[1]

        # print("CROSSOVER")
        new_forecast = Forecast.Forecast(self.forecast_params)
        new_conditions = new_forecast.__get_conditions__

        # RANDOMIZE BITS
        for bit in new_conditions.keys():
            parent_choice = random.randint(1, 2)
            if parent_choice == 1:
                bit_id, bit_value = parent_1.__get_condition__(bit)
                new_forecast.__set_condition_val__(bit, new_value=bit_value)
            elif parent_choice == 2:
                bit_id, bit_value = parent_2.__get_condition__(bit)
                new_forecast.__set_condition_val__(bit, new_value=bit_value)

            if bit_value > 0:
                new_forecast.increment_specificity()

        # Combine forecast parameters
        if parent_1.__get_variance__ > 0 and parent_2.__get_variance__ > 0:
            weight_1 = (1.0 / parent_1.__get_variance__) / (1.0 / parent_1.__get_variance__  + 1.0 / parent_2.__get_variance__ )
        else:
            weight_1 = 0.5
        weight_2 = 1.0 - weight_1

        new_forecast.__set_a__(weight_1*parent_1.__get_a__ + weight_2*parent_2.__get_a__)
        new_forecast.__set_b__(weight_1*parent_1.__get_b__ + weight_2*parent_2.__get_b__)
        new_forecast.__set_c__(weight_1*parent_1.__get_c__ + weight_2*parent_2.__get_c__)

        new_forecast.__set_count__(max((parent_1.__get_count__, parent_2.__get_count__)))
        new_forecast.__set_last_active__((parent_1.__get_last_active__ + parent_2.__get_last_active__) / 2)

        new_forecast.update_spec_factor()

        if (((self.time - parent_1.__get_last_active__) > self.forecast_params['long_time']) or
                ((self.time - parent_2.__get_last_active__) > self.forecast_params['long_time']) or
                parent_1.__get_count__ * parent_2.__get_count__ == 0):
            new_forecast.__set_strength__(median_strength)
        else:
            new_strength = 0.5 * (parent_1.__get_strength__ + parent_2.__get_strength__)
            new_forecast.__set_strength__(new_strength)

        return new_forecast
