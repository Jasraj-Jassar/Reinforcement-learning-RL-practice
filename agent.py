import random

from dino_interface import ACTIONS, DO_NOTHING, JUMP
from q_table_manager import get_q_values


DEFAULT_EXPLORATION_RATE = 0.2
LEARNING_RATE = 0.502
DISCOUNT_RATE = 0.95


def choose_best_action(state_bucket):
    q_values = get_q_values(state_bucket)

    if q_values[JUMP] > q_values[DO_NOTHING]:
        return JUMP

    return DO_NOTHING


def choose_action(state_bucket, exploration_rate=DEFAULT_EXPLORATION_RATE):
    if random.random() < exploration_rate:
        return random.choice(ACTIONS)

    return choose_best_action(state_bucket)


def learn(
    state_bucket,
    action,
    reward,
    next_state_bucket,
    done,
    learning_rate=LEARNING_RATE,
    discount_rate=DISCOUNT_RATE,
):
    q_values = get_q_values(state_bucket)
    old_q = q_values[action]

    if done:
        target_q = reward
    else:
        next_q_values = get_q_values(next_state_bucket)
        best_future_q = max(next_q_values.values())
        target_q = reward + discount_rate * best_future_q

    q_values[action] = old_q + learning_rate * (target_q - old_q)
    return q_values[action]
