import Conditions
import Dividend
import MovingAverages
import ForecastParams
import random


class Mechanics(object):
    def __init__(self):
        # important world variables
        self.moving_averages = 4
        self.dimensions = 61
        self.max_history = 500
        self.up_down_ref = 5
        self.p_up_down_bit = 42
        self.ratios = [.25, 0.5, 0.75, 0.875, 1.0, 1.125, 1.25, 1.5, 2.0, 4.0]
        # -------------------

        # MISC. VARIABLES
        self.int_rate = .1
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
        # Initialize possible market conditions
        self.conditions = Conditions.ConditionList()
        self.load_conditions()
        # -------------------

        #  FORECAST PARAMS
        # Initialize possible forecast params
        self.forecast_params = ForecastParams.Params(self.conditions)
        # -------------------

    @property
    def __get_rate__(self):
        return self.int_rate

    @property
    def __get_exponential_ma__(self):
        return self.exponential_ma

    @property
    def __get_dimensions__(self):
        return self.dimensions

    @property
    def __get_price__(self):
        return self.price

    @property
    def __get_profit_per_unit__(self):
        return self.profit_per_unit

    @property
    def __get_dividend__(self):
        return self.dividend

    @property
    def __get_risk_neutral__(self):
        return self.risk_neutral

    @property
    def __get_conditions__(self):
        return self.conditions

    @property
    def __get_forecast_params__(self):
        params_copy = self.forecast_params.__copy__
        return params_copy

    @property
    def __get_dividend_object__(self):
        return self.Dividend_obj

    def __set_dividend_vals__(self, baseline=None, min_dividend=None, max_dividend=None, amplitude=None, period=None):
        self.Dividend_obj.__set_baseline__(baseline)
        self.Dividend_obj.__set_min_dividend__(min_dividend)
        self.Dividend_obj.__set_max_dividend__(max_dividend)
        self.Dividend_obj.__set_amplitude__(amplitude)
        self.Dividend_obj.__set_period__(period)

    def __set_price__(self, new_price):
        self.saved_price = self.price

        if self.price != self.saved_price:
            print("Price was changed illegally.")

        self.old_price = self.price
        self.price = new_price

        self.profit_per_unit = self.price - self.old_price + self.dividend
        if self.old_price <= 0:
            self.return_ratio = self.profit_per_unit * 1000
        else:
            self.return_ratio = self.profit_per_unit / self.old_price

    def __set_dividend__(self, new_div):
        if self.dividend != self.saved_dividend:
            print("Dividend was changed illegally.")

        self.old_dividend = self.dividend
        self.dividend = new_div
        self.Dividend_obj.__set_dividend__(new_div)

        self.saved_dividend = self.dividend
        self.risk_neutral = self.dividend / self.int_rate

    def __set_int_rate__(self, rate):
        self.int_rate = rate

    def __set_exponential_ma__(self, aboolean):
        self.exponential_ma = aboolean

    def print_values(self):
        window = self.div_ma[0].__get__()
        print("New Dividend: ", self.dividend, "Div_ma: ", window)
        print(self.price)

    # -------------------
    def price_trend(self, n):
        if n > self.up_down_ref:
            print("argument " + str(n) + "to -pricetrend: exceeds: " + str(self.up_down_ref))

        for i in range(n):
            trend |= self.conditions[i+self.p_up_down_bit]

        if trend == 1:
            return 1
        elif trend == 2:
            return -1
        else:
            return 0

    # -------------------
    def __update_dividend__(self):
        new_div = self.Dividend_obj.forecast()
        self.__set_dividend__(new_div)
        return new_div

    def __update_market__(self):
        # self.print_values()
        # update dividend

        # get indicators of where price & dividend moves
        self.up_down_top = (self.up_down_top + 1) % self.up_down_ref
        self.price_up_down[self.up_down_top] = self.price > self.old_price
        self.dividend_up_down[self.up_down_top] = self.dividend > self.old_dividend

        self.history_top = self.history_top + 1 + self.max_history

        # add values to moving averages
        for i in range(self.moving_averages):
            position = (self.history_top - self.ma_length[i]) % self.max_history

            self.price_ma[i].__add__(self.price)
            self.div_ma[i].__add__(self.dividend)

            self.old_price_ma[i].__add__(self.price_history[position])
            self.old_div_ma[i].__add__(self.div_history[position])

        # add values to history arrays
        self.history_top %= self.max_history
        self.price_history[self.history_top] = self.price
        self.div_history[self.history_top] = self.dividend

        self.__gen_conditions__()
        return self.conditions
    # -------------------
    def __see_conditions__(self):
        for condition in self.conditions:
            print(condition.__get_id__, condition.__get_name__, condition.__getstate__)

    def load_conditions(self):
        with open('conditions.txt') as infile:
            index = 0
            for condition in infile:
                try:
                    name, description, *rest = condition.replace("{", '').replace("}", "").replace('"', '').split(',')
                except Exception as e:
                    pass
                new_cond = Conditions.Condition(index, name, description)
                self.conditions.__add__(new_cond)
                index += 1

    def __gen_conditions__(self):
        self.conditions[0].__setstate__(True)
        self.conditions[1].__setstate__(False)
        self.conditions[2].__setstate__(random.choice([True, False]))
        index = 3

        temp = self.up_down_top + self.up_down_ref
        for i in range(0, self.up_down_ref):
            if self.dividend_up_down[temp % self.up_down_ref] == 0:
                abool = False
            else:
                abool = True
            self.conditions[index].__setstate__(abool)
            # print(index, "test__3 - 7", self.conditions[index].__get_name__)
            index += 1
            temp -= 1

        # If dividend moving averages are moving up or down
        for i in range(0, self.moving_averages):
            self.conditions[index].__setstate__(self.div_ma[i].__get_ma__() > self.old_div_ma[i].__get_ma__())
            # print(index, "test__8 - 11", self.conditions[index].__get_name__)
            index += 1

        # If current dividend is greater than the moving average
        for i in range(0, self.moving_averages):
            self.conditions[index].__setstate__(self.dividend > self.div_ma[i].__get_ma__())
            # print(index, "test__12 - 15", self.conditions[index].__get_name__)
            index += 1

        # if dividend[i] > dividend [j]
        for i in range(0, self.moving_averages - 1):
            for j in range(i+1, self.moving_averages):
                self.conditions[index].__setstate__(self.div_ma[i].__get_ma__() > self.div_ma[j].__get_ma__())
                # print(index, "test__15 - 21", self.conditions[index].__get_name__)
                index += 1

        # Dividend as multiple of mean dividend
        multiple = self.dividend / self.dividend_scale
        for i in range(0, len(self.ratios)):
            self.conditions[index].__setstate__(multiple > self.ratios[i])
            # print(index, "test__22 - 31", self.conditions[index].__get_name__)
            index += 1

        # Price as multiple of dividend/intrate. Use olddividend
        multiple = (self.price * self.int_rate) / self.old_dividend
        for i in range(0, len(self.ratios)):
            self.conditions[index].__setstate__(multiple > self.ratios[i])
            # print(index, "test__32 - 41", self.conditions[index].__get_name__)
            index += 1

        temp = self.up_down_top + self.up_down_ref
        for i in range(0, self.up_down_ref):
            if self.price_up_down[temp % self.up_down_ref] == 0:
                abool = False
            else:
                abool = True
            self.conditions[index].__setstate__(abool)
            # print(index, "test__42 - 46", self.conditions[index].__get_name__)
            index += 1
            temp -= 1

        # Price moving averages went up or down
        for i in range(0, self.moving_averages):
            self.conditions[index].__setstate__(self.price_ma[i].__get_ma__() > self.old_price_ma[i].__get_ma__())
            # print(index, "test__47 - 50", self.conditions[index].__get_name__)
            index += 1

        # Price > MA[j]
        for i in range(0, self.moving_averages):
            self.conditions[index].__setstate__(self.price > self.price_ma[i].__get_ma__())
            # print(index, "test__51 - 54", self.conditions[index].__get_name__)
            index += 1

        # if price[i] > price[j]
        for i in range(0, self.moving_averages - 1):
            for j in range(i + 1, self.moving_averages):
                self.conditions[index].__setstate__(self.price_ma[i].__get_ma__() > self.old_price_ma[j].__get_ma__())
                # print(index, "test__55 - 60", self.conditions[index].__get_name__)
                index += 1

        if index != self.dimensions:
            print("Conditions determined != Dimensions")