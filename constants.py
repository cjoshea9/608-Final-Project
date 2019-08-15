import pygame
WIDTH = 1910
HEIGHT = 1070
FPS = 60
PERIOD = 1/FPS
# define colors
WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
ORANGE = (255,99,71)

target1_loc = [(3*WIDTH//8 - WIDTH//48, HEIGHT//8), (WIDTH//8 - WIDTH//24, HEIGHT//8),
               (WIDTH//8 - WIDTH//24, 3 * HEIGHT//8 - HEIGHT//12), (WIDTH // 8 - WIDTH // 24, 5 * HEIGHT // 8 + HEIGHT//12),
               (WIDTH//8 - WIDTH//24, 7 * HEIGHT//8), (3 * WIDTH//8 - WIDTH//48, 7 * HEIGHT//8)]

target2_loc = [(5 * WIDTH // 8 + WIDTH//48, HEIGHT//8), (7 * WIDTH // 8 + WIDTH//24, HEIGHT//8),
               (7 * WIDTH // 8 + WIDTH//24, 3*HEIGHT//8 - HEIGHT//12), (7 * WIDTH // 8 + WIDTH//24, 5*HEIGHT//8 + HEIGHT//12),
               (7 * WIDTH // 8 + WIDTH // 24, 7 * HEIGHT // 8), (5 * WIDTH // 8 + WIDTH//48, 7*HEIGHT//8)]


def get_text(type, size, color, text):
    if type in pygame.font.get_fonts():
        font = pygame.font.SysFont(type, size)
        final_text = font.render(text, True, color)
        return final_text
    else:
        raise ValueError(f"Font not in pygame fonts")

