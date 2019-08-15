import pygame
import random
import constants
import time

pygame.init()


class GalleryBackground(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        pygame.sprite.Sprite.__init__(self)
        self.WIDTH = screen_width
        self.HEIGHT = screen_height
        self.image = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect()

        self.font_type = 'arial'
        self.font_big = 100
        self.font_norm = 50

        self.time_count = 0
        self.game_over = False
        self.game_duration = 30
        self.start_time = time.time()
        self.elapsed_time = int(time.time() - self.start_time)
        self.target1_score = target1.score
        self.target2_score = target2.score

    def new_game(self, difficulty):
        self.time_count = 0
        self.game_over = False
        self.start_time = time.time()
        self.elapsed_time = int(time.time() - self.start_time)

    def update(self):
        self.image.fill(constants.BLACK)
        self.image.set_colorkey(constants.BLACK)
        self.time_count += 1
        self.elapsed_time = int(time.time() - self.start_time)
        self.target1_score = target1.score
        self.target2_score = target2.score
        score_text = constants.get_text(self.font_type, self.font_norm, constants.GREEN,
                                        f"SCORE: {self.target1_score}              SCORE: {self.target2_score}")
        self.image.blit(score_text,
                        (self.WIDTH // 2 - score_text.get_width() // 2, self.HEIGHT//2 - score_text.get_height() // 2))

        if self.game_duration - self.elapsed_time >= 0:
            time_text = constants.get_text(self.font_type, self.font_big, constants.GREEN,
                                           f"{self.game_duration - self.elapsed_time}")
            self.image.blit(time_text,
                            (self.WIDTH // 2 - time_text.get_width() // 2, self.HEIGHT//2 - time_text.get_height() // 2))
        else:
            time_text = constants.get_text(self.font_type, self.font_big, constants.GREEN, "0")
            self.image.blit(time_text,
                            (self.WIDTH // 2 - time_text.get_width() // 2, self.HEIGHT//2 - time_text.get_height() // 2))
        if self.game_duration - self.elapsed_time < 0:
            self.game_over = True


class Target(pygame.sprite.Sprite):
    def __init__(self, screen_dim, all_pos, player_num, color1, color2):
        pygame.sprite.Sprite.__init__(self)
        self.screen_dim = screen_dim
        self.player_num = player_num
        self.all_pos = all_pos
        self.current_pos = self.all_pos[int(random.randrange(len(self.all_pos)))]
        self.target_num = self.all_pos.index(self.current_pos)
        self.image = pygame.Surface((self.screen_dim[1]//5, self.screen_dim[1]//5))
        self.rect = self.image.get_rect()
        self.rect.center = (self.current_pos[0], self.current_pos[1])
        self.score = 0
        self.is_scored = False
        self.color1 = color1
        self.color2 = color2
        self.target_time = time.time()
        self.next = False
        self.difficulty = 0
        self.easy_duration = 5
        self.med_duration = 3
        self.hard_duration = 1.5
        self.target_duration = self.easy_duration

    def next_target(self):
        new_pos = self.all_pos[random.randrange(len(self.all_pos))]
        while new_pos == self.current_pos:
            new_pos = self.all_pos[random.randrange(len(self.all_pos))]
        self.current_pos = new_pos
        self.target_num = self.all_pos.index(self.current_pos)
        self.target_time = time.time()

    def draw_target(self, color1, color2):
        pygame.draw.circle(self.image, color1, (self.rect.width//2, self.rect.height//2), self.rect.height//2)
        pygame.draw.circle(self.image, color2,(self.rect.width//2, self.rect.height//2), 3 * self.rect.height//8, 35)

    def draw_broken_target(self, color1, color2):
        self.draw_target(color1, color2)
        pygame.draw.line(self.image,constants.BLACK, (0, self.rect.height//2),
                         (self.rect.width, self.rect.height//2), 15)
        pygame.draw.line(self.image, constants.BLACK, (self.rect.width//2, 0),
                         (self.rect.width//2, self.rect.height), 15)

    def new_game(self, difficulty):
        self.next_target()
        self.score = 0
        self.is_scored = False
        self.difficulty = difficulty
        if self.difficulty == 0:
            self.target_duration = self.easy_duration
        elif self.difficulty == 1:
            self.target_duration = self.med_duration
        else:
            self.target_duration = self.hard_duration

    def score_point(self, target_hit):
        print("IT HIT", target_hit, self.player_num)
        if self.target_num == target_hit:
            print("IT SCORED")
            self.score += 1
            self.is_scored = True
            self.draw_target(self.color1, self.color2)

    def update(self):
        if self.is_scored:
            self.next = True
            self.is_scored = False
        elif time.time() - self.target_time >= self.target_duration or self.next:
            self.next_target()
            self.next = False
        self.rect.center = (self.current_pos[0], self.current_pos[1])
        if self.next:
            self.draw_broken_target(self.color1, self.color2)
        else:
            self.draw_target(self.color1, self.color2)


shooting_gallery_sprites = pygame.sprite.Group()
target1 = Target((constants.WIDTH, constants.HEIGHT), constants.target1_loc, 1, constants.RED,constants.WHITE)
target2 = Target((constants.WIDTH, constants.HEIGHT), constants.target2_loc, 2, constants.RED,constants.WHITE)
gallery_background = GalleryBackground(constants.WIDTH, constants.HEIGHT)
shooting_gallery_sprites.add(gallery_background)
shooting_gallery_sprites.add(target1)
shooting_gallery_sprites.add(target2)



