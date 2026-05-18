# RL Practice Dino Runner

This is a tiny Pygame runner game for practicing reinforcement learning.

Right now it is just the playable base game: a small dino jumps over a moving obstacle. The next step is to turn the game logic into a simple environment that an agent can train against.

## Setup

```powershell
py -m pip install -r requirements.txt
```

## Run

```powershell
py dino_game.py
```

## Run Game With RL Interface

```powershell
py main.py
```

This opens the game and shows the interface values at the same time. `main.py` does not contain the learning agent yet. It initializes the interface, sends `0` by default, and lets you manually test the `1 = jump` command with the keyboard.

## RL Interface Demo

The RL side talks to `dino_interface.py` instead of the keyboard game loop.

```powershell
py dino_interface.py
```

That prints the values an agent can read:

- distance to the obstacle
- dino height
- dino vertical speed
- whether the dino is on the ground
- obstacle speed
- score

The action values are:

- `0`: do nothing
- `1`: jump

## Controls

- `Space`, `Up`, or `W`: jump
- `R`: restart after a crash
- `Esc` or `Q`: quit

## Learning Plan

1. Keep the game simple and understandable.
2. Add an RL-style `reset()` and `step(action)` environment.
3. Train a basic Q-learning agent.
4. Watch the trained agent play.
