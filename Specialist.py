import numpy


class MarketClearer(object):
    def __init__(self):
        self.max_price = None
        self.min_price = None
        self.eta = None
        self.min_excess = None
        self.rea = None
        self.reb = None
        self.bid_fraction = None
        self.offer_fraction = None
        self.max_iterations = None
        self.volume = None
        self.taup_decay = None
        self.taup_new = None
        self.sp_type = None
        self.types = ["sp_re", "sp_slope", "sp_eta"]
        self.demand_coefficient = 1
        self.int_rate = .1
        self.world_price = None
        self.world_dividend = None
        self.profit_per_unit = None
        self.agents = None

    def __set_max_price__(self, x):
        self.max_price = x

    def __set_min_price__(self, x):
        self.min_price = x

    def __set_taup__(self, x):
        self.taup_new = -numpy.expm1(-1.0 / x)
        self.taup_decay = 1.0 - self.taup_new

    def __set_sp_type__(self, x):
        if x != 0 or x != 1 or x != 2:
            x = 1
        self.sp_type = x

    def __set_max_iterations__(self, x):
        self.max_iterations = x

    def __set_min_excess__(self, x):
        self.min_excess = x

    def __set_eta__(self, x):
        self.eta = x

    def __set_rea__(self, x):
        self.rea = x

    def __set_reb__(self, x):
        self.trial_price = x

    def __set_world_price__(self, x):
        self.world_price = x

    def __set_world_dividend__(self, x):
        self.world_dividend = x

    def __set_profit_per_unit__(self, x):
        self.profit_per_unit = x

    def __set_agents__(self, x):
        self.agents = x

    def __set_vals__(self, max_price=None, min_price=None, taup=None, sp_type=None,max_iterations=None,
                     min_excess=None, eta=None, rea=None, reb=None, agents=None):
        self.__set_max_price__(max_price)
        self.__set_min_price__(min_price)
        self.__set_taup__(taup)
        self.__set_sp_type__(sp_type)
        self.__set_max_iterations__(max_iterations)
        self.__set_min_excess__(min_excess)
        self.__set_eta__(eta)
        self.__set_rea__(rea)
        self.__set_reb__(reb)
        self.__set_agents__(agents)

    @property
    def __get_volume__(self):
        return self.volume

    def perform_trades(self):
        # done = False
        # slope, imbalance = 0, 0
        # slope_total = 0.0
        # trial_price = 0.0
        # offer_total = 0.0
        # bid_total = 0.0
        #
        #
        # for i in range(self.max_iterations):
        #     if not done:
        #         if self.sp_type == 0:
        #             trial_price = self.rea * self.dividend + self.reb
        #             done = True
        #
        #         if self.sp_type == 1:
        #             if i == 0:
        #                 trial_price = self.world_price
        #
        #             else:
        #                 imbalance = bid_total - offer_total
        #                 if imbalance <= self.min_excess and imbalance >= -self.min_excess:
        #                     done = True
        #                     continue
        #                 # print("HERE")
        #                 if slope_total != 0:
        #                     trial_price -= imbalance / slope_total
        #                 else:
        #                     trial_price += 1 + self.eta * imbalance
        #
        #
        #         elif self.sp_type == 2:
        #             if index == 0:
        #                 trial_price = self.world_price
        #             else:
        #                 trial_price *= self.world_price * (1 + self.eta * (bid_total - offer_total))
        #                 done = True
        #         trial_price = self.world_price
        #
        #         if trial_price < self.min_price:
        #             trial_price = self.min_price
        #         elif trial_price > self.max_price:
        #             trial_price = self.max_price
        #
        #         bid_total = 0
        #         offer_total = 0
        #         slope_total = 0
        #
        #         buys = 0
        #         sells = 0
        #         attempted_sells = 0
        #         attempted_buys = 0
        #
        #         for agent in self.agents:
        #             slope = 0
        #             slope, agent_price = agent.calc_demand_slope(slope, trial_price)
        #             slope_total += slope
        #
        #             if agent.__get_demand__ > 0.1:
        #                 bid_total += agent_price
        #                 buys += 1
        #                 attempted_buys += 1
        #
        #             elif agent.__get_demand__ < 0:
        #                 offer_total -= agent_price
        #                 sells += 1
        #                 attempted_sells += 1
        #
        #             demand_coefficient = attempted_sells *.01 if attempted_sells > attempted_buys else (attempted_buys *.01) + 1
        #             trial_price =
        #         self.volume = offer_total if bid_total > offer_total else bid_total
        #         self.bid_fraction = self.volume / bid_total if bid_total > 0 else 0
        #         self.offer_fraction = self.volume / offer_total if offer_total > 0 else 0
        #
        #
        #         print("TOTALS: ", bid_total, offer_total)
        #         print("VOLUME: ", self.volume, self.bid_fraction, self.offer_fraction)
        #         print("--------------------")
        trial_price = 0
        bid_total = 0
        offer_total = 0
        slope_total = 0

        buys = 0
        sells = 0
        attempted_sells = 0
        attempted_buys = 0

        trial_price = self.world_price
        for agent in self.agents:
            slope = 0
            slope, agent_price = agent.calc_demand_slope(slope, trial_price)
            slope_total += slope

            if agent.__get_demand__ > 0.2:
                buys += 1
                attempted_buys += 1
                bid_total += agent_price

            elif agent.__get_demand__ < -0.2:
                sells += 1
                attempted_sells += 1
                offer_total -= agent_price
        if attempted_sells > attempted_buys:
            demand_coefficient = attempted_sells * .01
        elif attempted_buys > attempted_sells:
            demand_coefficient = (attempted_buys * .01) + 1
        else:
            demand_coefficient = 1
        trial_price = self.world_dividend * demand_coefficient / self.int_rate

        if self.world_price - (self.world_price * .3) > trial_price:
            trial_price = self.world_price - (self.world_price * .3)

        if trial_price < self.min_price:
            trial_price = self.min_price
        elif trial_price > self.max_price:
            trial_price = self.max_price

        self.volume = abs(offer_total) if bid_total > offer_total else bid_total
        self.bid_fraction = self.volume / bid_total if bid_total > 0 else 0
        self.offer_fraction = self.volume / offer_total if offer_total > 0 else 0

        # print(trial_price)
        return trial_price

    def complete_trades(self):
        buys = 0
        sells = 0
        attempted_sells = 0
        attempted_buys = 0
        bf_price = self.bid_fraction * self.world_price
        of_price = self.offer_fraction * self.world_price
        t_price = self.taup_new * self.profit_per_unit

        for agent in self.agents:
            # Aggressive Buy
            # if agent.__get_demand__ > -0.1:
            if agent.__get_demand__ > 0.2:
                buys += 1
                attempted_buys += 1

            # Aggressive Sell
            elif agent.__get_demand__ < -.2:
            # elif agent.__get_demand__ <= -0.1:
                sells += 1
                attempted_sells += 1

            new_profit = self.taup_decay * agent.__get_profit__ + t_price * agent.__get_pos__
            agent.__set_profit__(new_profit)

        smallest_num = min(buys, sells)
        buys = smallest_num
        sells = smallest_num

        if buys != 0 and sells != 0:
            for i in range(smallest_num):
                agent = self.agents[smallest_num]
                if agent.__get_demand__ > 0.2:
                    new_position = agent.__get_pos__ + agent.__get_demand__*self.bid_fraction
                    agent.__set_pos__(new_position)

                    new_cash = agent.__get_cash__ - agent.__get_demand__ * bf_price
                    agent.__set_cash__(new_cash)

                elif agent.__get_demand__ < -0.2:
                    new_position = agent.__get_pos__ + agent.__get_demand__*self.offer_fraction
                    agent.__set_pos__(new_position)

                    new_cash = agent.__get_cash__ - agent.__get_demand__ * of_price
                    agent.__set_cash__(new_cash)


                # print("CASE 2", new_profit, new_position, new_cash)

        return buys, sells, attempted_sells, attempted_buys
