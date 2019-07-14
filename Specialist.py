import numpy
import operator


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
        self.int_rate = None
        self.world_price = None
        self.old_price = None
        self.world_dividend = None
        self.profit_per_unit = None
        self.agents = None
        self.min_cash = None
        self.min_holding = None
        self.buy_threshold = None
        self.sell_threshold = None

        self.total_buys = 0
        self.total_sells = 0
        self.attempted_buys = 0
        self.attempted_sells = 0

        self.recently_bought = {}
        self.recently_sold = {}
        self.profit_tracker = {}

    def __set_max_price__(self, x):
        self.max_price = x

    def __set_min_price__(self, x):
        self.min_price = x

    def __set_int_rate__(self, x):
        self.int_rate = x

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

    def __set_min_cash__(self, x):
        self.min_cash = x

    def __set_sell_threshold__(self, x):
        self.sell_threshold = x

    def __set_buy_threshold__(self, x):
        self.buy_threshold = x

    def __set_min_holding__(self, x):
        self.min_holding = x

    def __set_old_price__(self, x):
        self.old_price = x

    def __set_vals__(self, max_price=None, min_price=None, taup=None, sp_type=None, max_iterations=None,
                     min_excess=None, eta=None, rea=None, reb=None, agents=None, int_rate=None, min_cash=None,
                     sell_threshold=None, buy_threshold=None, min_holding=None):
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
        self.__set_int_rate__(int_rate)
        self.__set_min_cash__(min_cash)
        self.__set_min_holding__(min_holding)
        self.__set_sell_threshold__(sell_threshold)
        self.__set_buy_threshold__(buy_threshold)

    @property
    def __get_volume__(self):
        return self.volume

    def __get_agent__(self, id):
        for agent in self.agents:
            if id == agent.__get_id__:
                return agent

    def perform_trades(self):
        order_book_buys = {}
        order_book_sells = {}

        bid_total = 0
        offer_total = 0
        slope_total = 0

        self.total_buys = 0
        self.total_sells = 0
        self.attempted_buys = 0
        self.attempted_sells = 0

        # Increase in attempt buys/sells correlates to increase in eta
        eta = 0.0005

        trial_price = self.world_price

        for agent in self.agents:
            slope, agent_price = 0, 0
            slope, agent_price = agent.calc_demand_slope(slope, trial_price)
            slope_total += slope

            if agent.__get_demand__ >= self.buy_threshold:
                self.total_buys += 1
                self.attempted_buys += 1
                bid_total += agent.__get_demand__
                cash_to_bankruptcy = agent.__get_cash__ - self.min_cash
                if agent_price > cash_to_bankruptcy:
                    agent_price = cash_to_bankruptcy
                order_book_buys[agent.__get_id__] = agent_price

            elif agent.__get_demand__ <= self.sell_threshold:
                # if agent.__get_pos__ == self.min_holding:
                #     continue
                self.total_sells += 1
                self.attempted_sells += 1
                offer_total -= agent.__get_demand__
                order_book_sells[agent.__get_id__] = agent_price

        # match prices and calculate
        trial_price, matches = self.order_book(order_book_buys, order_book_sells)
        imbalance = bid_total - offer_total
        if trial_price == -1:
            trial_price = self.world_price
            print("ATTEMPT BUYS: ", len(order_book_buys), "; ATTEMPT SELLS: ", len(order_book_sells), "; IMBALANCE: ",
                  imbalance, "; SLOPE TOTAL: ", slope_total)
            trial_price *= 1 + eta * imbalance
            print(trial_price)

        if trial_price < self.min_price:
            trial_price = self.min_price
            try:
                print("TRIAL PRICE", trial_price, imbalance, slope_total, imbalance/slope_total)
            except ZeroDivisionError:
                pass
        elif trial_price > self.max_price:
            trial_price = self.max_price

        self.volume = abs(offer_total) if bid_total > offer_total else bid_total
        self.bid_fraction = self.volume / bid_total if bid_total > 0 else 0
        self.offer_fraction = self.volume / offer_total if offer_total > 0 else 0
        print('VOLUME: ', self.volume, 'Ask: ', offer_total, 'Bid ', bid_total)
        return trial_price, matches, bid_total, offer_total

    def order_book(self, buy_book, sell_book):
        price = 0
        matches = 0
        sell_prices = []
        sorted_buy = sorted(buy_book.items(), key=operator.itemgetter(1))
        sorted_sell = sorted(sell_book.items(), key=operator.itemgetter(1))
        if len(sorted_sell) == 0 or len(sorted_buy) == 0:
            return -1, matches

        for buy_order in sorted_buy:
            buyer_id, buy_price = buy_order[0], buy_order[1]
            seller_id, sell_price = sorted_sell[0][0], sorted_sell[0][1]

            self.recently_bought[buyer_id] = sell_price
            self.recently_sold[seller_id] = sell_price
            sell_prices.append(sell_price)

            sorted_sell = sorted_sell[1:]
            price += sell_price
            matches += 1

            if len(sorted_sell) == 0:
                break

        final_price = price/matches
        return final_price, matches

    def complete_trades(self):
        t_price = self.taup_new * self.profit_per_unit
        for agent in self.agents:
            new_profit = self.taup_decay * agent.__get_profit__ + t_price * agent.__get_pos__
            agent.__set_profit__(new_profit)

        # Recently Sold
        for seller in self.recently_sold:
            # print("Seller INFO", seller, self.recently_sold.get(seller))
            agent = self.__get_agent__(seller)

            # Update profits
            # new_profit = self.recently_sold.get(seller) - self.old_price
            # agent.__set_profit__(new_profit)

            # Update position and clip it if necessary
            new_position = agent.__get_pos__ + agent.__get_demand__*self.bid_fraction
            if new_position < self.min_holding:
                new_position = self.min_holding
            agent.__set_pos__(new_position)

            # Update cash
            new_cash = agent.__get_cash__ + self.recently_sold.get(seller)
            agent.__set_cash__(new_cash)

        # Recently sold
        for buyer in self.recently_bought:
            # print("Buyer INFO", buyer, self.recently_bought.get(buyer))
            agent = self.__get_agent__(buyer)

            # Update positions
            # new_profit = self.taup_decay * agent.__get_profit__ + t_price * agent.__get_pos__
            # agent.__set_profit__(new_profit)

            # Update position
            new_position = agent.__get_pos__ + agent.__get_demand__*self.offer_fraction
            agent.__set_pos__(new_position)

            # Update cash
            new_cash = agent.__get_cash__ - self.recently_bought.get(buyer)
            agent.__set_cash__(new_cash)

        self.old_price = self.world_price
        self.recently_bought.clear()
        self.recently_sold.clear()
        return self.total_buys, self.total_sells, self.attempted_buys, self.attempted_sells, self.agents
