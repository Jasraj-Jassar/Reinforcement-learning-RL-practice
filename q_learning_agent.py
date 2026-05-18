import json
from pathlib import Path

from dino_interface import DO_NOTHING, JUMP


Q_TABLE_PATH = Path("q_table.json")
q_table = {}


def state_to_key(state_bucket):
    return "|".join(str(part) for part in state_bucket)


def key_to_state(key):
    distance, height, velocity, ground = key.split("|")
    return (int(distance), int(height), velocity, int(ground))


def get_q_values(state_bucket):
    if state_bucket not in q_table:
        q_table[state_bucket] = {
            DO_NOTHING: 0.0,
            JUMP: 0.0,
        }

    return q_table[state_bucket]


def choose_action(state_bucket):
    q_values = get_q_values(state_bucket)

    if q_values[JUMP] > q_values[DO_NOTHING]:
        return JUMP

    return DO_NOTHING


def save_q_table(path=Q_TABLE_PATH):
    json_ready_table = {}

    for state_bucket, q_values in q_table.items():
        json_ready_table[state_to_key(state_bucket)] = {
            str(action): value for action, value in q_values.items()
        }

    path.write_text(json.dumps(json_ready_table, indent=2), encoding="utf-8")


def load_q_table(path=Q_TABLE_PATH):
    if not path.exists():
        return

    saved_table = json.loads(path.read_text(encoding="utf-8"))
    q_table.clear()

    for state_key, q_values in saved_table.items():
        q_table[key_to_state(state_key)] = {
            int(action): value for action, value in q_values.items()
        }
