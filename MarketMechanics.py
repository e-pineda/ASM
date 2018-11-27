import Conditions
import Dividend
import MovingAverages
import random


class Mechanics(object):
    def __init__(self, conditions):
        # important world variables
        self.moving_averages = 4
        self.dimensions = 61
        self.max_history = 500
        self.up_down_ref = 5
        # -------------------

        # MISC. VARIABLES
        self.int_rate = .3
        self.history_top = 0
        self.up_down_top = 0
        self.risk_neutral = 0
        # -------------------

        #  DIVIDENDS
        self.Dividend_obj = Dividend.Dividend()

        self.baseline = self.Dividend_obj.__get_baseline__()
        self.dividend_scale = self.baseline
        self.dividend = self.baseline
        self.Dividend_obj.__set_dividend__(self.dividend)

        self.old_dividend = self.dividend
        self.saved_dividend = self.dividend

        self.dividend_up_down = [0 for i in range(self.up_down_ref)]
        self.div_history = [0 for i in range(self.max_history)]
        # -------------------

        # PRICE
        self.price = self.baseline / self.int_rate
        self.old_price = self.price
        self.saved_price = self.price
        self.price_up_down = [0 for i in range(self.up_down_ref)]
        self.price_history = [0 for i in range(self.max_history)]
        # -------------------

        # RATIOS
        self.profit_per_unit = 0
        self.return_ratio = self.int_rate
        # -------------------

        # ARRAYS
        # Moving Averages
        self.exponential_ma = True
        self.ma_length = [5, 20, 100, self.max_history]

        self.price_ma = []
        self.old_price_ma = []
        self.div_ma = []
        self.old_div_ma = []

        for i in range(len(self.ma_length)):
            price_ma = MovingAverages.MovingAverage(self.ma_length[i], self.price)
            self.price_ma.append(price_ma)

            old_price_ma = MovingAverages.MovingAverage(self.ma_length[i], self.price)
            self.old_price_ma.append(old_price_ma)

            d_ma = MovingAverages.MovingAverage(self.ma_length[i], self.dividend)
            self.div_ma.append(d_ma)

            old_d_ma = MovingAverages.MovingAverage(self.ma_length[i], self.dividend)
            self.old_div_ma.append(old_d_ma)
        # -------------------

        #  CONDITIONS
        self.conditions = conditions
        self.__init_conditions__()
        # -------------------

    # ---------
    def print_values(self):
        for condition in self.conditions[:3]:
            condition.__print__()
    # ---------

    @property
    def __set_int_rate__(self, rate):
        self.int_rate = rate

    @property
    def __get_rate__(self):
        return self.int_rate

    @property
    def __set_exponential_ma__(self, aboolean):
        self.exponential_ma = aboolean

    @property
    def __get_exponential_ma__(self):
        return self.exponential_ma

    @property
    def __get_dimensions__(self):
        return self.dimensions

    @property
    def __set_price__(self, new_price):
        if self.price != self.saved_price:
            print("Price was changed illegally.")

        self.old_price = self.price
        self.price = new_price

        if self.old_price <= 0:
            self.return_ratio = self.profit_per_unit * 1000
        else:
            self.return_ratio = self.profit_per_unit / self.old_price

    @property
    def __get_price__(self):
        return self.price

    @property
    def __get_profit_per_unit__(self):
        return self.profit_per_unit

    def __set_dividend__(self, new_div):
        if self.dividend != self.saved_dividend:
            print("Dividend was changed illegally.")

        self.old_dividend = self.dividend
        self.dividend = new_div
        self.Dividend_obj.__set_dividend__(new_div)

        self.saved_dividend = self.dividend
        self.risk_neutral = self.dividend / self.int_rate

    @property
    def __get_dividend__(self):
        return self.dividend

    @property
    def __get_risk_neutral__(self):
        return self.risk_neutral

    # -------------------
    def price_trend(self, n):
        if n > self.up_down_ref:
            print("argument " + str(n) + "to -pricetrend: exceeds: " + str(self.up_down_ref))

        # for(i)

        if trend == 1:
            return 1
        elif trend == 2:
            return -1
        else:
            return 0

    @property
    def __update_market__(self):
        pass
    # -------------------

    def __init_conditions__(self):
        self.conditions[0].__setstate__(True)
        self.conditions[1].__setstate__(False)
        self.conditions[2].__setstate__(random.choice([True, False]))
        index = 3

        temp = self.up_down_top + self.up_down_ref
        