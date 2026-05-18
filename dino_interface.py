import random
from dataclasses import asdict, dataclass

from dino_game import Dino, Obstacle


DO_NOTHING = 0
JUMP = 1
ACTIONS = (DO_NOTHING, JUMP)

DINO_STANDING_Y = 192
DISTANCE_BUCKET_SIZE = 40
MAX_DISTANCE_BUCKET = 20
HEIGHT_BUCKET_SIZE = 20
MAX_HEIGHT_BUCKET = 6

NORMAL_JUMP_PENALTY = -0.2
EARLY_JUMP_PENALTY = -5.0
AIR_JUMP_PENALTY = -10.0
USEFUL_JUMP_DISTANCE = 220


@dataclass(frozen=True)
class DinoObservation:
    distance_to_obstacle: float
    dino_y: float
    dino_velocity_y: float
    on_ground: bool
    obstacle_speed: float
    score: int

    def as_dict(self):
        return asdict(self)


def bucket_number(value, bucket_size, max_bucket):
    if value < 0:
        return 0

    bucket = int(value // bucket_size)
    return min(bucket, max_bucket)


def bucket_velocity(velocity_y):
    if velocity_y < -1:
        return "up"
    if velocity_y > 1:
        return "down"
    return "still"


def get_state_bucket(state):
    distance_bucket = bucket_number(
        value=state["distance_to_obstacle"],
        bucket_size=DISTANCE_BUCKET_SIZE,
        max_bucket=MAX_DISTANCE_BUCKET,
    )
    height_bucket = bucket_number(
        value=DINO_STANDING_Y - state["dino_y"],
        bucket_size=HEIGHT_BUCKET_SIZE,
        max_bucket=MAX_HEIGHT_BUCKET,
    )
    velocity_bucket = bucket_velocity(state["dino_velocity_y"])
    ground_bucket = int(state["on_ground"])

    return (
        distance_bucket,
        height_bucket,
        velocity_bucket,
        ground_bucket,
    )


def get_jump_penalty(action, jumped, distance_to_obstacle):
    if action != JUMP:
        return 0.0

    if not jumped:
        return AIR_JUMP_PENALTY

    if distance_to_obstacle > USEFUL_JUMP_DISTANCE:
        return EARLY_JUMP_PENALTY

    return NORMAL_JUMP_PENALTY


class DinoRunnerInterface:
    """Small RL-style interface for the dino game.

    The agent only talks to this class:
    - read current values with reset() or observe()
    - read bucketed values with observe_bucket()
    - send an action with step(action)
    """

    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)

        self.dino = None
        self.obstacle = None
        self.score = 0
        self.game_over = False
        self.reset()

    def reset(self):
        self.dino = Dino()
        self.obstacle = Obstacle()
        self.score = 0
        self.game_over = False
        return self.observe().as_dict()

    def observe(self):
        return DinoObservation(
            distance_to_obstacle=self.obstacle.x - self.dino.x,
            dino_y=self.dino.y,
            dino_velocity_y=self.dino.velocity_y,
            on_ground=self.dino.on_ground,
            obstacle_speed=self.obstacle.speed,
            score=self.score,
        )

    def observe_bucket(self):
        return get_state_bucket(self.observe().as_dict())

    def step(self, action):
        if action not in ACTIONS:
            raise ValueError(f"Unknown action {action}. Use 0=do nothing or 1=jump.")

        if self.game_over:
            return self.observe().as_dict(), 0.0, True, {
                "score": self.score,
                "reason": "game_over_reset_required",
            }

        jumped = False
        distance_before_action = self.obstacle.x - self.dino.x

        if action == JUMP and self.dino.on_ground:
            self.dino.jump()
            jumped = True

        previous_obstacle_right = self.obstacle.rect.right

        self.dino.update()
        self.obstacle.update()
        self.score += 1

        reward = 0.1
        passed_obstacle = (
            previous_obstacle_right >= self.dino.x
            and self.obstacle.rect.right < self.dino.x
        )

        if passed_obstacle:
            reward += 10.0

        reward += get_jump_penalty(action, jumped, distance_before_action)

        if self.dino.rect.colliderect(self.obstacle.rect):
            self.game_over = True
            reward = -100.0

        return self.observe().as_dict(), reward, self.game_over, {
            "score": self.score,
            "jumped": jumped,
            "passed_obstacle": passed_obstacle,
        }


def action_name(action):
    if action == JUMP:
        return "jump"
    return "wait"
