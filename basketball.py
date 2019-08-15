import pygame
import constants
import time

pygame.init()


class BasketballGoal:
    # draws basketball goal depending on center
    def __init__(self, goal_dim, center_pos):
        self.width = goal_dim[0]
        self.height = goal_dim[1]
        self.center_pos = center_pos
        self.back_board = pygame.Rect(0,0, self.width, self.height)
        self.back_board.center = center_pos
        self.center_board = pygame.Rect(self.back_board.center[0] - self.width/5, self.back_board.center[1] + 10,
                                        self.width/2.5, self.height/2.5)
        self.hoop = pygame.Rect(self.back_board.center[0] - self.width/5, self.back_board.bottom-2,
                                self.width/2.5, self.height/5)
        self.font_type = 'arial'
        self.font_size = 40

    def draw_goal(self, surface, score, center):
        self.back_board.center = center
        self.center_board = pygame.Rect(self.back_board.center[0] - self.width / 5, self.back_board.center[1] + 10,
                                        self.width / 2.5, self.height / 2.5)
        self.hoop = pygame.Rect(self.back_board.center[0] - self.width / 5, self.back_board.bottom - 2,
                                self.width / 2.5, self.height / 5)
        self.draw_board(surface)
        self.draw_hoop(surface)
        score_text = constants.get_text(self.font_type, self.font_size, constants.GREEN, f"SCORE: {score}")
        surface.blit(score_text, (self.center_pos[0] - score_text.get_width()//2, score_text.get_height()//2))

    def draw_board(self, surface):
        pygame.draw.rect(surface, constants.BLUE, self.center_board, 4)
        pygame.draw.rect(surface, constants.BLUE, self.back_board, 5)

    def draw_hoop(self, surface):
        pygame.draw.ellipse(surface, constants.RED, self.hoop, 5)

    def draw_point(self, surface):
        score_text = constants.get_text(self.font_type, self.font_size, constants.GREEN, 'DUNKED!')
        surface.blit(score_text, (self.center_board.right + score_text.get_width()//2, self.center_board.bottom))
        score_text_rect = score_text.get_rect()
        score_text_rect.center = (self.center_board.right + score_text.get_width(), self.center_board.bottom + score_text.get_height()/2)
        score_text_rect = score_text_rect.inflate(30,30)
        pygame.draw.ellipse(surface, constants.GREEN, score_text_rect, 7)


class BasketballBackground(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height):
        pygame.sprite.Sprite.__init__(self)
        self.WIDTH = screen_width
        self.HEIGHT = screen_height
        self.goal_dim = (self.WIDTH/4, self.HEIGHT/4)
        self.image = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect()

        self.goal1_score = 0
        self.p1_section = pygame.Rect(0,0,self.WIDTH/2,self.HEIGHT)
        self.goal1_center = (self.WIDTH / 3-self.goal_dim[0]/3, self.HEIGHT / 2)
        self.goal1 = BasketballGoal(self.goal_dim, self.goal1_center)
        self.goal1.draw_goal(self.image, self.goal1_score, self.goal1_center)

        self.goal2_score = 0
        self.p2_section = pygame.Rect(self.WIDTH/2, 0, self.WIDTH / 2, self.HEIGHT)
        self.goal2_center = (self.WIDTH / 3 * 2 + self.goal_dim[0] / 3, self.HEIGHT / 2)
        self.goal2 = BasketballGoal(self.goal_dim, self.goal2_center)
        self.goal2.draw_goal(self.image, self.goal2_score, self.goal2_center)

        self.time_count = 0
        self.time_over = False
        self.game_over = False
        self.game_duration = 30
        self.start_time = time.time()
        self.elapsed_time = int(time.time() - self.start_time)
        self.font_type = 'arial'
        self.font_size = 80
        self.difficulty = 0
        if self.difficulty == 0:
            self.goal1_vel = 0
            self.goal2_vel = 0
        else:
            self.goal1_vel = 5
            self.goal2_vel = -5

    def new_game(self, difficulty):
        self.time_count = 0
        self.time_over = False
        self.game_over = False
        self.start_time = time.time()
        self.elapsed_time = int(time.time() - self.start_time)
        self.difficulty = difficulty
        if self.difficulty == 0:
            self.goal1_vel = 0
            self.goal2_vel = 0
        else:
            self.goal1_vel = 5
            self.goal2_vel = -5
        self.goal1_center = (self.WIDTH / 3 - self.goal_dim[0] / 3, self.HEIGHT / 2)
        self.goal2_center = (self.WIDTH / 3 * 2 + self.goal_dim[0] / 3, self.HEIGHT / 2)

    def update(self):
            self.image.fill(constants.BLACK)
            self.image.set_colorkey(constants.BLACK)
            self.time_count += 1
            self.elapsed_time = int(time.time() - self.start_time)
            self.goal1_score = bball1.score
            self.goal2_score = bball2.score

            self.goal1_center = (self.goal1_center[0] + self.goal1_vel, self.goal1_center[1])
            if self.goal1.back_board.right + self.goal1_vel > self.WIDTH//2 or self.goal1.back_board.left + self.goal1_vel < 0:
                self.goal1_vel = -self.goal1_vel
            self.goal1.draw_goal(self.image, self.goal1_score, self.goal1_center)

            self.goal2_center = (self.goal2_center[0] + self.goal2_vel, self.goal2_center[1])
            if self.goal2.back_board.left + self.goal2_vel < self.WIDTH//2 or self.goal2.back_board.right + self.goal2_vel > self.WIDTH:
                self.goal2_vel = -self.goal2_vel
            self.goal2.draw_goal(self.image, self.goal2_score, self.goal2_center)

            if self.game_duration - self.elapsed_time >= 0:
                time_text = constants.get_text(self.font_type, self.font_size, constants.GREEN, f"{self.game_duration - self.elapsed_time}")
                self.image.blit(time_text, (self.WIDTH//2 - time_text.get_width()//2, time_text.get_height()//2))
            else:
                time_text = constants.get_text(self.font_type, self.font_size, constants.GREEN, "0")
                self.image.blit(time_text, (self.WIDTH // 2 - time_text.get_width() // 2, time_text.get_height() // 2))
            pygame.draw.line(self.image, constants.RED, (self.WIDTH // 2,time_text.get_rect().bottom + time_text.get_height()),
                             (self.WIDTH // 2, self.HEIGHT), 2)
            if self.game_duration - self.elapsed_time < 0:
                self.time_over = True
                if not bball1.in_motion and not bball2.in_motion:
                    self.game_over = True

    def clear_section(self, player_num):
        if player_num == 1:
            self.goal1.draw_goal(self.image, bball1.score, self.goal1_center)
        else:
            self.goal2.draw_goal(self.image, bball2.score, self.goal2_center)


class Basketball(pygame.sprite.Sprite):
    def __init__(self, background, dt, player_number, mass = 1):
        pygame.sprite.Sprite.__init__(self)
        self.player_num = player_number
        self.background = background
        self.initial_radius = self.background.rect.height//10
        self.radius = self.background.rect.height//10
        self.color = constants.ORANGE
        self.TOP_LIMIT = self.background.rect.top
        self.BOTTOM_LIMIT = self.background.rect.bottom
        if player_number == 1:
            self.LEFT_LIMIT = self.background.rect.left
            self.RIGHT_LIMIT = self.background.rect.right/2
            self.goal = self.background.goal1
        else:
            self.LEFT_LIMIT = self.background.rect.right/2

            self.RIGHT_LIMIT = self.background.rect.right
            self.goal = self.background.goal2
        self.initial_center = ((self.RIGHT_LIMIT-self.LEFT_LIMIT)/2 + self.LEFT_LIMIT, self.BOTTOM_LIMIT + self.radius)

        self.image = pygame.Surface((self.radius*2, self.radius*2))
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = self.initial_center

        self.in_motion = False
        self.x_pos = self.rect.center[0]
        self.y_pos = self.rect.center[1]
        self.x_vel = 0
        self.y_vel = 0
        self.x_accel = 0
        self.y_accel = 0
        self.GRAVITY = 20
        self.DT = dt
        self.MASS = mass
        self.time_count = 0
        self.score = 0
        self.is_scored = False
        self.over_board = False

    def reset(self):
        self.image = pygame.Surface((self.radius * 2, self.radius * 2))
        self.image.set_colorkey(constants.BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = self.initial_center
        self.x_pos = self.rect.center[0]
        self.y_pos = self.rect.center[1]
        self.radius = self.initial_radius
        self.x_vel = 0
        self.y_vel = 0
        self.x_accel = 0
        self.y_accel = 0
        self.in_motion = False
        self.is_scored = False
        self.over_board = False
        self.background.clear_section(self.player_num)

    def new_game(self,difficulty):
        self.reset()
        self.score = 0

    def throw(self, x_force=0, y_force=0):
        # y_accel good throw is 10
        # x_accel good throw is 2.5

        self.in_motion = True
        self.rect.center = (self.initial_center[0], self.initial_center[1]-self.radius/2)
        self.x_accel = (30*x_force)/self.MASS
        self.y_accel = 2*self.GRAVITY - 200*y_force/self.MASS
        self.moveBall()

    def update(self,new_game=False):
        if new_game:
            self.new_game(None)
        pygame.draw.circle(self.image, constants.BLACK, (self.rect.width // 2, self.rect.height // 2), self.radius)
        if not self.background.game_over and self.in_motion:
            self.throw()

    def getX(self):
        return self.x_pos

    def getY(self):
        return self.y_pos

    def moveBall(self):
        self.time_count += 1
        if self.time_count % 3 == 0 and self.radius - 1 > 0:
            self.radius -= 1
            self.image = pygame.transform.scale(self.image, (self.radius*2, self.radius*2))
            self.rect = self.image.get_rect()

        self.x_vel += 10*self.DT*self.x_accel
        self.y_vel += 10*self.DT*self.y_accel

        self.x_pos += self.DT*self.x_vel
        self.y_pos += self.DT*self.y_vel

        self.rect.center = (self.x_pos, self.y_pos)

        if self.y_vel > 0:
            if self.rect.top > self.BOTTOM_LIMIT:
                self.in_motion = False
                if self.is_scored:
                    self.score += 1
                self.reset()
            elif not self.over_board and self.goal.center_board.left < self.rect.center[0] < self.goal.center_board.right:
                if self.goal.center_board.top < self.rect.center[1] < self.goal.hoop.bottom:
                    if self.radius < self.initial_radius/2 - self.initial_radius/8:
                        self.is_scored = True
                        print("SCORED")

            if self.radius < 20 and self.rect.bottom >= self.goal.back_board.top and not self.is_scored:
                if self.rect.left < self.goal.back_board.right or self.rect.right > self.goal.back_board.left:
                    self.over_board = True

        if self.over_board:
            pygame.draw.circle(self.image, constants.BLACK, (self.rect.width // 2, self.rect.height // 2), self.radius)
        else:
            pygame.draw.circle(self.image, self.color, (self.rect.width // 2, self.rect.height // 2), self.radius)
            if self.is_scored and self.rect.bottom > self.goal.hoop.top:
                self.goal.draw_point(self.background.image)


basketball_sprites = pygame.sprite.Group()
bball_background = BasketballBackground(constants.WIDTH, constants.HEIGHT)
bball1 = Basketball(bball_background, constants.PERIOD,1)
bball2 = Basketball(bball_background, constants.PERIOD,2)
basketball_sprites.add(bball_background)
basketball_sprites.add(bball1)
basketball_sprites.add(bball2)


