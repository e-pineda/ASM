# Artificial Stock Market X -- ASMX

This program attempts to generate an agent-based simulation of a simplified yet realistic stock market. 



## Traders
In this theoretical market, there are twenty-five traders who share nearly identical starting conditions. 
The only differing factor between traders is their natural level of risk-averseness.
Each agent's goal is to simply maximize the expected utility of their portfolio for the next period of the simulation.  
 
 
## Asset
The only asset within the market is a risky asset that pays a randomly-generated dividend per turn of the simulation. 
Any cash held by the agent earns interest per turn of the simulation. 
Further, it must be noted that each agent's earnings is subject to taxes per turn of the simulation.

## Conditions
As of now, there are over sixty different possible states the market can fulfill at any point during the simulation. 
These states may be a simple comparison between different market variables or, between the present and historical states of one market variable.
It must be stated that all traders within the market monitor the same twelve states to gather information about the market dynamics.

## Learning
Traders first attempt to forecast the price of the risky asset using whatever information they may have on the market state with their own set of one-hundred different forecasting methods. 
Essentially, each of these methods maps a set of market conditions to a set of forecasting parameters. 
Agents are only allowed to select one forecasting method per turn of the simulation. 
With this, it's important to mention that each agent learns by actively updating their set of forecasting methods through the Adaptive Rule Learning mechanism that I designed.
