import Forecast
import random


class Agent(object):
    def __init__(self, id=None, name=None, agent_type=None, forecast_params=None, conditions=None,
                 price=None, dividend=None, int_rate=None, min_holding=None, init_cash=None, position=None,
                 min_cash=None, risk_aversion=None, tolerance=None, mistake_threshold=None, make_mistakes=None):
        self.id = id
        self.name = name
        self.agent_type = agent_type
        self.tolerance = tolerance

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
        self.max_risk_aversion = risk_aversion
        self.curr_risk_aversion = None

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
        self.last_rule_id = 101

        self.made_mistake = False
        self.learned = False

        # History for agents
        self.history = {'Cash': [], "Position": [], "Wealth": [], "Profit": []}

        #MISTAKE THRESHOLD
        self.make_mistakes = make_mistakes
        self.mistake_threshold = mistake_threshold

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

        self.bankruptcy_flag = False

    # -------------------------
    @property
    def __get_basic_info__(self):
        return self.name, self.wealth, self.cash, self.position, self.profit

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

    @property
    def __get_curr_risk_aversion__(self):
        return self.curr_risk_aversion

    @property
    def __get_history__(self):
        return self.history

    @property
    def __get_price__(self):
        return self.price

    @property
    def __get_dividend__(self):
        return self.dividend

    @property
    def __get_mistake_made__(self):
        return self.made_mistake

    @property
    def __get_learned__(self):
        return self.learned

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

    def bankrupt(self):
        self.wealth = 0
        self.cash = self.init_cash / 2
        self.position = self.min_holding

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
        forecast = self.__gen_forecast__(0)
        self.forecasting_rules.append(forecast)
        self.strongest_rule = forecast

        for i in range(int(num_forecasts)):
            forecast = self.__gen_forecast__(i+1)
            forecast = self.randomize_conditions(forecast)
            self.forecasting_rules.append(forecast)

    def __gen_bit_list__(self):
        bit_list = [0, 1]
        condition_ids = random.sample(range(2, 60), 10)
        for id in condition_ids:
            bit_list.append(id)
        return bit_list

    def __gen_forecast__(self, id):
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

        self.forecast_params['bit_list'] = self.__gen_bit_list__()
        forecast_obj = Forecast.Forecast(self.forecast_params, id)

        forecast_obj.__set_forecast__(0)
        forecast_obj.__set_lagged_forecast__(self.mean)
        forecast_obj.__set_variance__(self.forecast_params['init_var'])
        forecast_obj.__set_real_variance__(self.forecast_params["init_var"])
        forecast_obj.__set_strength__(0)

        forecast_obj.__set_a__(a_rand)
        forecast_obj.__set_b__(b_rand)
        forecast_obj.__set_c__(c_rand)
        return forecast_obj

    def randomize_conditions(self, forecast_object):
        bit_list = self.forecast_params["bit_list"]
        prob_list = self.forecast_params["prob_list"]

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
        return forecast_object

    # --------------------------
    def credit_earnings_and_taxes(self):
        self.cash = (self.price * self.int_rate - self.dividend) * self.position

        if self.cash < self.min_cash:
            self.cash = self.min_cash
        # print('ID: ', self.id, 'Cash: ', self.cash, self.min_cash)
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
            # print("AGENT ", self.id, " WANTS TO SELL with DEMAND ", self.demand)
        return slope
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
        min_var = 1e50
        best_forecast = None
        n_active = False
        min_count = self.forecast_params['min_count']

        self.made_mistake = False
        self.learned = False

        # activate GA if necessary
        if self.time >= self.forecast_params["first_ga_time"] and random.uniform(0,1) < self.forecast_params["ga_prob"]:
            self.activate_ga()

        self.lagged_forecast = self.forecast_value

        self.update_active_list()

        # Find the best forecast
        for counter, forecast in enumerate(self.active_rules):
            skip_factor = random.uniform(0, 1)
            mistake_factor = random.uniform(0, 1)
            forecast.__set_last_active__(self.time)

            forecast.increment_count()
            if forecast.__get_count__ >= min_count:
                n_active = True

                if self.make_mistakes:
                    if mistake_factor < self.mistake_threshold:
                        # print("MISTAKE HIT w/ FACTORS: ", mistake_factor)
                        min_var = forecast.__get_real_variance__
                        best_forecast = forecast
                        self.made_mistake = True
                        break

                    if forecast.__get_real_variance__ < min_var:
                        if skip_factor < self.mistake_threshold:
                            # print("SKIP HIT w/ FACTORS: ", skip_factor, mistake_factor)
                            self.made_mistake = True
                            continue
                        min_var = forecast.__get_real_variance__
                        best_forecast = forecast
                else:
                    min_var = forecast.__get_real_variance__
                    best_forecast = forecast

        # some forecasts are active
        if n_active:
            self.pd_coefficient = best_forecast.__get_a__
            self.offset = (best_forecast.__get_b__ * self.dividend) + best_forecast.__get_c__
            forecast_var = best_forecast.__get_variance__
            # print("BEST FORECAST TEST with AGENT", self.id, "BEST FORECAST ID: ", best_forecast.__get_id__, "USED ",
            #       best_forecast.__get_last_used__)
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

        # self.divisor = self.forecast_params["lamb"] * forecast_var
        self.calculate_risk_aversion()
        self.divisor = self.curr_risk_aversion * forecast_var

    def calculate_risk_aversion(self):
        if -1.6 <= self.position <= 1.6:
            risk_factor = random.uniform(0, .3)
            self.curr_risk_aversion = self.max_risk_aversion - risk_factor
            # if self.id == 0:
            #     print("CASE 1: ", self.position,self.curr_risk_aversion)

        elif -3.2 <= self.position < -1.6 or 1.6 < self.position <= 3.2:
            risk_factor = random.uniform(0, .15)
            self.curr_risk_aversion = self.max_risk_aversion - risk_factor
            # if self.id == 0:
                # print("CASE 2: ", self.position, self.curr_risk_aversion)

        elif 3.2 < self.position < -3.2:
            self.curr_risk_aversion = self.max_risk_aversion
            # if self.id == 0:
            #     print("CASE 3: ", self.position,self.curr_risk_aversion)

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
        # print("UPDATE TEST with Agent ID", self.id, len(self.active_rules))

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
            self.demand = self.forecast_params["max_bid"] * .8
            slope = 0

        elif self.demand < -self.forecast_params["max_bid"]:
            self.demand = -self.forecast_params["max_bid"] * .8
            slope = 0

        slope = self.constrain_demand(slope, trial_price)
        # CONSTRAIN FORECAST, WHICH IS THE AGENT'S PRICE, HERE
        forecast = self.constrain_forecast(forecast)
        return slope, forecast

    def constrain_forecast(self, forecast_price):
        # print("AGENT ID: ", self.id, '; CASH: ', self.cash, "; HOLDINGS: ", self.position, "; DEMAND: ", self.demand, "; FORECAST: ", forecast_price)
        if self.demand > 0:
            cash_to_bankruptcy = self.cash - self.min_cash
            if forecast_price > cash_to_bankruptcy:
                forecast_price = cash_to_bankruptcy * .8

        if self.demand < 0:
            pass
        return forecast_price

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

    def record_history(self):
        self.history.get('Cash').append(self.cash)
        self.history.get('Position').append(self.position)
        self.history.get('Wealth').append(self.wealth)
        self.history.get('Profit').append(self.profit)

    # GA
    # Add new rules and
    def activate_ga(self):
        # print("ENTERED GA")
        self.ga_count += 1
        self.learned = True

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
            if forecast.__get_count__ == 0:
                continue

            elif forecast.__get_count__ != 0:
                if forecast.__get_spec_factor__ is None:
                    forecast.update_spec_factor()
                strength = self.forecast_params['max_dev'] - forecast.__get_variance__ + forecast.__get_spec_factor__
                forecast.__set_variance__(forecast.__get_real_variance__)
                forecast.__set_strength__(strength)
                if index > 0:
                    unsorted_rules.append(forecast)

        sorted_rules = sorted(unsorted_rules, key=lambda forecast:forecast.__get_strength__)
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

        new_forecast = Forecast.Forecast(self.forecast_params, self.last_rule_id)
        self.last_rule_id += 1
        new_conditions = {}

        # print("PARENT 1: ", parent_1.__get_count__)
        # print("PARENT 2: ", parent_2.__get_count__)

        # RANDOMIZE BITS
        for counter in range(12):
            parent_choice = random.randint(1, 2)
            if parent_choice == 1:
                bit_id, bit_value = parent_1.__get_condition_by_pos__(counter)
                if bit_id in new_conditions:
                    bit_id, bit_value = parent_2.__get_condition_by_pos__(counter)

            elif parent_choice == 2:
                bit_id, bit_value = parent_2.__get_condition_by_pos__(counter)
                if bit_id in new_conditions:
                    bit_id, bit_value = parent_1.__get_condition_by_pos__(counter)

            if bit_id in new_conditions:
                parent_set = list(set(list(parent_1.__get_conditions__.keys()) + list(parent_2.__get_conditions__.keys())))
                conditions = [i for i in range(2, 61)]
                available = [i for i in conditions if i not in parent_set]
                # print("PARENT: ", parent_set, available)
                bit_id = random.choice(available)
                bit_value = random.randint(0, 2)
                # print("HIT", bit_id, bit_value)
            new_conditions[bit_id] = bit_value

            if bit_value > 0:
                new_forecast.increment_specificity()

        new_forecast.__set_conditions__(new_conditions)
        # wait = input("WAIT: ")
        # print("------------------")
        
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
