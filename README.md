### Price Action Trader for IBKR

This is an automation tool for the IBKR trading platform.

#### Getting Started

1. **Clone the repository:**

   ```sh
   git clone https://github.com/ofins/price_action_trader.git
   cd price_action_trader
   ```

2. **Create and activate a virtual environment:**

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory and add your IBKR credentials and other necessary configurations.

   ```env
   IBKR_USERNAME=your_username
   IBKR_PASSWORD=your_password
   ```

5. **Run the application:**
   ```sh
   python main.py
   ```

#### Project Structure

```
price_action_trader/
├── main.py
├── connect.py
├── logger.py
├── reversal_algo.py
├── trading_app.py
├── discord_server.py
├── requirements.txt
├── .env
└── logs/
    └── 2025-02-28.log
```

#### Logging

Logs are stored in the `logs` directory. You can check the logs for detailed information about the application's execution.

#### Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

#### License

This project is licensed under the MIT License.
