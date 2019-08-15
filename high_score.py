import pygame
import constants
import time


class HighscoreBackground(pygame.sprite.Sprite):
    def __init__(self, screen_dim):
        self.screen = None
        pygame.sprite.Sprite.__init__(self)
        self.width = screen_dim[0]
        self.height = screen_dim[1]
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.high_scores = dict()
        self.current_scores = dict()
        self.start_time = 0
        self.display_time = 8
        self.display_over = False

        self.game_over_text = "GAME OVER"
        self.high_score_title_text = "HIGH SCORES"
        self.high_score_labels_text = "RANK     USERNAME     SCORE"

        self.font_super = 100
        self.font_big = 80
        self.font_med = 60
        self.font_small = 50
        self.font_type = 'arial'

        self.game_over = constants.get_text(self.font_type, self.font_super, constants.RED, self.game_over_text)
        self.high_score_title = constants.get_text(self.font_type, self.font_big, constants.GREEN, self.high_score_title_text)
        self.high_score_labels = constants.get_text(self.font_type, self.font_med, constants.GREEN, self.high_score_labels_text)


    def reset(self):
        self.display_over = False
        self.high_scores = dict()
        self.current_scores = dict()

    def update(self):
        if self.display_over:
            return
        if time.time() - self.start_time > self.display_time:
            self.display_over = True

        self.image.fill(constants.BLACK)
        user1_score_text = self.current_scores['user1']['username'] + "'S SCORE: " + self.current_scores['user1']['score']
        user2_score_text = self.current_scores['user2']['username'] + "'S SCORE: " + self.current_scores['user2']['score']
        user1_score = constants.get_text(self.font_type, self.font_med, constants.GREEN, user1_score_text)
        user2_score = constants.get_text(self.font_type, self.font_med, constants.GREEN, user2_score_text)

        for i in range(len(self.high_scores.keys())):
            rank = str(i + 1)
            username = self.high_scores[rank]['username'].upper()
            score = self.high_scores[rank]['score']
            if int(score) < 10:
                score += " "
            high_score_name = f"{rank}            {username}"
            high_score_val = score
            high_score = constants.get_text(self.font_type, self.font_small, constants.GREEN, high_score_name)
            high_score_val = constants.get_text(self.font_type, self.font_small, constants.GREEN, high_score_val)
            self.image.blit(high_score,
                            (self.width//2 - 310,
                             9 * self.height//16 + i*self.height//12 - high_score.get_height()//2))
            self.image.blit(high_score_val,
                            (self.width // 2 + 290 - high_score_val.get_width()//2,
                             9 * self.height // 16 + i * self.height // 12 - high_score.get_height() // 2))

        self.image.blit(self.game_over,
                        (self.width // 2 - self.game_over.get_width() // 2,
                         self.game_over.get_height()//2))
        self.image.blit(self.high_score_title,
                        (self.width // 2 - self.high_score_title.get_width() // 2,
                         3 * self.height//8 - self.high_score_title.get_height() // 2))
        self.image.blit(self.high_score_labels,
                        (self.width // 2 - self.high_score_labels.get_width() // 2,
                         self.height // 2 - self.high_score_labels.get_height() // 2))

        self.image.blit(user1_score,
                        (3 * self.width // 16 - user1_score.get_width()//2,
                         self.height // 4 - user1_score.get_height() // 2))
        self.image.blit(user2_score,
                        (13 * self.width // 16 - user2_score.get_width()//2,
                         self.height // 4 - user2_score.get_height() // 2))

        # self.image.blit(high_score1,
        #                 (self.width // 4 - high_score1.get_width(),
        #                  5 * self.height // 8 - high_score1.get_height() // 2))
        # self.image.blit(high_score2,
        #                 (3 * self.width // 4 - high_score2.get_width(),
        #                  5 * self.height // 8 - high_score2.get_height() // 2))

    def update_current(self, current_dict):
        self.current_scores = current_dict

    def update_high(self, high_dict):
        self.high_scores = high_dict


high_score_sprites = pygame.sprite.Group()
high_score_bg = HighscoreBackground((constants.WIDTH, constants.HEIGHT))
high_score_sprites.add(high_score_bg)





