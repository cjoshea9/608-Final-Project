import pygame
import constants

pygame.init()


class Username(pygame.sprite.Sprite):
    def __init__(self, screen_dim):
        pygame.sprite.Sprite.__init__(self)
        self.width = screen_dim[0]
        self.height = screen_dim[1]
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.user1 = ""
        self.user2 = ""
        self.title = "CHOOSE YOUR USERNAME PLAYER "
        self.font_type = 'arial'
        self.font_size = 32
        self.user1_done = False
        self.user2_done = False
        self.shift = False

    def update(self):
        self.image.fill(constants.BLACK)
        title_text = self.title
        display_text = ""
        if not self.user1_done:
            title_text += "1"
            display_text += self.user1
        elif not self.user2_done:
            title_text += "2"
            display_text += self.user2
        title = constants.get_text(self.font_type, self.font_size, constants.GREEN, title_text)
        display = constants.get_text(self.font_type, self.font_size, constants.GREEN, display_text)
        self.image.blit(title, (self.width//2 - title.get_width()//2, self.height//3-title.get_height()//2))
        self.image.blit(display, (self.width//2-display.get_width()//2, self.height//2-display.get_height()//2))

    def add_letter(self, letter):
        if not self.user1_done:
            if letter == "backspace":
                if len(self.user1) > 0:
                    self.user1 = self.user1[0:len(self.user1) - 1]
            elif letter == "left shift":
                self.shift = True
            elif letter == "space" and len(self.user1) < 10:
                self.user1 += ' '
            elif letter == "return":
                self.user1_done = True
            elif letter == "up" or letter == "right" or letter == "down" or letter == "left":
                pass
            elif len(letter) == 1 and len(self.user1) < 10:
                if self.shift:
                    letter = letter.upper()
                    self.shift = False
                self.user1 += letter
        elif not self.user2_done:
            if letter == "backspace":
                if len(self.user2) > 0:
                    self.user2 = self.user2[0:len(self.user2) - 1]
            elif letter == "left shift":
                self.shift = True
            elif letter == "space" and len(self.user1) < 10:
                self.user2 += ' '
            elif letter == "return":
                self.user2_done = True
            elif letter == "up" or letter == "right" or letter == "down" or letter == "left":
                pass
            elif len(letter) == 1 and len(self.user1) < 10:
                if self.shift:
                    letter = letter.upper()
                    self.shift = False
                self.user2 += letter


username_sprites = pygame.sprite.Group()
un = Username((constants.WIDTH, constants.HEIGHT))
username_sprites.add(un)
