import pygame
import time
import requests
import username
import controller
import game_selection
import basketball
import shooting_gallery
import high_score
import constants


class StateMachine():
    def __init__(self):
        self.current_game = 'username'
        self.previous_stats = {'game': 'basketball', 'user1_score': 0, 'user2_score': 0}
        self.then = time.time()
        self.p1_name = ""
        self.p2_name = ""
        self.url = "http://608dev.net/sandbox/sc/sacevedo/final_project_test/carnival_server.py"

    def update(self, screen):
        if self.current_game == 'username':
            username.username_sprites.update()

        elif self.current_game == "controller":
            controller.controller_sprites.update()

        elif self.current_game == "game_selection":
            game_selection.game_sel_sprites.update()

        elif self.current_game == "basketball":
            content = [[0,0], [0,0]]
            if (not basketball.bball1.in_motion or not basketball.bball2.in_motion) and basketball.bball_background.time_count % 100 == 0 and not basketball.bball_background.time_over:
                param = {'current_game': 'basketball'}
                r = requests.get(url=self.url, params=param)
                response = str(r.content)[2:len(str(r.content)) - 1]
                response = list(response.split(" "))
                if response[0] != 'Something':
                    for i in range(len(response)):
                        new = [float(val) for val in response[i].split(',')]
                        content[i] = new
            if not basketball.bball1.in_motion:
                basketball.bball1.throw(content[0][0], content[0][1])      # add 10 to whatever is returned from server
            if not basketball.bball2.in_motion:
                basketball.bball2.throw(content[1][0], content[1][1])
            basketball.basketball_sprites.update()

        elif self.current_game == "gallery":
            if shooting_gallery.gallery_background.time_count % 25 == 0 and not shooting_gallery.gallery_background.game_over:
                param = {'current_game': "gallery"}
                r = requests.get(url=self.url, params=param)
                response = str(r.content)[2:len(str(r.content)) - 1]
                content_list = response.split(",")
                for c in content_list:
                    if c != "":
                        content = int(c)
                        if content != -1:
                            if content < 6:
                                shooting_gallery.target1.score_point(content)
                            else:
                                shooting_gallery.target2.score_point(content-6)
            shooting_gallery.shooting_gallery_sprites.update()

        elif self.current_game == "high_score":
            if len(high_score.high_score_bg.current_scores.keys()) == 0:
                current_scores_dict = {'user1': {'username': self.p1_name.upper(), 'score': str(self.previous_stats['user1_score'])},
                                       'user2': {'username': self.p2_name.upper(), 'score': str(self.previous_stats['user2_score'])}}
                high_score.high_score_bg.update_current(current_scores_dict)
                high_score.high_score_bg.start_time = time.time()
                high_score.high_score_bg.screen = screen
            if len(high_score.high_score_bg.high_scores.keys()) == 0:
                param = {'current_game': 'high_score', 'game': self.previous_stats['game']}
                r = requests.get(url=self.url, params=param)
                response = str(r.content)[2:len(str(r.content)) - 1]
                high_scores_dict = dict()
                if len(response) > 0:
                    response_list = response.split(';')
                    for i in range(len(response_list)):
                        values = response_list[i].split(',')
                        if len(values) > 1:
                            high_scores_dict[str(i+1)] = {'username': values[0], 'score': values[1]}
                    high_score.high_score_bg.update_high(high_scores_dict)
            high_score.high_score_sprites.update()

    def draw(self, screen):
        # Draw / render
        screen.fill(constants.BLACK)

        if self.current_game == 'username':
            username.username_sprites.draw(screen)
            if username.un.user1_done and username.un.user2_done:
                self.p1_name = username.un.user1
                self.p2_name = username.un.user2
                self.current_game = "controller"

        elif self.current_game == "controller":
            controller.controller_sprites.draw(screen)
            param = {'current_game': "controller_selection"}
            r = requests.get(url=self.url, params=param)
            controller_num = int(str(r.content)[2:len(str(r.content)) - 1])
            if controller_num == 2:
                self.current_game = "game_selection"
                data = {'current_game':self.current_game, 'game_over':0}
                requests.post(url=self.url, data=data)

        elif self.current_game == "game_selection":
            game_selection.game_sel_sprites.draw(screen)
            self.current_game, difficulty = game_selection.game_sel.next_game()
            if self.current_game != "game_selection":
                data = {"current_game": self.current_game, "game_over": 0}
                if self.current_game == "basketball":
                    for sprite in basketball.basketball_sprites:
                        sprite.new_game(difficulty)
                if self.current_game == "gallery":
                    for sprite in shooting_gallery.shooting_gallery_sprites:
                        sprite.new_game(difficulty)
                    game_selection.game_sel.difficulty = 0
                requests.post(url=self.url, data=data)

        if self.current_game == "basketball":
            basketball.basketball_sprites.draw(screen)
            if basketball.bball_background.game_over:
                if basketball.bball_background.difficulty == 0:
                    game = "basketball_norm"
                else:
                    game = "basketball_hard"
                data = {'current_game': "basketball", "game_over": 1, "user1": self.p1_name, "user2": self.p2_name,
                        "user1_score": basketball.bball1.score, "user2_score": basketball.bball2.score, 'game': game}
                requests.post(url=self.url, data=data)
                self.current_game = "high_score"
                self.previous_stats = {'game': game, 'user1_score': str(basketball.bball1.score), 'user2_score': str(basketball.bball2.score)}

        elif self.current_game == "gallery":
            shooting_gallery.shooting_gallery_sprites.draw(screen)
            if shooting_gallery.gallery_background.game_over:
                if shooting_gallery.target1.difficulty == 0:
                    game = "gallery_easy"
                elif shooting_gallery.target1.difficulty == 1:
                    game = "gallery_med"
                else:
                    game = "gallery_hard"
                data = {'current_game': "gallery", "game_over": 1, "user1": self.p1_name, "user2": self.p2_name,
                        "user1_score": shooting_gallery.target1.score, "user2_score": shooting_gallery.target2.score, "game": game}
                requests.post(url=self.url, data=data)
                self.current_game = "high_score"
                self.previous_stats = {'game': game, 'user1_score': str(shooting_gallery.target1.score),
                                       'user2_score': str(shooting_gallery.target2.score)}

        elif self.current_game == "high_score":
            high_score.high_score_sprites.draw(screen)
            if high_score.high_score_bg.display_over:
                high_score.high_score_bg.reset()
                self.current_game = "game_selection"
                data = {'current_game': self.current_game, 'game_over': 0}
                requests.post(url=self.url, data=data)

    def update_keypressed(self, letter):
        if self.current_game == "username":
            username.un.add_letter(letter)
        elif self.current_game == "game_selection":
            game_selection.game_sel.update_key(letter)

    def clear_db(self):
        high_score.high_score_bg.reset()
        data = {'current_game': self.current_game, 'game_over':1}
        requests.post(url=self.url, data=data)
        self.then = time.time()
        while time.time()-self.then < 1:
            pass
        data = {'current_game': "CLEAR"}
        requests.post(url=self.url, data=data)


sm = StateMachine()
