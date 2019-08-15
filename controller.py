import pygame
import constants


class ControllerBackground(pygame.sprite.Sprite):
    def __init__(self, screen_dim):
        pygame.sprite.Sprite.__init__(self)
        self.width = screen_dim[0]
        self.height = screen_dim[1]
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.title_text = "CONTROLLER SELECTION"
        self.sub_text = "PLAYER 1 PRESS YOUR LEFT BUTTON                                                  PLAYER 2 PRESS YOUR RIGHT BUTTON"
        self.font_type = 'arial'
        self.font_big = 100
        self.font_norm = 35
        self.title = constants.get_text(self.font_type, self.font_big, constants.GREEN, self.title_text)
        self.sub = constants.get_text(self.font_type, self.font_norm, constants.GREEN, self.sub_text)
        self.image.blit(self.title,
                        (self.width//2-self.title.get_width()//2, self.height//4-self.title.get_height()//2))
        self.image.blit(self.sub, (self.width//2-self.sub.get_width()//2, self.height//2-self.sub.get_height()//2))


controller_sprites = pygame.sprite.Group()
con_bg = ControllerBackground((constants.WIDTH,constants.HEIGHT))
controller_sprites.add(con_bg)


