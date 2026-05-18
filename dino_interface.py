import random
import time
from dataclasses import asdict, dataclass

from dino_game import Dino, Obstacle


DO_NOTHING = 0
JUMP = 1
ACTIONS = (DO_NOTHING, JUMP)


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


class DinoRunnerInterface:
    """Small RL-style interface for the dino game.

    The agent only talks to this class:
    - read current values with reset() or observe()
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

    def step(self, action):
        if action not in ACTIONS:
            raise ValueError(f"Unknown action {action}. Use 0=do nothing or 1=jump.")

        if self.game_over:
            return self.observe().as_dict(), 0.0, True, {
                "score": self.score,
                "reason": "game_over_reset_required",
            }

        jumped = False
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

        if jumped:
            reward -= 0.2

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


def main():
    env = DinoRunnerInterface(seed=1)
    state = env.reset()

    for step_number in range(300):
        action = DO_NOTHING
        state, reward, done, info = env.step(action)

        print(
            f"step={step_number:03d} "
            f"distance={state['distance_to_obstacle']:7.1f} "
            f"y={state['dino_y']:6.1f} "
            f"vy={state['dino_velocity_y']:6.1f} "
            f"ground={int(state['on_ground'])} "
            f"action={action_name(action):4s} "
            f"reward={reward:6.1f} "
            f"score={info['score']}"
        )

        if done:
            print("episode ended: crashed")
            break

        time.sleep(0.03)


if __name__ == "__main__":
    main()
