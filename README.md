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

## Controls

- `Space`, `Up`, or `W`: jump
- `R`: restart after a crash
- `Esc` or `Q`: quit

## Learning Plan

1. Keep the game simple and understandable.
2. Add an RL-style `reset()` and `step(action)` environment.
3. Train a basic Q-learning agent.
4. Watch the trained agent play.
