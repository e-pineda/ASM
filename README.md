# Artificial Stock Market X -- ASMX

This program attempts to generate an agent-based simulation of a realistic stock market. In this market, all 
traders share nearly identical starting conditions in which the only differing factor are the traders'  risk-adverseness.
Each trader's goal is to simply maximize the expected utility of their portfolio for the next period of the simulation.  The only asset 
within the market is a risky asset that pays a randomly-generated dividend per turn of the simulation. Traders are subject to dividend earnings 
and taxes per turn of the simulation. 


#### Learning
Traders first attempt to forecast the price of the risky asset using whatever information they may have on the market state with their own set of one-hundred different forecasting methods. 
Essentially, each of these methods maps a set of market conditions to a set of forecasting parameters. 
Agents are only allowed to select one forecasting method per turn of the simulation. 
With this, it's important to mention that each agent learns by actively and independently updating their set of forecasting method through the Adaptive Rule Learning mechanism that I designed.

## Installation
Please make sure the following Python libraries are installed before running the program:
```
random
numpy
pandas
operator
matplotlib
math
```


## Usage

Simply run control.py!
 
All simulation parameters can and should be changed within params.txt.

Note: The program, by default, will save all market data within a .csv file and graphs as .mp4 files.

## Updates
1. Add Profit-per-Unit graph
2. Clean up graphs.py
3. Make into web-app
 

## Meta
Elijah Pineda - epineda@conncoll.edu - 
https://github.com/e-pineda

## License
[MIT](https://choosealicense.com/licenses/mit/)