# Stock Drop Notifier
![stock-drop-notifier](https://socialify.git.ci/hxu296/stock-drop-notifier/image?font=Inter&forks=1&issues=1&language=1&owner=1&pulls=1&stargazers=1&theme=Light)
<div align="center">

  <a href="">![build](https://github.com/hxu296/stock-drop-notifier/actions/workflows/docker-image.yml/badge.svg)</a>

</div>

## Index
- [About](#about)
- [Use Case Demo](#use-case-demo)
- [Unique Features](#unique-features)
- [Installation](#installation)
- [Project Architecture](#project-architecture)

## About
Stock Drop Notifier will monitor the stock information for an user-specified product on www.newegg.com and send Telegram message for real time stock update. Users can send Telegram command to customize a search filter, spawn new notifiers, and terminate old notifiers. Simply talk to the Telegram bot [@StockDropBot](https://telegram.me/StockDropBot) to use the service.


## Use Case Demo

| Use case      | Screenshot |
| ----------- | ----------- |
| Add a notifier to monitor all products on `newegg` that: <ul><li>contain any of the keywords `4080`, `RTX 4080`, `4090`, or `RTX 4090`</li><li>don't contain any of the keywords `mid tower`, `PC`, or `ATX` to exclude PC cases</li><li>have a price lower than `$1200`</li></ul> | ![add_example](./assets/add_example.png) |
| Remove the above-added notifier   | ![rm_example](./assets/rm_example.png)        |
| Receive stock notification about RTX 3080   | ![stock_notification](./assets/stock_notification.png)        |

## Unique Features
While most other stock informers adopt the naive approach of checking the "add to cart" keyword from webpage, our notifier used a tailored newegg parser to locate the price, dealer, and stock information for an product, which enables more complex search filters and higher information accuracy. 

Moreover, our notifier automated the process of manually entering product urls to check on. All you need to do is to give some search words, and the notifier will automatically find product urls based on them.


Finally, features of Stock Drop Notifier can be accessed through a Telegram bot. See [command.md](command.md) for details. 

## Installation
*Note: you don't need to host Stock Drop Notifier to use it. Simply talk to the Telegram bot [@StockDropBot](https://telegram.me/StockDropBot) to use the service.*

**Installation Option 1: Docker**
1. Receive and copy your telegram bot token from [@BotFather](https://telegram.me/BotFather).
2. Make sure you have Docker installed on your machine. 
3. Run the following command to start the bot.
```
    git clone https://github.com/hxu296/stock-drop-notifier.git
    cd stock-drop-notifier
    docker build -t stock-drop-notifier .
    docker run -d -e TELEGRAM_BOT_TOKEN="your_token" stock-drop-notifier
```
4. You can now talk to your Telegram bot using commands from [command.md](command.md).

**Installation Option 2: Bare-metal**

1. Receive and copy your telegram bot token from [@BotFather](https://telegram.me/BotFather).
2. Make sure your host machine has a Unix-like system with Python 3.6+ installed.
3. Run the following commands to set up the environment.
 ```
    git clone https://github.com/hxu296/stock-drop-notifier.git
    cd stock-drop-notifier
    pip3 install -r requirements.txt
    pip3 install python-telegram-bot --upgrade
```
4. To start the bot, run `python3 run.py -m` from the project root directory and paste your bot token according to the instruction.
4. You can now talk to your Telegram bot using commands from [command.md](command.md).


## Project Architecture
![architecture](./assets/architecture.png)



