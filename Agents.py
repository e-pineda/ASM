import random
import Assets

class Agent(object):

    def __init__(self, name=None, money = None, agent_type = None):
        self.name = name
        self.money = money
        self.agent_type = agent_type

        self.risky_assets = Assets.RiskyAssets()
        self.bonds = Assets.Bonds()

        # self.demand =
        # self.position =
        # self.forecasting_rules =
        # self.risk_preference =

    def __setpos__(self, new_position):
        self.position = new_position

    def __getpos__(self, item):
        return self.position

    def get_name(self):
        return self.name

    def get_money(self):
        return self.money

    def get_risky_assets(self):
        r_assets = iter(self.risky_assets)
        for asset in (r_assets):
            yield asset

    def get_risky_asset_info(self):
        r_assets = iter(self.risky_assets)
        info = ''
        for asset in (r_assets):
            info += "Name: " + self.name + "\n"
            info += "Has: " + str(len(self.risky_assets)) + " asset(s)" + "\n"
            info += asset.__getinfo__()
        return info

    def get_bonds(self):
        iter_bonds = iter(self.bonds)
        for bond in iter_bonds:
            yield bond

    def get_rules(self):
        return self.forecasting_rules

    def get_agent_type(self):
        return self.agent_type

    def add_rule(self, new_rule):
        self.forecasting_rules.append(new_rule)

    def remove_rule(self, rule_to_remove):
        self.forecasting_rules.remove(rule_to_remove)

    def update_rule(self):
        pass

    def give_risky_asset(self, asset):
        self.risky_assets.add_risky_asset(asset)

    def consider_rules(self):
        self.consider = [rule for rule in forecasting_rules if rule.get_condition() == current_market_conditions]

    # ASSET METHODS
    def buy_risky_asset(self, r_asset):
        pass
        # try to buy
        # try:
            # self.assets.append(r_asset)
            # curr_price = -1 * (r_asset.get_current_price())
            # self.update_money(self, curr_price)

        # not enough shares, then run the market clearing process
        # except:
            # some stuff

    def sell_risky_asset(self, r_asset):
        pass
        # try to sell

        # try:
        # 	self.assets.remove(r_asset)
        # 	curr_price = r_asset.get_current_price()
        # 	self.update_money(self, curr_price)


        # if someone can't sell
        # except:
            # some stuff
    # ----------------------------------

class Rule(object):
    def __init__(self, conditions, parameters):
        self.conditions = conditions
        self.parameters = parameters
        self.accuracy = 0

    def get_condition(self):
        return self.conditions

    def get_parameters(self):
        return self.parameters

    def calculate_rule_accuracy(self, rule):
        pass

    def update_parameters(self):
        pass



