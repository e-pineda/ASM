import pandas as pd
import MarketMechanics
import Agents
import Specialist
import Conditions
import random
import numpy as np
import Graph
import threading


class Market(object):
    def __init__(self):
        # Initialize storage for market performance
        self.div_ratio, self.pr_ratio = [], []
        self.div_periods, self.pr_periods = [[], [], [], [], []], [[], [], [], [], []]
        self.div_mas, self.pr_mas = [[], [], [], []], [[], [], [], []]
        self.poor_performers, self.good_performers = [], []

        # Initialize model parameters
        self.model_params = {}
        self.__load_model_params__()
        self.prob_int_rate_change = self.model_params.get('prob_int_rate')
        self.int_rate = self.model_params.get('int_rate')
        self.min_int_rate = self.model_params.get("min_rate")
        self.max_int_rate = self.model_params.get("max_rate")

        # Initialize conditions
        self.conditions = Conditions.ConditionList()
        self.__load_conditions__()

        # Initialize forecast parameters
        self.forecast_params = {}
        self.__load_forecast_params__()

        # Initialize market mechanics
        self.Mechanics = MarketMechanics.Mechanics(self.model_params, self.conditions)
        self.__set_world_values__()

        # Store initial dividend and price
        self.init_dividend = self.Mechanics.__get_dividend__
        self.init_asset_price = self.Mechanics.__get_price__
        self.dividend_value = self.init_dividend
        self.price = self.init_asset_price

        # Initialize population space
        self.population = []
        self.risk_aversion_list = self.__gen_risk_dist__()
        self.__set_agent_values__()

        # Initialize market-maker
        self.specialist = Specialist.MarketClearer()
        self.__set_specialist_values__()

        # Clock
        self.curr_time = 0
        self.time_duration = int(self.model_params['time_duration'])
        self.warm_up_time = int(self.model_params['warm_up_time'])

        # bailout flag
        self.already_bailed = False

        # Changing Interest Rate
        self.dynamic_interest = self.model_params['dynamic_interest']

        # variables for graphs
        self.averages = {'avg_wealth': 0, 'avg_pos': 0, 'avg_cash': 0, 'avg_profit': 0}
        self.graph_save = self.model_params['graph_saving']

        # graphs
        self.market_graphs = Graph.MarketGraphs(self.time_duration, self.graph_save)
        self.price_ma_graphs = Graph.MAGraphs(self.time_duration, 'Price', self.graph_save)
        self.div_ma_graphs = Graph.MAGraphs(self.time_duration, 'Dividend', self.graph_save)
        self.agent_graphs = Graph.AgentGraphs(self.time_duration, self.graph_save)
        self.agent_performance_graphs = Graph.AgentPerformance(self.time_duration, self.graph_save)
        if self.dynamic_interest:
            self.interest_graphs = Graph.InterestRate(self.time_duration, self.graph_save)

        # Warm-Up and run
        self.warm_up()
        self.run_market()
        self.populate_records()

    @property
    def __get_agent_size__(self):
        return self.population.__sizeof__

    @property
    def __get_population__(self):
        return self.population

    @property
    def __get_agent_init_cash__(self):
        return self.model_params['initial_cash']

    @property
    def __get_mechanics__(self):
        return self.Mechanics

    @property
    def __get_specialist__(self):
        return self.Mechanics

    @property
    def __get_time__(self):
        return self.curr_time

    @property
    def __gen_agent_risk__(self):
        risk_preference = random.choice(self.risk_aversion_list)
        del self.risk_aversion_list[self.risk_aversion_list.index(risk_preference)]
        return risk_preference

    def __get_avgs__(self):
        for agent in self.population:
            self.averages['avg_cash'] += agent.__get_cash__
            self.averages["avg_pos"] += agent.__get_pos__
            self.averages['avg_profit'] += agent.__get_profit__
            self.averages['avg_wealth'] += agent.__get_wealth__

        self.averages['avg_cash'] /= len(self.population)
        self.averages["avg_pos"] /= len(self.population)
        self.averages['avg_profit'] /= len(self.population)
        self.averages['avg_wealth'] /= len(self.population)

    # generates normal distribution ranging from -1 to 1
    @staticmethod
    def __gen_risk_dist__():
        x = list(np.linspace(.31, .99, 100))
        return x

    def __load_model_params__(self):
        with open("model_params.txt", mode='r') as in_file:
            for line in in_file:
                if '=' not in line:
                    continue
                if line == "Forecast Parameters":
                    break

                parameter = line.split()
                param_var = parameter[0]

                if param_var == "ratios":
                    param_value = [float(value) for value in parameter[2:]]
                elif param_var == 'moving_average_lengths':
                    param_value = [int(value.strip(','))for value in parameter[2:]]
                elif param_var == 'dynamic_interest' or param_var == 'graph_saving' or param_var == 'make_mistakes' or param_var =='csv_save':
                    if parameter[2] == 'False':
                        param_value = False
                    else:
                        param_value = True

                else:
                    param_value = float(parameter[2])

                self.model_params[param_var] = param_value

    def __load_forecast_params__(self):
        flag = False

        with open("model_params.txt", mode='r') as in_file:
            for line in in_file:
                line = line.strip()
                if line == '':
                    continue
                if line == 'Forecast Parameters':
                    flag = True
                    continue
                if flag:
                    parameter = line.split()
                    param_var = parameter[0]
                    param_value = float(parameter[2])

                    self.forecast_params[param_var] = param_value

        self.forecast_params['cond_words'] = int((self.forecast_params['cond_bits'] + 15) / 16)
        self.forecast_params['a_range'] = self.forecast_params["a_max"] - self.forecast_params["a_min"]
        self.forecast_params['b_range'] = self.forecast_params["b_max"] - self.forecast_params["b_min"]
        self.forecast_params['c_range'] = self.forecast_params["c_max"] - self.forecast_params["c_min"]
        self.forecast_params['ga_prob'] = 1 / self.forecast_params['ga_freq']

        self.forecast_params['n_pool'] = self.forecast_params['num_forecasts'] * self.forecast_params['pool_fraction']
        self.forecast_params['n_new'] = self.forecast_params['num_forecasts'] * self.forecast_params['new_fraction']

        self.forecast_params['prob_list'] = [self.forecast_params['bit_prob'] for i in range(int(self.forecast_params['cond_bits']))]


    def __load_conditions__(self):
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

    def __set_world_values__(self):
        int_rate = self.model_params["int_rate"]
        self.Mechanics.__set_int_rate__(int_rate)

    def __set_specialist_values__(self):
        max_price = self.model_params["max_price"]
        min_price = self.model_params["min_price"]
        taup = self.model_params["taup"]
        sp_type = self.model_params["sp_type"]
        max_iterations = self.model_params["max_iterations"]
        min_excess = self.model_params["min_excess"]
        eta = self.model_params["eta"]
        rea = self.model_params["rea"]
        reb = self.model_params["reb"]
        int_rate = self.model_params['int_rate']
        min_cash = self.model_params['min_cash']
        sell_threshold = self.model_params['sell_threshold']
        buy_threshold = self.model_params['buy_threshold']
        min_holding = self.model_params['min_holding']
        self.specialist.__set_vals__(max_price=max_price, min_price=min_price, taup=taup, sp_type=sp_type,
                                     max_iterations=max_iterations, min_excess=min_excess, eta=eta, rea=rea, reb=reb,
                                     agents=self.population, int_rate=int_rate, min_cash=min_cash,
                                     sell_threshold=sell_threshold, buy_threshold=buy_threshold, min_holding=min_holding)

    def __set_agent_values__(self):
        int_rate = self.model_params["int_rate"]
        min_holding = self.model_params['min_holding']
        init_cash = self.model_params['init_cash']
        position = self.model_params['init_holding']
        min_cash = self.model_params['min_cash']
        tolerance = self.model_params['tolerance']
        mistake_threshold = self.model_params['mistake_threshold']
        make_mistakes = self.model_params['make_mistakes']

        for i in range(int(self.model_params['num_agents'])):
            agent = Agents.Agent(id=i, name='Agent '+str(i), int_rate=int_rate, min_holding=min_holding, 
                                 init_cash=init_cash, position=position, forecast_params=self.forecast_params, 
                                 dividend=self.init_dividend, price=self.init_asset_price, conditions=self.conditions, 
                                 min_cash=min_cash, risk_aversion=self.__gen_agent_risk__, tolerance=tolerance,
                                 mistake_threshold=mistake_threshold, make_mistakes=make_mistakes)
            agent.__set_holdings__()
            self.population.append(agent)

    def catch_market_states(self):
        price_history, div_history = self.Mechanics.__get_histories__
        price_ma, div_ma = self.Mechanics.__get_mas__

        # Dividend to mean dividend ratio
        self.div_ratio.append(self.Mechanics.__get_div_ratio__)

        # Price * interest to dividend dividend ratio
        self.pr_ratio.append(self.Mechanics.__get_price_ratio__)

        # Dividend and Price for the 5 most recent periods
        for i in range(5):
            self.div_periods[i].append(div_history[-i])
            self.pr_periods[i].append(price_history[-i])

        # Dividend moving average
        for i, ma in enumerate(div_ma):
            self.div_mas[i].append(ma.__get_ma__())

        # Price moving average
        for i, ma in enumerate(price_ma):
            self.pr_mas[i].append(ma.__get_ma__())

    def populate_records(self):
        data = {
            "Dividend Ratio": self.div_ratio,
            "Price ratio": self.pr_ratio,

            # 'Recent Div 1 period ago': self.div_periods[0],
            # 'Recent Div 2 periods ago': self.div_periods[1],
            # 'Recent Div 3 periods ago': self.div_periods[2],
            # 'Recent Div 4 periods ago': self.div_periods[3],
            # 'Recent Div 5 periods ago': self.div_periods[4],
            #
            # 'Recent Price 1 period': self.pr_periods[0],
            # 'Recent Price 2 periods ago': self.pr_periods[1],
            # 'Recent Price 3 periods ago': self.pr_periods[2],
            # 'Recent Price 4 periods ago': self.pr_periods[3],
            # 'Recent Price 5 periods ago': self.pr_periods[4],

            '5 Day Div Moving Average': self.div_mas[0],
            '20 Day Div Moving Average': self.div_mas[1],
            '100 Day Div Moving Average': self.div_mas[2],
            '500 Day Div Moving Average': self.div_mas[3],

            '5 Day Price Moving Average': self.pr_mas[0],
            '20 Day Price Moving Average': self.pr_mas[1],
            '100 Day Price Moving Average': self.pr_mas[2],
            '500 Day Price Moving Average': self.pr_mas[3]
        }
        df = pd.DataFrame(data)
        df.to_csv('market_states.csv')

    def warm_up(self):
        for i in range(self.warm_up_time):
            self.dividend_value = self.Mechanics.__update_dividend__()
            self.conditions = self.Mechanics.__update_market__()
            self.catch_market_states()

            self.price = self.dividend_value / self.model_params['int_rate']
            self.Mechanics.__set_price__(self.price)
        print("WARM UP COMPLETE")

    def condition_string(self):
        output = ''
        for condition in self.conditions:
            string = str(condition.__get__) + "\n"
            output += string
        return output

    def run_market(self):
        div = []
        price = []
        volumes = []
        buy = []
        sell = []
        attempt_buys = []
        attempt_sells = []
        matches = []
        interest_rates = []
        time = []
        bids = []
        asks = []
        for i in range(self.time_duration):
            print("TIME", self.curr_time)
            print('PRICE', self.price)
            
            # CHANGE INT RATE
            if self.dynamic_interest:
                chance_new_int_rate = random.randint(0, 10)/100
                if i >= 2500 and chance_new_int_rate < self.prob_int_rate_change:
                    self.change_int_rate()

            # Give agents their information
            self.give_info()

            # New Dividend
            self.new_dividend()

            # Credit earnings and pay taxes
            if self.curr_time > 1:
                self.credits_and_taxes()

            # Update the Market
            self.conditions = self.Mechanics.__update_market__()

            # Prepare agents for trades
            self.prepare_trades()

            # Calculate the new price and perform trades
            self.price, curr_matches, bid, ask = self.specialist.perform_trades()
            self.Mechanics.__set_price__(self.price)

            # Complete the trades
            self.specialist.__set_agents__(self.population)
            buys, sells, at_sells, at_buys, self.population = self.specialist.complete_trades()
            volume = self.specialist.__get_volume__

            # Update agent performance
            self.update_performances()

            # get good and bad performers
            self.check_performances()

            # record data
            div.append(self.dividend_value)
            price.append(self.price)
            volumes.append(volume)
            buy.append(buys)
            sell.append(sells)
            attempt_buys.append(at_buys)
            attempt_sells.append(at_sells)
            time.append(i)
            matches.append(curr_matches)
            interest_rates.append(self.int_rate)
            bids.append(bid)
            asks.append(ask)

            # graphs
            self.__get_avgs__()
            price_ma_dict = self.get_ma_values('price')
            div_ma_dict = self.get_ma_values('div')
            agent_performances = self.get_agent_performances()

            self.div_ma_graphs.graph_data(div_ma_dict)
            self.price_ma_graphs.graph_data(price_ma_dict)
            self.agent_graphs.graph_data(self.averages)
            self.agent_performance_graphs.graph_data(agent_performances)
            self.market_graphs.graph_data(self.price, curr_matches, bid, ask, volume)
            if self.dynamic_interest:
                self.interest_graphs.graph_data(self.int_rate)

            self.curr_time += 1

            print("-------------------")

        data = {"Price": price, "Dividend": div, "Volume": volumes, "Matches": matches, "Attempt Buys": attempt_buys,
                "Attempt Sells": attempt_sells, 'Interest Rates': self.int_rate, 'Total Bid': bids, 'Total Ask': asks,
                'Total Buys': buy, 'Total Sells': sell}
        self.save_data(data)

    def run_threaded(self, job_fn, kwargs):
        job_thread = threading.Thread(target=job_fn, kwargs=kwargs)
        job_thread.start()

    def get_agent_performances(self):
        return {'g_performers': len(self.good_performers), 'b_performers': len(self.poor_performers)}

    def get_ma_values(self, name):
        price_ma, div_ma = self.Mechanics.__get_mas__
        if name == 'price':
            return {'five_ma_val': price_ma[0].__get_ma__(), 'twenty_ma_val': price_ma[1].__get_ma__(), 'hundred_ma_val':
                   price_ma[2].__get_ma__(), 'five_hundred_ma_val': price_ma[3].__get_ma__()}
        else:
            return {'five_ma_val': div_ma[0].__get_ma__(), 'twenty_ma_val': div_ma[1].__get_ma__(), 'hundred_ma_val':
                   div_ma[2].__get_ma__(), 'five_hundred_ma_val': div_ma[3].__get_ma__()}

    def check_performances(self):
        self.poor_performers.clear()
        self.good_performers.clear()

        # redo in percentiles of wealth
        # wealth = [agent.__get_wealth__ for agent in self.population]
        # median_welth = np.percentile(wealth, 50)

        for agent in self.population:

            if agent.__get_wealth__ <= 0:
                self.poor_performers.append(agent)
                if agent in self.good_performers:
                    self.good_performers.remove(agent)

            elif agent.__get_wealth__ > 0:
                self.good_performers.append(agent)
                if agent in self.poor_performers:
                    self.poor_performers.remove(agent)

    def bailout(self, agents):
        for agent in agents:
            agent.bankrupt()

    def change_int_rate(self):
        choice = random.randint(1,2)
        if choice == 1:
            new_int_rate = self.int_rate - 0.01
        elif choice == 2:
            new_int_rate = self.int_rate + 0.01
        # new_int_rate = self.int_rate - .01

        if new_int_rate <= self.min_int_rate:
            new_int_rate = self.min_int_rate
        elif new_int_rate >= self.max_int_rate:
            new_int_rate = self.max_int_rate
        self.int_rate = new_int_rate

        self.Mechanics.__set_int_rate__(self.int_rate)
        self.specialist.__set_int_rate__(self.int_rate)
        for agent in self.population:
            agent.__set_int_rate__(self.int_rate)

        print("NEW INTEREST RATE", self.int_rate)
        # wait = input("WAITING: ")

    def new_dividend(self):
        self.dividend_value = self.Mechanics.__update_dividend__()

    def credits_and_taxes(self):
        for agent in self.population:
            agent.credit_earnings_and_taxes()

    def prepare_trades(self):
        for agent in self.population:
            agent.prepare_trading()

    def update_performances(self):
        for agent in self.population:
            agent.update_performance()

    def give_info(self):
        for agent in self.population:
            agent.__set_price__(self.price)
            agent.__set_dividend__(self.dividend_value)
            agent.__set_conditions__(self.conditions)
            agent.__set_time__(self.curr_time)

            if self.curr_time >= 1:
                agent.record_history()

        self.specialist.__set_world_price__(self.price)
        self.specialist.__set_world_dividend__(self.dividend_value)
        self.specialist.__set_profit_per_unit__(self.Mechanics.__get_profit_per_unit__)
        self.specialist.__set_agents__(self.population)

    def save_data(self, data):
        df = pd.DataFrame(data=data)
        df.to_csv('output.csv', sep='\t')
