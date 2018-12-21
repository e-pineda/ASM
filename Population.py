from Agents import *
from Assets import *


class Population(object):

    def __init__(self, forecast_params, price, dividend, conditions):
        # POPULATION CONDITIONS
        self.population_size = 25
        self.curr_agent = 0
        self.forecast_params = forecast_params
        self.price = price
        self.dividend = dividend
        self.conditions = conditions
        self.generate_population()

    @property
    def __sizeof__(self):
        return self.population_size

    def __iter__(self):
        return self

    def __next__(self):
        if self.curr_agent >= len(self.population):
            self.curr_agent = 0
            raise StopIteration
        else:
            self.curr_agent += 1
            return self.population[self.curr_agent - 1]

    def generate_population(self):
        self.population = []
        for i in range(self.population_size):

            agent_name = "Agent " + str(i + 1)
            agent_type = self.generate_agent_type

            agent = Agent(id=i, name=agent_name, agent_type=agent_type,
                          forecast_params=self.forecast_params, price=self.price,
                          dividend=self.dividend, conditions=self.conditions)
            self.population.append(agent)

    @property
    def generate_agent_type(self):
        agent_types = ['Original']

        secure_random = random.SystemRandom()
        agent_type = secure_random.choice(agent_types)

        return agent_type

    def get_agents(self):
        population_iter = iter(self.population)
        return population_iter



