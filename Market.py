import Population
import Assets
import MarketMechanics
import Agents
import Specialist
import ModelParams
import ForecastParams
import Conditions
import csv
import pandas as pd
from itertools import *


class Market(object):
    def __init__(self):
        # Initialize storage for market performance
        self.div_ratio, self.pr_ratio = [], []
        self.div_periods, self.pr_periods = [[], [], [], [], []], [[], [], [], [], []]
        self.div_mas, self.pr_mas = [[], [], [], []], [[], [], [], []]

        # Initialize model parameters
        self.model_params = {}
        self.__load_model_params__()

        # Initialize conditions
        self.conditions = Conditions.ConditionList()
        self.__load_conditions__()

        # Initialize forecast parameters
        self.forecast_params = {}
        self.__load_forecast_params__()

        # Initialize market mechanics
        self.Mechanics = MarketMechanics.Mechanics(self.model_params, self.conditions)
        self.__set_world_values__()
        self.__set_dividend_values__()

        # Store initial dividend and price
        self.init_dividend = self.Mechanics.__get_dividend__
        self.init_asset_price = self.Mechanics.__get_price__
        self.dividend_value = self.init_dividend
        self.price = self.init_asset_price

        # Initialize population space
        self.population = []
        self.__set_agent_values__()

        # Initialize market-maker
        self.specialist = Specialist.MarketClearer()
        self.__set_specialist_values__()

        # Clock
        self.curr_time = 0
        self.time_duration = 1000
        self.warm_up_time = 501

        # Warm-Up and run
        self.warm_up()
        # self.run_market()
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
                else:
                    param_value = float(parameter[2])

                self.model_params[param_var] = param_value

    def __load_forecast_params__(self):
        flag = False

        with open("model_params.txt", mode='r') as in_file:
            for line in in_file:
                if '=' not in line or line == 'Forecast Parameters':
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

        monitor_conditions = ["pr/d>1/4", "pr/d>1/2", "pr/d>3/4", "pr/d>7/8", "pr/d>1", "pr/d>9/8", "p>p5",
                              "p>p20", "p>p100", "p>p500", "on", "off"]
        bit_list = [None for i in range(len(monitor_conditions))]
        for i, name in enumerate(monitor_conditions):
            bit_list[i] = self.conditions.__get_condition_id__(name)
        self.forecast_params['bit_list'] = bit_list

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

    def __set_dividend_values__(self):
        baseline = self.model_params["baseline"]
        min_dividend = self.model_params["min_dividend"]
        max_dividend = self.model_params["max_dividend"]
        amplitude = self.model_params["amplitude"]
        period = self.model_params["period"]

        self.Mechanics.__set_dividend_vals__(baseline=baseline, min_dividend=min_dividend, max_dividend=max_dividend,
                                             amplitude=amplitude, period=period)

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
        self.specialist.__set_vals__(max_price=max_price, min_price=min_price, taup=taup, sp_type=sp_type,
                                     max_iterations=max_iterations, min_excess=min_excess, eta=eta, rea=rea, reb=reb,
                                     agents=self.population)

    def __set_agent_values__(self):
        int_rate = self.model_params["int_rate"]
        min_holding = self.model_params['min_holding']
        init_cash = self.model_params['init_cash']
        position = self.model_params['init_holding']
        min_cash = self.model_params['min_cash']

        for i in range(int(self.model_params['num_agents'])):
            agent = Agents.Agent(id=i, name='Agent '+str(i), int_rate=int_rate, min_holding=min_holding, init_cash=init_cash, position=position,
                          forecast_params=self.forecast_params, dividend=self.init_dividend, price=self.init_asset_price, conditions=self.conditions, min_cash=min_cash)
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
        # div = []
        # price = []
        for i in range(self.warm_up_time):
            self.dividend_value = self.Mechanics.__update_dividend__()
            self.conditions = self.Mechanics.__update_market__()
            self.catch_market_states()
            condition_str = self.condition_string()

            self.price = self.dividend_value / self.model_params['int_rate']

            # div.append(self.dividend_value)
            # price.append((self.price))

            # data_add.append([i, self.dividend_value, self.price])


            # with open("conditions_output.txt", mode='a') as in_file:
            #     in_file.write("TIME: " + str(i))
            #     in_file.write(condition_str)
            #     in_file.write('\n----------------\n')
            self.Mechanics.__set_price__(self.price)

        # data = {"Dividend": div, "Price" :price}
        # df = pd.DataFrame(data=data)
        # print(df)
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
        time = []
        for i in range(self.time_duration):
            # Give agents their information
            self.give_info()

            # New Dividend
            self.new_dividend()

            # Credit earnings and pay taxes
            self.credits_and_taxes()

            # Update the Market
            self.conditions = self.Mechanics.__update_market__()

            # Prepare agents for trades
            self.prepare_trades()

            # Calculate the new price
            self.new_price()

            # Complete the trades
            buys, sells, at_sells, at_buys = self.specialist.complete_trades()
            volume = self.specialist.__get_volume__

            # Update agent performance
            self.update_performances()

            # conditions = self.Mechanics.__get_conditions__
            # condition_str = self.condition_string()


            # with open("simulation.txt", mode='a') as in_file:
            #     in_file_writer = csv.writer(in_file, delimiter=',')
            #     in_file_writer.writerow(["Time: " + str(i), "Dividend_value: " + str(self.dividend_value),
            #                              "Price: " + str(self.price), "Volume: " + str(volume), "Buys: " + str(buys),
            #                              "Attempted Buys: " + str(at_buys), "Sells: " + str(sells),
            #                              "Attempted Sells: " + str(attempt_sells)])
            #
            # with open("simulation_conditions_output.txt", mode='a') as in_file:
            #     in_file.write("TIME: " + str(i))
            #     in_file.write(condition_str)
            #     in_file.write('\n----------------\n')
            # print(self.curr_time)
            # self.agent_info()
            div.append(self.dividend_value)
            price.append(self.price)
            volumes.append(volume)
            buy.append(buys)
            sell.append(sells)
            attempt_buys.append(at_buys)
            attempt_sells.append(at_sells)
            time.append(i)
            # print(i)
            self.curr_time += 1
            # break
        data = {"Dividend": div, "Price" : price, "Volume" : volumes, "Buys" : buy, "Sells" : sell, "Attempt Buys" : attempt_buys, "Attempt Sells" : attempt_sells}
        df = pd.DataFrame(data=data)
        writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')
        df.to_excel(writer, 'Sheet1', engine='xlsxwriter')
        writer.save()

    def new_dividend(self):
        self.dividend_value = self.Mechanics.__update_dividend__()

    def credits_and_taxes(self):
        for agent in self.population:
            agent.credit_earnings_and_taxes()

    def prepare_trades(self):
        for agent in self.population:
            agent.prepare_trading()

    def new_price(self):
        self.price = self.specialist.perform_trades()
        self.Mechanics.__set_price__(self.price)
        # print("NEW PRICE", self.price)

    def update_performances(self):
        for agent in self.population:
            agent.update_performance()

    def give_info(self):
        for agent in self.population:
            agent.__set_price__(self.price)
            agent.__set_dividend__(self.dividend_value)
            agent.__set_conditions__(self.conditions)
            agent.__set_time__(self.curr_time)
            # if agent.__get_id__ == 0:
            #     print("MARKET TIME: ", time)
            #     print("MARKET CONDITIONS: ")
            #     self.print(conditions)
            #     print("AGENT TIME: ", agent.__get_time__)
            #     print("AGENT CONDITIONS:", agent.__get_conditions__)
            #     # agent.update_active_list()
            #     # agent.activate_ga()
            #     print("-------------------")

        self.specialist.__set_world_price__(self.price)
        self.specialist.__set_world_dividend__(self.dividend_value)
        self.specialist.__set_profit_per_unit__(self.Mechanics.__get_profit_per_unit__)
        self.specialist.__set_agents__(self.population)



def test():
    test_market = Market()

    # test_agents = test_market.__get_population__
    # agent = test_agents[0]
    # print(agent.__get_cash__)
    # mechanics.__update_market__()
    # mechanics.__see_conditions__()
    #
    # agent = test_market.__get_agents__(0)
    # agent.update_active_list()
    #
    # print("#############################")
    # print("FORECAST PARAMS")
    # params = mechanics.__get_forecast_params__
    # print(params)



test()
