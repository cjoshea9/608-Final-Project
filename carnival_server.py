import sqlite3
import datetime

basketball_db = '__HOME__/final_project_test/carnival_basketball.db'
gallery_db = '__HOME__/final_project_test/carnival_gallery.db'
target_hit_db = '__HOME__/final_project_test/test_hit.db'
game_db = '__HOME__/final_project_test/game.db'
controller_db = '__HOME__/final_project_test/controller.db'
high_score_db = '__HOME__/final_project_test/high_score.db'


def request_handler(req):
    create_all_databases()
    if req['method'] == 'POST':
        if req['form']['current_game'] != "CLEAR":
            update_game_db(req)
            if "user1_score" in req['form']:
                update_high_score_db(req)
            elif req['form']['current_game'] == 'basketball':
                update_bball_db(req)
            elif req['form']['current_game'] == 'gallery':
                update_gallery_db(req)
            elif req['form']['current_game'] == 'controller_selection':
                return update_controller_db(req)
        else:
            clear_all_db()
    elif req['method'] == 'GET':
        if req['values']['current_game'] == "basketball":
            return basketball_get()
        elif req['values']['current_game'] == 'gallery':
            return gallery_get()
        elif req['values']['current_game'] == 'current_game':
            return game_get()
        elif req['values']['current_game'] == 'controller_selection':
            return controller_get()
        elif req['values']['current_game'] == 'high_score':
            return high_score_get(req)


def update_gallery_db(req):
    target = int(req['form']['target'])

    conn = sqlite3.connect(gallery_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)
    c.execute('''INSERT into gallery_data VALUES (?,?);''', (target, datetime.datetime.now()))
    conn.commit()  # commit commands
    conn.close()  # close connection to database


def gallery_get():
    one_second_ago = datetime.datetime.now() - datetime.timedelta(
        seconds=5)
    conn = sqlite3.connect(gallery_db)
    c = conn.cursor()
    target1 = c.execute(
        '''SELECT DISTINCT target FROM gallery_data WHERE post_time > ? AND target < 6 ORDER BY post_time DESC LIMIT 1;''',
        (one_second_ago,)).fetchall()
    target2 = c.execute(
        '''SELECT DISTINCT target FROM gallery_data WHERE post_time > ? AND target >= 6 ORDER BY post_time DESC LIMIT 1;''',
        (one_second_ago,)).fetchall()
    conn.commit()
    conn.close()
    if len(target1) > 0 or len(target2) > 0:
        final = ""
        if len(target1) > 0:
            final += str(target1[0][0]) + ","
        if len(target2) > 0:
            final += str(target2[0][0]) + ","
        return final
    else:
        return "-1,"


def update_controller_db(req):
    player_num = int(req['form']['player_num'])

    conn = sqlite3.connect(controller_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)

    c.execute('''INSERT into controller_data VALUES (?,?);''', (player_num, datetime.datetime.now()))
    things = c.execute(
        '''SELECT player_num FROM controller_data GROUP BY player_num LIMIT 2 ;''', ).fetchall()
    final = len(things)
    conn.commit()  # commit commands
    conn.close()  # close connection to database
    return final


def controller_get():
    twenty_second_ago = datetime.datetime.now() - datetime.timedelta(
        seconds=20)
    conn = sqlite3.connect(controller_db)
    c = conn.cursor()
    things = c.execute(
        '''SELECT player_num FROM controller_data WHERE post_time > ? GROUP BY player_num ORDER BY post_time DESC LIMIT 2;''', (twenty_second_ago,)).fetchall()
    final = len(things)
    conn.commit()
    conn.close()
    return final


def update_bball_db(req):
    z_acc = float(req['form']['z_acc'])
    x_acc= float(req['form']['x_acc'])
    player_num = req['form']['player_num']
    
    conn = sqlite3.connect(basketball_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)

    c.execute('''CREATE TABLE IF NOT EXISTS basketball_data (z_acc float, x_acc float, player_num text, post_time timestamp);''') # run a CREATE TABLE command
    c.execute('''INSERT into basketball_data VALUES (?,?,?,?);''', (z_acc,x_acc,player_num,datetime.datetime.now()))

    conn.commit() # commit commands
    conn.close() # close connection to database


def basketball_get():
    bball_throws = ""
    two_second_ago = datetime.datetime.now() - datetime.timedelta(
        seconds=2)
    conn = sqlite3.connect(basketball_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)

    things = c.execute('''SELECT player_num, x_acc, z_acc FROM basketball_data WHERE post_time > ? GROUP BY player_num ORDER BY post_time DESC LIMIT 2;''', (two_second_ago,)).fetchall()

    if len(things) == 0:
        bball_throws = "0,0 0,0"
    for i in range(len(things)):
        ball_throw = things[i]
        if i == 0 and int(ball_throw[0]) == 2 and len(things) == 1:
            bball_throws = "0,0 "
        bball_throws += str(ball_throw[1]) + ',' + str(ball_throw[2]) + " "
        if i == 0 and int(ball_throw[0]) == 1 and len(things) == 1:
            bball_throws += "0,0"

    conn.commit()  # commit commands
    conn.close()  # close connection to database
    return bball_throws


def update_game_db(req):
    game = req['form']['current_game']
    game_over = int(req['form']['game_over'])
    conn = sqlite3.connect(game_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)
    c.execute('''INSERT into game_data VALUES (?,?,?);''', (game, game_over, datetime.datetime.now()))
    conn.commit()  # commit commands
    conn.close()  # close connection to database


def game_get():
    conn = sqlite3.connect(game_db)
    c = conn.cursor()
    things = c.execute(
        '''SELECT current_game, game_over FROM game_data ORDER BY post_time DESC LIMIT 1 ;''',).fetchall()
    conn.commit()
    conn.close()
    final = None
    if len(things) > 0:
        final = f'{things[0][0]} {things[0][1]}'
    return final


def update_high_score_db(req):
    game = req['form']['game']
    user1 = req['form']['user1']
    user1_score = int(req['form']['user1_score'])
    user2 = req['form']['user2']
    user2_score = int(req['form']['user2_score'])
    final_scores = {user1: {'basketball_norm': 0, "basketball_hard": 0,
                            'gallery_easy': 0, 'gallery_med': 0, 'gallery_hard': 0},
                    user2: {'basketball_norm': 0, "basketball_hard": 0,
                            'gallery_easy': 0, 'gallery_med': 0, 'gallery_hard': 0}}

    conn = sqlite3.connect(high_score_db)   # check what are the current high scores for each player
    c = conn.cursor()
    user1_stats = c.execute(
        '''SELECT basketball_score_norm, basketball_score_hard,
         gallery_score_easy, gallery_score_med, gallery_score_hard FROM high_score_data WHERE username = ? ORDER BY post_time DESC LIMIT 1 ;''',
        (user1,)).fetchall()
    user2_stats = c.execute(
        '''SELECT basketball_score_norm, basketball_score_hard,
         gallery_score_easy, gallery_score_med, gallery_score_hard FROM high_score_data WHERE username = ? ORDER BY post_time DESC LIMIT 1 ;''',
        (user2,)).fetchall()
    conn.commit()
    conn.close()

    if len(user1_stats) > 0:
        final_scores[user1]['basketball_norm'] = user1_stats[0][0]
        final_scores[user1]['basketball_hard'] = user1_stats[0][1]
        final_scores[user1]['gallery_easy'] = user1_stats[0][2]
        final_scores[user1]['gallery_med'] = user1_stats[0][3]
        final_scores[user1]['gallery_hard'] = user1_stats[0][4]
    if len(user2_stats) > 0:
        final_scores[user2]['basketball_norm'] = user2_stats[0][0]
        final_scores[user2]['basketball_hard'] = user2_stats[0][1]
        final_scores[user2]['gallery_easy'] = user2_stats[0][2]
        final_scores[user2]['gallery_med'] = user2_stats[0][3]
        final_scores[user2]['gallery_hard'] = user2_stats[0][4]
    if user1_score > final_scores[user1][game]:
        final_scores[user1][game] = user1_score
    if user2_score > final_scores[user2][game]:
        final_scores[user2][game] = user2_score

    conn = sqlite3.connect(high_score_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)
    c.execute('''INSERT into high_score_data VALUES (?,?,?,?,?,?,?);''', (user1,
                                                                    final_scores[user1]['basketball_norm'],
                                                                    final_scores[user1]['basketball_hard'],
                                                                    final_scores[user1]['gallery_easy'],
                                                                    final_scores[user1]['gallery_med'],
                                                                    final_scores[user1]['gallery_hard'],
                                                                    datetime.datetime.now()))

    c.execute('''INSERT into high_score_data VALUES (?,?,?,?,?,?,?);''', (user2,
                                                                    final_scores[user2]['basketball_norm'],
                                                                    final_scores[user2]['basketball_hard'],
                                                                    final_scores[user2]['gallery_easy'],
                                                                    final_scores[user2]['gallery_med'],
                                                                    final_scores[user2]['gallery_hard'],
                                                                    datetime.datetime.now()))
    conn.commit()  # commit commands
    conn.close()  # close connection to database


def high_score_get(req):
    game = req['values']['game']
    conn = sqlite3.connect(high_score_db)
    c = conn.cursor()
    if game == "basketball_norm":
        high_scores = c.execute(
            '''SELECT username, basketball_score_norm FROM high_score_data GROUP BY username ORDER BY basketball_score_norm DESC, post_time DESC LIMIT 5 ;''',).fetchall()
    elif game == "basketball_hard":
        high_scores = c.execute(
            '''SELECT username, basketball_score_hard FROM high_score_data GROUP BY username ORDER BY basketball_score_hard DESC, post_time DESC LIMIT 5 ;''', ).fetchall()
    elif game == "gallery_easy":
        high_scores = c.execute(
            '''SELECT username, gallery_score_easy FROM high_score_data GROUP BY username ORDER BY gallery_score_easy DESC, post_time DESC LIMIT 5 ;''', ).fetchall()
    elif game == "gallery_med":
        high_scores = c.execute(
            '''SELECT username, gallery_score_med FROM high_score_data GROUP BY username ORDER BY gallery_score_med DESC, post_time DESC LIMIT 5 ;''', ).fetchall()
    elif game == "gallery_hard":
        high_scores = c.execute(
            '''SELECT username, gallery_score_hard FROM high_score_data GROUP BY username ORDER BY gallery_score_hard DESC, post_time DESC LIMIT 5 ;''', ).fetchall()

    conn.commit()
    conn.close()
    final = ""
    for entry in high_scores:
        final += f"{entry[0]},{entry[1]};"
    return final


def clear_all_db():
    conn = sqlite3.connect(basketball_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)
    c.execute(
        '''DELETE FROM basketball_data;''')  # run a DELETE command
    conn.commit()  # commit commands
    conn.close()  # close connection to database

    conn = sqlite3.connect(gallery_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)
    c.execute(
        '''DELETE FROM gallery_data;''')  # run a DELETE command
    conn.commit()  # commit commands
    conn.close()  # close connection to database

    conn = sqlite3.connect(game_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)
    c.execute(
        '''DELETE FROM game_data;''')  # run a DELETE command
    conn.commit()  # commit commands
    conn.close()  # close connection to database
    
    conn = sqlite3.connect(controller_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)
    c.execute(
        '''DELETE FROM controller_data;''')  # run a DELETE command
    conn.commit()  # commit commands
    conn.close()  # close connection to database


def create_all_databases():
    conn = sqlite3.connect(basketball_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)
    c.execute(
        '''CREATE TABLE IF NOT EXISTS basketball_data (z_acc float, x_acc float, player_num text, post_time timestamp);''')  # run a CREATE TABLE command
    conn.commit()  # commit commands
    conn.close()  # close connection to database

    conn = sqlite3.connect(gallery_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)
    c.execute(
        '''CREATE TABLE IF NOT EXISTS gallery_data (target integer, post_time timestamp);''')  # run a CREATE TABLE command
    conn.commit()  # commit commands
    conn.close()  # close connection to database

    conn = sqlite3.connect(game_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)
    c.execute(
        '''CREATE TABLE IF NOT EXISTS game_data ( current_game text, game_over integer, post_time timestamp);''')  # run a CREATE TABLE command
    conn.commit()  # commit commands
    conn.close()  # close connection to database

    conn = sqlite3.connect(controller_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)
    c.execute(
        '''CREATE TABLE IF NOT EXISTS controller_data ( player_num text, post_time timestamp);''')  # run a CREATE TABLE command
    conn.commit()  # commit commands
    conn.close()  # close connection to database

    conn = sqlite3.connect(high_score_db)  # connect to that database (will create if it doesn't already exist)
    c = conn.cursor()  # make cursor into database (allows us to execute commands)
    c.execute(
        '''CREATE TABLE IF NOT EXISTS high_score_data ( username text, basketball_score_norm integer, basketball_score_hard integer, 
         gallery_score_easy integer, gallery_score_med integer, gallery_score_hard integer, post_time timestamp);''')  # run a CREATE TABLE command
    conn.commit()  # commit commands
    conn.close()  # close connection to database

