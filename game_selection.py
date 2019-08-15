import pygame
import constants


class GameSel(pygame.sprite.Sprite):
    def __init__(self, bounds):
        pygame.sprite.Sprite.__init__(self)
        self.width = bounds[0]
        self.height = bounds[1]
        self.bounds = (self.width, self.height)
        self.image = pygame.Surface(self.bounds)
        self.rect = self.image.get_rect()
        self.hover = 0
        self.difficulty = 0
        self.selected = "game_selection"
        self.title = "CHOOSE YOUR GAME"
        self.game_choice0 = "Basketball"
        self.game_choice1 = "Shooting Gallery"
        self.bball_diff_choice0 = "Normal"
        self.bball_diff_choice1 = "Hard"
        self.gal_diff_choice0 = "Easy"
        self.gal_diff_choice1 = "Medium"
        self.gal_diff_choice2 = "Hard"
        self.font_type = 'arial'
        self.font_small = 45
        self.font_big = 60

    def update(self):
        self.image.fill(constants.BLACK)
        title = constants.get_text(self.font_type, self.font_big, constants.GREEN, self.title)
        if self.hover == 0:
            game_choice0 = constants.get_text(self.font_type, self.font_big, constants.RED, self.game_choice0)
            game_choice1 = constants.get_text(self.font_type, self.font_small, constants.GREEN, self.game_choice1)
            gal_diff_choice0 = constants.get_text(self.font_type, self.font_small, constants.BLACK, self.gal_diff_choice0)
            gal_diff_choice1 = constants.get_text(self.font_type, self.font_small, constants.BLACK, self.gal_diff_choice1)
            gal_diff_choice2 = constants.get_text(self.font_type, self.font_small, constants.BLACK, self.gal_diff_choice2)
            if self.difficulty == 0:
                bball_diff_choice0 = constants.get_text(self.font_type, self.font_small, constants.RED,
                                                      self.bball_diff_choice0)
                bball_diff_choice1 = constants.get_text(self.font_type, self.font_small, constants.GREEN,
                                                      self.bball_diff_choice1)
            else:
                bball_diff_choice0 = constants.get_text(self.font_type, self.font_small, constants.GREEN,
                                                        self.bball_diff_choice0)
                bball_diff_choice1 = constants.get_text(self.font_type, self.font_small, constants.RED,
                                                        self.bball_diff_choice1)
        else:
            game_choice0 = constants.get_text(self.font_type, self.font_small, constants.GREEN, self.game_choice0)
            game_choice1 = constants.get_text(self.font_type, self.font_big, constants.RED, self.game_choice1)
            if self.difficulty == 0:
                gal_diff_choice0 = constants.get_text(self.font_type, self.font_small, constants.RED, self.gal_diff_choice0)
                gal_diff_choice1 = constants.get_text(self.font_type, self.font_small, constants.GREEN, self.gal_diff_choice1)
                gal_diff_choice2 = constants.get_text(self.font_type, self.font_small, constants.GREEN, self.gal_diff_choice2)
            elif self.difficulty == 1:
                gal_diff_choice0 = constants.get_text(self.font_type, self.font_small, constants.GREEN, self.gal_diff_choice0)
                gal_diff_choice1 = constants.get_text(self.font_type, self.font_small, constants.RED, self.gal_diff_choice1)
                gal_diff_choice2 = constants.get_text(self.font_type, self.font_small, constants.GREEN, self.gal_diff_choice2)
            else:
                gal_diff_choice0 = constants.get_text(self.font_type, self.font_small, constants.GREEN, self.gal_diff_choice0)
                gal_diff_choice1 = constants.get_text(self.font_type, self.font_small, constants.GREEN, self.gal_diff_choice1)
                gal_diff_choice2 = constants.get_text(self.font_type, self.font_small, constants.RED, self.gal_diff_choice2)
            bball_diff_choice0 = constants.get_text(self.font_type, self.font_small, constants.BLACK,
                                                    self.bball_diff_choice0)
            bball_diff_choice1 = constants.get_text(self.font_type, self.font_small, constants.BLACK,
                                                    self.bball_diff_choice1)

        self.image.blit(title, (self.width//2 - title.get_width()//2,
                                self.height//4 - title.get_height()//2))
        self.image.blit(game_choice0, (self.width//2 - game_choice0.get_width()//2,
                                       self.height//2 - game_choice0.get_height()//2))
        self.image.blit(game_choice1, (self.width//2 - game_choice1.get_width()//2,
                                       self.height * 3//4 - game_choice1.get_height()//2))
        self.image.blit(gal_diff_choice0, (5 * self.width // 8 + game_choice1.get_width()//4 - gal_diff_choice0.get_width() // 2,
                                       self.height * 3 // 4 - gal_diff_choice0.get_height() // 2))
        self.image.blit(gal_diff_choice1, (3 * self.width // 4 + game_choice1.get_width()//4 - gal_diff_choice1.get_width() // 2,
                                       self.height * 3 // 4 - gal_diff_choice1.get_height() // 2))
        self.image.blit(gal_diff_choice2, (7 * self.width // 8 + game_choice1.get_width()//4 - gal_diff_choice2.get_width() // 2,
                                       self.height * 3 // 4 - gal_diff_choice2.get_height() // 2))
        self.image.blit(bball_diff_choice0, (5 * self.width // 8 + game_choice0.get_width()//4 - bball_diff_choice0.get_width() // 2,
                                             self.height//2 - bball_diff_choice0.get_height()//2))
        self.image.blit(bball_diff_choice1, (3 * self.width // 4 + game_choice1.get_width() // 4 - bball_diff_choice1.get_width() // 2,
                                             self.height // 2 - bball_diff_choice1.get_height() // 2))

    def next_game(self):
        selected = self.selected
        difficulty = self.difficulty
        self.selected = "game_selection"
        return selected, difficulty

    def update_key(self, key):
        if key == "return":
            if self.hover == 0:
                self.selected = "basketball"
            else:
                self.selected = "gallery"

        elif key == "up":
            self.hover = (self.hover - 1) % 2
            self.difficulty = 0
        elif key == "down":
            self.hover = (self.hover + 1) % 2
            self.difficulty = 0
        elif key == "left":
            if self.hover == 0:
                self.difficulty = (self.difficulty - 1) % 2
            else:
                self.difficulty = (self.difficulty - 1) % 3
        elif key == "right":
            if self.hover == 0:
                self.difficulty = (self.difficulty + 1) % 2
            else:
                self.difficulty = (self.difficulty + 1) % 3



game_sel_sprites = pygame.sprite.Group()
game_sel = GameSel((constants.WIDTH, constants.HEIGHT))
game_sel_sprites.add(game_sel)

