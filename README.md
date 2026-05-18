# RL Practice Dino Runner

This is a tiny Pygame runner game for practicing reinforcement learning.

Right now `main.py` starts the game, the RL interface, and the Q-table agent. The agent is not trained yet, so it mostly waits and crashes until we add learning.

## Setup

```powershell
py -m pip install -r requirements.txt
```

## Run

```powershell
py main.py
```

This initializes the game, the RL interface, and the Q-table agent. The agent reads the bucketed state, chooses an action from the Q-table, and sends that action to the game.

The Q-table is not trained yet, so the agent will usually choose `0 = do nothing` until we add learning.

The UI shows the values the agent sees:

- distance bucket
- height bucket
- velocity bucket
- ground bucket
- Q-values for wait and jump
- chosen action and reward

The action values are:

- `0`: do nothing
- `1`: jump

## Controls

There are no keyboard controls in the RL runner. Close the game window to quit.

## Learning Plan

1. Keep the game simple and understandable.
2. Add an RL-style `reset()` and `step(action)` environment.
3. Train a basic Q-learning agent.
4. Watch the trained agent play.
