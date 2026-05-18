import argparse
import os
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

from agent import choose_best_action
from dino_game import BLACK, FPS, GRAY, GROUND_Y, HEIGHT, RED, WHITE, WIDTH, draw_text
from dino_interface import DO_NOTHING, DinoRunnerInterface, action_name, get_state_bucket
from q_table_manager import Q_TABLE_PATH, get_q_values, load_q_table, q_table


BEST_Q_TABLE_PATH = Path("best_q_table.json")
AUTO_RESET_FRAMES = FPS


def default_table_path():
    if BEST_Q_TABLE_PATH.exists():
        return BEST_Q_TABLE_PATH

    return Q_TABLE_PATH


def draw_status_panel(screen, font, state, action, score, best_score, table_path):
    bucket_state = get_state_bucket(state)
    q_values = get_q_values(bucket_state)
    lines = [
        "Watching trained model",
        f"table: {table_path}",
        "explore: 0%",
        f"score: {score}",
        f"best score: {best_score}",
        f"distance bucket: {bucket_state[0]}",
        f"height bucket: {bucket_state[1]}",
        f"velocity bucket: {bucket_state[2]}",
        f"ground bucket: {bucket_state[3]}",
        f"wait q: {q_values[0]:.2f}",
        f"jump q: {q_values[1]:.2f}",
        f"action: {action_name(action)}",
    ]

    for index, line in enumerate(lines):
        color = BLACK if index else RED
        draw_text(screen, font, line, 500, 18 + index * 21, color)


def parse_args():
    parser = argparse.ArgumentParser(description="Watch the trained Dino model.")
    parser.add_argument(
        "--table",
        type=Path,
        default=default_table_path(),
        help="Q-table JSON to load. Defaults to best_q_table.json if it exists.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    load_q_table(args.table)

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Dino Model Viewer - {args.table}")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)
    big_font = pygame.font.SysFont(None, 42)

    env = DinoRunnerInterface()
    state = env.reset()
    action = DO_NOTHING
    score = 0
    best_score = 0
    done = False
    reset_timer = 0
    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not done:
            bucket_state = get_state_bucket(state)
            action = choose_best_action(bucket_state)
            state, _reward, done, info = env.step(action)
            score = info["score"]
            best_score = max(best_score, score)
        else:
            reset_timer += 1

            if reset_timer >= AUTO_RESET_FRAMES:
                state = env.reset()
                action = DO_NOTHING
                score = 0
                done = False
                reset_timer = 0

        screen.fill(WHITE)
        pygame.draw.line(screen, GRAY, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)
        env.dino.draw(screen)
        env.obstacle.draw(screen)
        draw_status_panel(screen, font, state, action, score, best_score, args.table)

        if done:
            draw_text(screen, big_font, "Crashed", 225, 95, RED)
            draw_text(screen, font, "Auto restarting", 235, 140)

        pygame.display.flip()

    pygame.quit()

    if not q_table:
        print(f"No Q-table data loaded from {args.table}")


if __name__ == "__main__":
    main()
