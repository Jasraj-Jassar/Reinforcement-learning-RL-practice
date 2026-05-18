import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

from agent import DEFAULT_EXPLORATION_RATE, choose_action, learn
from dino_game import BLACK, FPS, GRAY, GROUND_Y, HEIGHT, RED, WHITE, WIDTH, Dino, Obstacle, draw_text
from dino_interface import DO_NOTHING, JUMP, get_jump_penalty, get_state_bucket
from q_table_manager import get_q_values, load_q_table, q_table, save_q_table


AGENT_COUNT = 100000
REFERENCE_AGENT_ID = 0
DRAW_SAMPLE_LIMIT = 400
SAVE_EVERY_FRAMES = FPS * 5
RESTART_DELAY_FRAMES = FPS

BLUE = (40, 100, 220)
GREEN = (40, 150, 80)
DARK_GRAY = (55, 55, 55)


def make_agent(index):
    return {
        "id": index,
        "dino": Dino(),
        "alive": True,
        "action": DO_NOTHING,
        "reward": 0.0,
        "score": 0,
        "exploration_rate": 0.0 if index == REFERENCE_AGENT_ID else DEFAULT_EXPLORATION_RATE,
    }


def get_agent_state(agent, obstacle, score):
    dino = agent["dino"]
    return {
        "distance_to_obstacle": obstacle.x - dino.x,
        "dino_y": dino.y,
        "dino_velocity_y": dino.velocity_y,
        "on_ground": dino.on_ground,
        "obstacle_speed": obstacle.speed,
        "score": score,
    }


def start_generation(generation):
    return {
        "generation": generation,
        "agents": [make_agent(index) for index in range(AGENT_COUNT)],
        "alive_count": AGENT_COUNT,
        "obstacle": Obstacle(),
        "score": 0,
        "best_score": 0,
        "restart_timer": 0,
    }


def step_game(game):
    obstacle = game["obstacle"]
    previous_obstacle_right = obstacle.rect.right
    updates = 0

    for agent in game["agents"]:
        if not agent["alive"]:
            continue

        state = get_agent_state(agent, obstacle, game["score"])
        state_bucket = get_state_bucket(state)
        action = choose_action(state_bucket, exploration_rate=agent["exploration_rate"])
        jumped = False

        if action == JUMP and agent["dino"].on_ground:
            agent["dino"].jump()
            jumped = True

        agent["dino"].update()
        agent["state_bucket"] = state_bucket
        agent["action"] = action
        agent["jumped"] = jumped
        agent["distance_to_obstacle"] = state["distance_to_obstacle"]

    obstacle.update()
    game["score"] += 1

    for agent in game["agents"]:
        if not agent["alive"]:
            continue

        next_state = get_agent_state(agent, obstacle, game["score"])
        next_state_bucket = get_state_bucket(next_state)

        reward = 0.1
        passed_obstacle = (
            previous_obstacle_right >= agent["dino"].x
            and obstacle.rect.right < agent["dino"].x
        )

        if passed_obstacle:
            reward += 10.0

        reward += get_jump_penalty(
            agent["action"],
            agent["jumped"],
            agent["distance_to_obstacle"],
        )

        done = agent["dino"].rect.colliderect(obstacle.rect)
        if done:
            reward = -100.0
            agent["alive"] = False
            game["alive_count"] -= 1

        learn(agent["state_bucket"], agent["action"], reward, next_state_bucket, done)

        agent["reward"] = reward
        agent["score"] = game["score"]
        updates += 1

    game["best_score"] = max(game["best_score"], game["score"])
    return updates


def draw_one_agent(screen, agent, color):
    dino = agent["dino"]
    visual_rect = dino.rect.copy()
    visual_rect.x += agent["id"] % 10
    pygame.draw.rect(screen, color, visual_rect)

    if agent["action"] == JUMP:
        pygame.draw.circle(screen, GREEN, (visual_rect.centerx, visual_rect.top - 7), 4)


def draw_agents(screen, game):
    drawn = 0

    for agent in game["agents"]:
        if not agent["alive"] or agent["id"] == REFERENCE_AGENT_ID:
            continue

        shade = 35 + int(140 * (drawn / max(DRAW_SAMPLE_LIMIT - 1, 1)))
        draw_one_agent(screen, agent, (shade, shade, shade))
        drawn += 1

        if drawn >= DRAW_SAMPLE_LIMIT:
            break

    reference_agent = game["agents"][REFERENCE_AGENT_ID]
    if reference_agent["alive"]:
        draw_one_agent(screen, reference_agent, BLUE)


def draw_dashboard(screen, font, game, total_updates):
    agents = game["agents"]
    reference_agent = agents[REFERENCE_AGENT_ID]
    sample_agent = reference_agent

    sample_state = get_agent_state(sample_agent, game["obstacle"], game["score"])
    sample_bucket = get_state_bucket(sample_state)
    sample_q = get_q_values(sample_bucket)

    lines = [
        f"{AGENT_COUNT} agents, one shared game",
        f"generation: {game['generation']}",
        f"alive: {game['alive_count']} / {AGENT_COUNT}",
        f"rendered: <= {DRAW_SAMPLE_LIMIT} + blue",
        f"blue alive: {reference_agent['alive']}",
        f"blue explore: {reference_agent['exploration_rate']:.0%}",
        f"score: {game['score']}",
        f"best score: {game['best_score']}",
        f"updates: {total_updates}",
        f"q states: {len(q_table)}",
        f"explore: {DEFAULT_EXPLORATION_RATE:.0%}",
        f"sample state: {sample_bucket}",
        f"wait q: {sample_q[0]:.2f}",
        f"jump q: {sample_q[1]:.2f}",
    ]

    for index, line in enumerate(lines):
        color = DARK_GRAY if index else BLACK
        draw_text(screen, font, line, 18, 16 + index * 20, color)


def main():
    load_q_table()
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Dino Runner {AGENT_COUNT} Agents One Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)
    big_font = pygame.font.SysFont(None, 42)

    game = start_generation(generation=1)
    total_updates = 0
    frames_since_save = 0
    running = True

    while running:
        clock.tick(FPS)
        frames_since_save += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if game["alive_count"] > 0:
            total_updates += step_game(game)
        else:
            game["restart_timer"] += 1
            if game["restart_timer"] >= RESTART_DELAY_FRAMES:
                game = start_generation(game["generation"] + 1)

        if frames_since_save >= SAVE_EVERY_FRAMES:
            save_q_table()
            frames_since_save = 0

        screen.fill(WHITE)
        pygame.draw.line(screen, GRAY, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)
        draw_agents(screen, game)
        game["obstacle"].draw(screen)
        draw_dashboard(screen, font, game, total_updates)

        if game["alive_count"] == 0:
            draw_text(screen, big_font, "Generation ended", 250, 122, RED)
            draw_text(screen, font, "New generation starting", 305, 164, DARK_GRAY)

        pygame.display.flip()

    save_q_table()
    pygame.quit()


if __name__ == "__main__":
    main()
