import random

import matplotlib.pyplot as plt

# Parameters
initial_reward = 10
min_reward = 5
max_reward = 50
attempts = 100000

# Simulation
reward = initial_reward
total_reward = 0
total_rewards = []

for _ in range(attempts):
    # Simulate a win/loss (52% chance of win, 48% chance of loss)
    if random.random() < 0.3:  # Win (52% chance)
        total_reward += reward * 3
        # reward = max(max_reward, reward + 5)
    else:  # Loss (48% chance)
        total_reward -= reward
        # reward = min(min_reward, reward - 5)

    total_rewards.append(total_reward)

# Plot the graph
plt.figure(figsize=(10, 6))
plt.plot(total_rewards, label="Total Reward")
plt.xlabel("Attempts")
plt.ylabel("Total Reward")
plt.title("Total Reward vs Attempts")
plt.legend()
plt.show()
