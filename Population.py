from Agents import *
from Assets import *


class Population(object):

    def __init__(self):
        # POPULATION CONDITIONS
        self.start_money = 1000
        self.population_size = 100
        self.generate_population()
        self.curr_agent = 0

    def __sizeof__(self):
        return self.population_size

    def __iter__(self):
        return self

    def __next__(self):
        if self.curr_agent >= len(self.population):
            raise StopIteration
        else:
            self.curr_agent += 1
            return self.population[self.curr_agent - 1]

    def generate_population(self):
        self.population = []
        for i in range(self.population_size):
            agent_name = "Agent " + str(i + 1)
            agent_type = self.generate_agent_type()
            agent = Agent(money=self.start_money, name=agent_name, agent_type=agent_type)
            self.population.append(agent)

    def generate_agent_type(self):
        agent_types = ['Original']

        secure_random = random.SystemRandom()
        agent_type = secure_random.choice(agent_types)

        return agent_type

    def get_agents(self):
        population_iter = iter(self.population)
        return population_iter


