### Disclaimer

This repo is for educational purpose only. It takes a lot more improvements and feature to apply it to real live trading.

### Intro

This is my personal repo to study machine learning in algo trading, where I will use the models from scikit-learn library to train and run an automatic trading bot using metatrader 5 library.

### Features

- Fetch data from metatrader 5, spice things up a bit with some indicators then save to a csv file. You would need an account from your broker and have metatrader 5 terminal installed on your computer.
- Declare models and train them using the fetched data. I will just declare some models and their default parameters. Improving the model's performance is a real problem and it requires a lot of testing.
- A Custom accuracy metric to determine how many times the model predict the price movement correctly.
- Automatic trading using metatrader 5 client. This is how I front test the models using my demo account from my mt5 broker, and realize that my trained models are a bunch of craps. 
 
### Improvements currently in my head

- Hyperparameters, feature selections, other indicators. Anything that can improve my win rate from 52%
- Risk management. Currently the bot's mechanic is to open the position on candle open, and close on candle close if the model predict a change in direction. No stop loss or take profit, which can drastically affect the model's performance.

### Summary

Applying machine learning to algo trading is a complicated, but very tempting problem with a huge reward if success. I would love to receive any contribution and feedback to my repo to solve it and defeat the market.
