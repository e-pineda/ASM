class Params(object):
    def __init__(self):
        self.num_agents = 25
        self.init_holding = 1
        self.initial_cash = 20000
        self.min_holding = -5
        self.min_cash = -2000
        self.int_rate = .1

        # Dividend
        self.baseline = 10
        self.min_dividend = .00005
        self.max_dividend = 100
        self.amplitude = .0873
        self.period = 19.5
        self.exponentialMAs = 1

        # Specialist
        self.max_price = 999999
        self.min_price = .001
        self.taup = 50
        self.sp_type = 1
        self.max_iterations = 20
        self.min_excess = .01
        self.eta = .0005
        self.eta_max = .05
        self.eta_min = .00001
        self.rea = 6.333
        self.reb = 16.6882

        # Agent params
        self.max_bid = 10
        self.max_dev = 500
        self.params = {}

    @property
    def load_conditions(self):
        self.params["num_agents"] = self.num_agents
        self.params["init_holding"] = self.init_holding
        self.params["init_cash"] = self.initial_cash
        self.params["min_holding"] = self.min_holding
        self.params["min_cash"] = self.min_cash
        self.params["int_rate"] = self.int_rate

        self.params["baseline"] = self.baseline
        self.params["min_dividend"] = self.min_dividend
        self.params["max_dividend"] = self.max_dividend
        self.params["amplitude"] = self.amplitude
        self.params["period"] = self.period
        self.params["exponentialMAs"] = self.exponentialMAs

        self.params["max_price"] = self.max_price
        self.params["min_price"] = self.min_price
        self.params["taup"] = self.taup
        self.params["sp_type"] = self.sp_type
        self.params["max_iterations"] = self.max_iterations
        self.params["min_excess"] = self.min_excess
        self.params["eta"] = self.eta
        self.params["eta_max"] = self.eta_max
        self.params["eta_min"] = self.eta_min
        self.params["rea"] = self.rea
        self.params["reb"] = self.reb
        self.params["randomSeed"] = self.randomSeed

        return self.params
