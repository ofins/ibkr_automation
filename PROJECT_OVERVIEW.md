# IBKR Automation

<img src="./assets/pug.jpg" alt="mascot" width="200" />

## Overview

Hi, I'm a pug that automates trading strategies.

### Project Name

Pug: IBKR Automation

### Brief Description

An automation tool designed to facilitate trading on the IBKR platform using price action strategies.

### Tech Stack

- Python
- IBKR API
- Discord API
- Logging
- Speak

## Problem & Solution

### Problem Statement

Manual trading on the IBKR platform can be time-consuming and prone to human error.

### Your Solution

This project automates trading strategies based on price action and indicators, reducing the need for manual intervention and increasing trading efficiency.

### Main Features

- **Automated Trading**: Executes trades based on predefined strategies/algo.
- **Real-time Monitoring**: Continuously monitors selected stocks and market conditions.
- **Logging**: Detailed logging of all trading activities and system events.
- **Discord Notifications**: Receives prompt command from and sends real-time notifications to a Discord server.
- **Generate Daily Report**: Automate report generation with essential trade data analysis.

### Unique Functionality

- **Guardian Monitor**: Run a isolated command to protect your account events like over-exposure and help you close out trades at designated time.
- **Reversal Algorithm**: Implements a custom reversal algorithm to identify potential trade opportunities.
- **Scaling ALgorithm**: Implements custom pyramid scaling algorithm `In-Progress`.

### High-level Architecture

- **Main Application**: Coordinates all trading activities.
- **Connect Module**: Manages connections to the IBKR API.
- **Logger Module**: Handles logging of all activities.
- **Reversal Algorithm Module**: Implements the trading strategy.
- **Discord Server Module**: Manages notifications to Discord.

### Component Interaction

- **Frontend**: N/A
- **Backend**: Python scripts interacting with IBKR and Discord APIs.
- **Database**: N/A
- **APIs**: IBKR API, Discord API

## Challenges & Learnings

This is my first project on Python (coming from JavaScript), I had quite a few challenges with a lot of learning and fun. I refactored my codes several time to try to align with Python best-practices.

**API Integration**:

- Using IBKR's official lib is tedious and comes with a lot of work. I later found out a library that works similar to a framework for IBKR api, `ib-inysync`. This saved me a ton of time.

**Real-time Monitoring**:

- I designed this app to be able to do several things at once. Down to its core, it has to continuously fetch data from IBKR API while maintaining stable connection with Discord to send notification and receive prompt.

**Python**:

- Running individual files in isolation in my_module gave me a lot of bugs and error.
  Fix: `python -m my_module.file_name`

### Optimizations

- **Asynchronous Processing**: Used async functions to handle API calls efficiently.
- **Design Patterns**: Implemented Singleton pattern for the logger module.

## Deployment & Hosting

### Hosting

- **Local Machine**: Currently hosted and run on a local machine.

### CI/CD Setup

### Running Locally

1. **Clone the repository**:
   ```sh
   git clone https://github.com/ofins/price_action_trader.git
   cd price_action_trader
   ```
2. **Create and activate a virtual environment**:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
4. **Set up environment variables**:
   Create a `.env` file with your IBKR credentials.
   ```env
   DISCORD_TOKEN=your_discord_token
   DISCORD_CHANNEL_ID=your_discord_channel_id
   ```
5. **Run the application**:

   ```sh
   python main.py

   # Shortcuts
   python main.py --menu 1
   ```

## Future Improvements

### Planned Features

- **Enhanced Trading Strategies**: Implement additional trading strategies.
- **Web Interface**: Develop a web interface for easier monitoring and control.
- **Scalability**: Optimize the system for handling more stocks and higher trading volumes.

## Demo & Links

### Live Demo

- [Live Demo](#) (currently not available)

### GitHub Repository

- [GitHub Repository](https://github.com/ofins/price_action_trader)

### Media

- **Screenshots**: ![Screenshot](#)
- **Videos**: [Demo Video](#)
