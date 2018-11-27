import Population
import Assets
import Conditions
import MarketMechanics
from itertools import *


class Market(object):
    def __init__(self):
        # Initialize population space
        self.population = Population.Population()

        # Initialize possible market conditions
        self.condition_list = Conditions.ConditionList()
        self.load_conditions()

        # Initialize market variables
        self.Mechanics = MarketMechanics.Mechanics(self.condition_list)
        self.init_dividend = self.Mechanics.__get_dividend__
        self.init_asset_price = self.Mechanics.__get_price__

        # Initialize assets
        # RISKY ASSETS
        # ----------
        self.risky_assets = []
        # Properties
        self.risky_asset_size = 300
        self.total_risky_asset_size = self.population.__sizeof__() + self.risky_asset_size
        self.remaining_asset_size = self.total_risky_asset_size
        self.init_asset_price = 50
        # Create assets & distribute 1 asset to each agent
        self.generate_risky_assets()
        self.birth_asset()

        # ----------
        # BONDS
        self.bonds = []
        self.starting_bond_price = 15

        self.curr_time = 0
        self.time_duration = 10000
        self.run_market()

    def __get_mechanics__(self):
        return self.Mechanics

    def __generate_bond_(self):
        bond = Assets.Bond(interest_rate=self.interest_rate, price=self.starting_bond_price)
        self.bonds.append(bond)
        return bond

    def run_market(self):
        for i in range(self.time_duration):
            pass

    def generate_risky_assets(self):
        for i in range(self.total_risky_asset_size):
            asset = Assets.RiskyAsset(dividend=self.init_dividend, price=self.init_asset_price, time=0)
            self.risky_assets.append(asset)

    def birth_asset(self):
        pop_iter = iter(self.population)
        for agent in pop_iter:
            asset = self.risky_assets[0]
            agent.give_risky_asset(asset)

            self.risky_assets = self.risky_assets[1:]
        self.remaining_asset_size = len(self.risky_assets)

    def load_conditions(self):
        with open('conditions.txt') as infile:
            for count, condition in enumerate(infile):
                try:
                    name, description, *rest = condition.replace("{", '').replace("}", "").replace('"', '').split(',')
                except Exception as e:
                    pass
                new_cond = Conditions.Condition(count, name, description)
                self.condition_list.__add__(new_cond)
                count += 1

    def __get_conditions__(self):
        for i in range(len(self.condition_list)):
            self.curr_conditions.append(self.verify(i))
        print(self.curr_conditions)


def test():
    test_market = Market()
    test_mechanics = test_market.__get_mechanics__()
    test_mechanics.print_values()


test()
