import math
import numpy as np
import random


class Dividend(object):
    def __init__(self):
        self.baseline = None

        self.normal_dist = self.gen_normal_dist()

        self.min_dividend = None
        self.max_dividend = None
        self.amplitude = None
        self.period = None

        self.derived_params = None
        self.deviation = None
        self.rho = None
        self.gauss = None
        self.dividend = None

    def __get__(self):
        new_value = self.forecast()
        return self.dividend, new_value

    def derived_params_empty(self):
        if self.derived_params is None:
            return True
        return False

    # sets derived params when needed
    def set_derived_params(self):
        self.derived_params = 0

        self.deviation = self.baseline * self.amplitude

        self.rho = math.exp(-1.0 / self.period)
        self.rho = 0.0001 * round(10000.0 * self.rho)

        self.gauss = self.deviation * math.sqrt(1.0 - self.rho * self.rho)

        sample = self.__get_sample__
        self.dividend = self.baseline + (self.gauss * sample)

        # print("Deviation", self.deviation)
        # print("rho", self.rho)
        # print("Gauss", self.gauss)
        # print("Dividend", self.dividend)

    def __set_baseline__(self, new_base):
        self.baseline = new_base

    def __get_baseline__(self):
        return self.baseline

    def __set_dividend__(self, new_div):
        self.dividend = new_div

    def __get_dividend__(self):
        return self.dividend

    def __set_min_dividend__(self, new_min):
        self.min_dividend = new_min

    def __set_max_dividend__(self, new_max):
        self.max_dividend = new_max

    def __set_amplitude__(self, new_amplitude):
        self.amplitude = new_amplitude

        if self.amplitude < 0.0:
            self.amplitude = 0.0

        elif self.amplitude > 1.0:
            self.amplitude = 1.0

        self.amplitude = 0.0001 * round(10000.0 * self.amplitude)

    def __set_period__(self, new_period):
        self.period = new_period

        if self.period < 2:
            self.period = 2

    # generates the next value of the dividend regardless of the time value
    def forecast(self):
        if self.derived_params_empty():
            self.set_derived_params()

        next_dividend = self.baseline + self.rho * (self.dividend - self.baseline) + \
                        (self.gauss * self.__get_sample__)

        if next_dividend < self.min_dividend:
            next_dividend = self.min_dividend

        elif next_dividend > self.max_dividend:
            next_dividend = self.max_dividend

        # print("Next dividend", next_dividend)
        return next_dividend

    # generates normal distribution ranging from -1 to 1
    @staticmethod
    def gen_normal_dist():
        mu = 0
        sigma = 1 / 3
        x = list(np.linspace(mu - 3 * sigma, mu + 3 * sigma, 500))
        return x

    # gets random sample from normal distribution
    @property
    def __get_sample__(self):
        return random.choice(self.normal_dist)


# def test():
    # test_div = Dividend()
    # if test_div.derived_params_empty():
    #     test_div.set_derived_params()
    # for i in range(10):
    #     print("-- Turn " + str(i) + " --")
    #     test_div.forecast()
    #     print("-------")

# test()