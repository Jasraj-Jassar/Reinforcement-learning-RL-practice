# RL Practice Dino Runner

This is a tiny Pygame runner game for practicing reinforcement learning.

Right now `main.py` starts the game, the RL interface, and the Q-table agent. The agent updates Q-values from reward feedback while the game runs.

## Setup

```powershell
py -m pip install -r requirements.txt
```

## Run

```powershell
py main.py
```

This initializes the game, the RL interface, and the Q-table agent. The agent reads the bucketed state, chooses an action from the Q-table, sends that action to the game, then updates the Q-table from the reward.

The Q-table is saved to `q_table.json` after each crash/reset and when the window closes.

For a visual 100-agent trainer in one shared game:

```powershell
py multi_agent_runner.py
```

It starts each generation with 100 agents in the same game. Agents disappear when they crash, and a new 100-agent generation starts when none are left.

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

## How Learning Works

1. The interface turns the game numbers into one bucketed state, like `(3, 0, "still", 1)`.
2. The Q-table looks up the current scores for waiting and jumping in that state.
3. The agent either explores with a random action or uses the action with the better Q-value.
4. The game runs that action for one frame and returns the next state, reward, and crash flag.
5. The next state is bucketed too, so the agent can compare where it was to where it ended up.
6. The agent updates the Q-value for the action it just took using the reward and best future Q-value.
7. The table is saved to `q_table.json`, so learned values carry over between runs.

## Controls

There are no keyboard controls in the RL runner. Close the game window to quit.

## Learning Plan

1. Keep the game simple and understandable.
2. Add an RL-style `reset()` and `step(action)` environment.
3. Train a basic Q-learning agent.
4. Watch the trained agent play.
