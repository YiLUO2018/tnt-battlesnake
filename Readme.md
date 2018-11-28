# tnt-battlesnake

This repository contains a Battlesnake OpenAI Gym environment and Reinforcement Learning Agents, that operate in this environment.

## Quick start

```bash
# Create conda environment
conda create -n bs python=3.6 pip

# Activate environment
conda activate bs

# Install dependencies
pip install sacred gym black pylint tensorflow keras tensorboardX

# Train a DQN agent
python run.py train_dqn

# In another terminal window
tensorboard --logdir tmp
```

## Repository structure

- `common`
    - Common models and functions that can be shared between multiple RL algorithms.
- `dqn`
    - Contains a DQN agent with several improvements.
- `experiments`
    - Experiments should have an unique name and a `main.py` file which defines a `sacred` Experiment called `ex` for reproducibility.
- `gym_battlesnake`
    - An OpenAI `gym` environment for Battlesnake.
- `legacy`
    - Contains the old APEX-DQN code that has not been refactored yet.
