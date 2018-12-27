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

        self.buy_threshold = .2
        self.sell_threshold = -.2
        self.total_buys = 0
        self.total_sells = 0
        self.attempted_buys = 0
        self.attempted_sells = 0

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
        bid_total = 0
        offer_total = 0
        slope_total = 0

        self.total_buys = 0
        self.total_sells = 0
        self.attempted_buys = 0
        self.attempted_sells = 0

        trial_price = self.world_price
        for agent in self.agents:
            slope = 0
            slope, agent_price = agent.calc_demand_slope(slope, trial_price)
            slope_total += slope

            if agent.__get_demand__ > self.buy_threshold:
                self.total_buys += 1
                self.attempted_buys += 1
                bid_total += agent_price

            elif agent.__get_demand__ < self.sell_threshold:
                self.total_sells += 1
                self.attempted_sells += 1
                offer_total -= agent_price

        # Calculate price
        if self.attempted_sells > self.attempted_buys:
            demand_coefficient = self.attempted_sells * .01
        elif self.attempted_buys > self.attempted_sells:
            demand_coefficient = (self.attempted_buys * .01) + 1
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

        return trial_price

    def complete_trades(self):
        bf_price = self.bid_fraction * self.world_price
        of_price = self.offer_fraction * self.world_price
        t_price = self.taup_new * self.profit_per_unit

        for agent in self.agents:
            new_profit = self.taup_decay * agent.__get_profit__ + t_price * agent.__get_pos__
            agent.__set_profit__(new_profit)

        smallest_num = min(self.total_buys, self.total_sells)
        buys = smallest_num
        sells = smallest_num

        if buys != 0 and sells != 0:
            for i in range(smallest_num):

                agent = self.agents[i]
                if agent.__get_demand__ > self.buy_threshold:
                    new_position = agent.__get_pos__ + agent.__get_demand__*self.bid_fraction
                    agent.__set_pos__(new_position)

                    new_cash = agent.__get_cash__ - agent.__get_demand__ * bf_price
                    agent.__set_cash__(new_cash)

                elif agent.__get_demand__ < self.sell_threshold:
                    new_position = agent.__get_pos__ + agent.__get_demand__*self.offer_fraction
                    agent.__set_pos__(new_position)

                    new_cash = agent.__get_cash__ - agent.__get_demand__ * of_price
                    agent.__set_cash__(new_cash)

        return self.total_buys, self.total_sells, self.attempted_buys, self.attempted_sells
