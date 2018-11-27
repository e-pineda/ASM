class RiskyAsset(object):

    def __init__(self, dividend, price, time):
        self.dividend = dividend
        self.starting_price = price
        self.current_price = price
        self.time = time

    def generate_dividend(self):
        pass

    def pay_dividend(self, agent):
        agent.update_money(dividend)

    def get_dividend(self):
        return self.dividend

    def get_amount(self):
        return self.amount

    def get_current_price(self):
        return self.current_price

    def __gettime__(self):
        return self.time

    def decrement_amount(self, amount):
        self.available_amount = self.available_amount - amount

    def increment_amount(self, amount):
        self.available_amount = self.available_amount + amount

    def update_price(self, new_price):
        self.current_price = new_price

    def __getinfo__(self):
        info = ''

        if self.time == 0:
            info += 'Risky asset was initialized to the agent\n'
        else:
            info += 'Risky asset purchased at time: ' + str(self.time) + "\n"
        info += 'Risky asset purchased at price: ' + str(self.starting_price) + "\n"
        info += "Risky asset's current price: " + str(self.current_price)

        return info


class Bond(object):

    def __init__(self, interest_rate, price):
        self.interest_rate = interest_rate
        self.price = price

    def pay_interest(self):
        pass

    def get_interest_rate(self):
        return self.interest_rate

    def get_price(self):
        return self.price

    def set_interest_rate(self, new_rate):
        self.interest_rate = new_rate


class RiskyAssets(object):
    def __init__(self):
        self.risky_assets = []
        self.curr_asset = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.curr_asset >= len(self.risky_assets):
            raise StopIteration
        else:
            self.curr_asset += 1
            return self.risky_assets[self.curr_asset - 1]

    def __len__(self):
        return len(self.risky_assets)

    def add_risky_asset(self, r_asset):
        self.risky_assets.append(r_asset)

    def remove_risky_asset(self):
        self.risky_assets = self.risky_assets[1:]

class Bonds(object):
    def __init__(self):
        self.bonds = []
        self.curr_asset = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.curr_asset >= len(self.bonds):
            raise StopIteration
        else:
            self.curr_asset += 1
            return self.bonds[self.curr_asset - 1]

    def __sizeof__(self):
        return len(self.bonds)

    def add_bond(self, bond):
        self.bonds.append(bond)

    def remove_bond(self):
        self.bonds = self.bonds[1:]
