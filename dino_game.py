import os
import random

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame


WIDTH = 800
HEIGHT = 300
FPS = 60

GROUND_Y = 240

WHITE = (245, 245, 245)
BLACK = (25, 25, 25)
GRAY = (120, 120, 120)
RED = (200, 40, 40)


class Dino:
    def __init__(self):
        self.width = 36
        self.height = 48
        self.x = 80
        self.y = GROUND_Y - self.height
        self.velocity_y = 0
        self.gravity = 1.1
        self.jump_power = -18
        self.on_ground = True

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def jump(self):
        if self.on_ground:
            self.velocity_y = self.jump_power
            self.on_ground = False

    def update(self):
        self.velocity_y += self.gravity
        self.y += self.velocity_y

        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.velocity_y = 0
            self.on_ground = True

    def draw(self, screen):
        pygame.draw.rect(screen, BLACK, self.rect)


class Obstacle:
    def __init__(self):
        self.width = 28
        self.height = 42
        self.speed = 7
        self.reset()

    @property
    def rect(self):
        return pygame.Rect(self.x, GROUND_Y - self.height, self.width, self.height)

    def reset(self):
        self.x = WIDTH + random.randint(100, 350)

    def update(self):
        self.x -= self.speed
        if self.x + self.width < 0:
            self.reset()

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)


def draw_text(screen, font, text, x, y, color=BLACK):
    image = font.render(text, True, color)
    screen.blit(image, (x, y))
