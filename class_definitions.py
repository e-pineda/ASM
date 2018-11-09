class Agent(object):

	def init(self, money = None, assets = None, forecasting_rules = None, agent_type = None):
		self.money = 0
		self.assets = [] 
		self.forecasting_rules = []
		self.agent_type = agent_type
		# self.risk_preference =

	def get_money(self):
		return self.money

	def get_assets(self):
		return self.assets

	def get_rules(self):
		return self.forecasting_rules

	def get_agent_type(self):
		return self.agent_type

	# ----------------------------------

	def update_money(self, new_amount):
		self.money = self.money + new_amount

	# ----------------------------------

	def add_rule(self, new_rule):
		self.forecasting_rules.append(new_rule)

	def remove_rule(self, rule_to_remove):
		self.forecasting_rules.remove(rule_to_remove)

	def update_rule(self):
		pass

	def calculate_rule_accuracy(self, rule):
		pass

	def consider_rules(self):
		consider = [rule for rule in forecasting_rules if rule.get_condition == current_market_conditions]

	# ----------------------------------
	# ASSET METHODS
	def buy_risky_asset(self, r_asset):
		self.assets.append(r_asset)
		curr_price = -(r_asset.get_current_price())
		self.update_money(self, curr_price)

	def sell_risky_asset(self, r_asset):
		# try to sell
		# try:  
		# 	self.assets.remove(r_asset)
		# 	curr_price = r_asset.get_current_price()
		# 	self.update_money(self, curr_price)	


		# if someone can't sell
		# except:
			# some stuff
	# ----------------------------------

class Risky_Asset(object):
	
	def init(self, amount, dividend, price):
		self.amount = amount
		self.available_amount = amount
		self.dividend = dividend
		self.starting_price = price
		self.current_price = price

	def generate_dividend(self):
		pass

	def pay_dividend(self):
		pass

	def get_dividend(self):
		return self.dividend

	def get_amount(self):
		return self.amount

	def get_current_price(self):
		return self.current_price

	def decrement_amount(self, amount):
		self.available_amount = self.available_amount - amount

	def increment_amount(self, amount):
		self.available_amount = self.available_amount + amount		

	def update_price(self, new_price):
		self.current_price = new_price


class Bond(object):
	
	def init(self, amount, interest_rate, price):
		self.amount = amount
		self.interest_rate = interest_rate
		self.price = price

	def pay_interest(self):
		pass

	def get_interest_rate(self):
		return self.interest_rate

	def set_interest_rate(self, new_rate):
		self.interest_rate = new_rate


















