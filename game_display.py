import pygame
import constants
import statemachine

# initialize pygame and create window
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((constants.WIDTH,constants.HEIGHT),pygame.FULLSCREEN)
pygame.display.set_caption("Practice Game")
clock = pygame.time.Clock()

# Game loop
running = True
while running:
    # keep loop running at the right speed
    clock.tick(constants.FPS)
    # process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.KEYDOWN:
            letter = pygame.key.name(pygame.key.get_pressed().index(1))
            if letter == 'escape':
                running = False
                statemachine.sm.clear_db()
            else:
                statemachine.sm.update_keypressed(letter)

    # Update
    statemachine.sm.update(screen)

    # Draw / render
    statemachine.sm.draw(screen)

    # *after* drawing everything, flip the display
    pygame.display.flip()

pygame.quit()
