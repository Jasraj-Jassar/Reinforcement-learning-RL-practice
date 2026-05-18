import os

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame

from dino_game import BLACK, FPS, GRAY, GROUND_Y, HEIGHT, RED, WHITE, WIDTH, draw_text
from dino_interface import DO_NOTHING, DinoRunnerInterface, action_name, get_state_bucket
from q_learning_agent import choose_action, get_q_values, load_q_table, save_q_table


def draw_interface_panel(screen, font, state, action, reward, done):
    bucket_state = get_state_bucket(state)
    q_values = get_q_values(bucket_state)
    lines = [
        "Agent sees",
        f"distance bucket: {bucket_state[0]}",
        f"height bucket: {bucket_state[1]}",
        f"velocity bucket: {bucket_state[2]}",
        f"ground bucket: {bucket_state[3]}",
        f"state: {bucket_state}",
        f"wait q: {q_values[0]:.2f}",
        f"jump q: {q_values[1]:.2f}",
        f"action: {action_name(action)}",
        f"reward: {reward:.1f}",
    ]

    panel_x = 510
    panel_y = 22
    line_height = 22

    for index, line in enumerate(lines):
        color = RED if done and line.startswith("reward") else BLACK
        draw_text(screen, font, line, panel_x, panel_y + index * line_height, color)


def main():
    load_q_table()

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Dino Runner RL Interface")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 21)
    big_font = pygame.font.SysFont(None, 44)

    env = DinoRunnerInterface(seed=1)
    state = env.reset()
    action = DO_NOTHING
    reward = 0.0
    done = False
    running = True

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not done:
            bucket_state = get_state_bucket(state)
            action = choose_action(bucket_state)
            state, reward, done, _info = env.step(action)

        screen.fill(WHITE)
        pygame.draw.line(screen, GRAY, (0, GROUND_Y), (WIDTH, GROUND_Y), 3)

        env.dino.draw(screen)
        env.obstacle.draw(screen)
        draw_interface_panel(screen, font, state, action, reward, done)

        if done:
            draw_text(screen, big_font, "Crashed", 225, 95, RED)
            draw_text(screen, font, "Close window to quit", 218, 140)

        pygame.display.flip()

    save_q_table()
    pygame.quit()


if __name__ == "__main__":
    main()
