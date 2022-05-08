"""
Name: Gediminas Vasiliauskas
Student ID: m31234gv
Game Resolution: 1440x900
"""

from tkinter import *
import random
import atexit
import sys

GAME_WIDTH = 1440
GAME_HEIGHT = 900

GAME_SPEED = 30
BACKGROUND_COLOR = "#000000"


class Player:
    SIZE = 58
    COLOR = "#f4f0ef"
    MOVEMENT_SPEED = 4
    REMOVE_SPEED = 2
    SPEED_CAP = 8

    keys = {
        "up": False,
        "left": False,
        "down": False,
        "right": False
    }

    shoot_keys = {
        "up": False,
        "left": False,
        "down": False,
        "right": False
    }

    def __init__(self):
        self.bullets = []
        self.shoot_cooldown = 0
        self.next_shot_sec = 6

        self.health = 3
        self.score = 0

        self.invincible = False
        self.invincible_cooldown = 50
        self.invincible_timer = 0

        self.coords = (700, 450, 0, 0)
        self.forces = [0, 0]

        self.playermodel = canvas_room.create_oval(
            self.coords[0], self.coords[1],
            self.coords[0] + self.SIZE, self.coords[1] + self.SIZE,
            fill=self.COLOR, outline="#000000", width=3, tag="player")

    def shoot_direction(self, direction):
        if(self.shoot_cooldown == 0):
            self.bullet = Bullet(direction)
            self.bullets.append(self.bullet)
            self.shoot_cooldown = self.next_shot_sec

    def handle_shooting(self):
        if(self.shoot_cooldown != 0):
            self.shoot_cooldown -= 1

        for direction, ready_to_shoot in self.shoot_keys.items():
            if(ready_to_shoot):
                self.shoot_direction(direction)
                break

        for bullet in self.bullets:
            bullet.fly()

    def handle_movement(self):
        for direction, active_move in self.keys.items():
            if(active_move):
                if(direction == "up"):
                    self.forces[1] -= self.MOVEMENT_SPEED
                elif(direction == "left"):
                    self.forces[0] -= self.MOVEMENT_SPEED
                elif(direction == "down"):
                    self.forces[1] += self.MOVEMENT_SPEED
                elif(direction == "right"):
                    self.forces[0] += self.MOVEMENT_SPEED

        for i, force in enumerate(self.forces):
            if(force > self.SPEED_CAP):
                self.forces[i] = self.SPEED_CAP
            elif(force < -self.SPEED_CAP):
                self.forces[i] = -self.SPEED_CAP

            if(force > 0):
                self.forces[i] -= self.REMOVE_SPEED
            elif(force < 0):
                self.forces[i] += self.REMOVE_SPEED

        self.check_room_collisions()

        canvas_room.move(self.playermodel, self.forces[0], self.forces[1])
        self.coords = canvas_room.coords(self.playermodel)

    def check_room_collisions(self):
        new_coords_x = (self.coords[0] + self.forces[0],
                        self.coords[2] + self.forces[0])

        new_coords_y = (self.coords[1] + self.forces[1],
                        self.coords[3] + self.forces[1])

        for new_x in new_coords_x:
            # force 10, current_x 1210, WIDTH 1216, new_x 1220
            # force 2, current_x 4, WIDTH 0, new_x -6

            if new_x > room.WIDTH:
                self.forces[0] = room.WIDTH - self.coords[2]
            if new_x < 0:
                self.forces[0] = -self.coords[0]

        for new_y in new_coords_y:
            if new_y > room.HEIGHT:
                self.forces[1] = room.HEIGHT - self.coords[3]
            if new_y < 0:
                self.forces[1] = -self.coords[1]

    def lose_health(self, amount):
        self.health -= amount
        self.invincible = True
        self.invincible_timer = self.invincible_cooldown

    def key_pressed(self, key):
        self.keys[key] = True

    def key_released(self, key):
        self.keys[key] = False

    def shoot_pressed(self, key):
        self.shoot_keys[key] = True

    def shoot_released(self, key):
        self.shoot_keys[key] = False

    def handle_invincible(self):
        if(self.invincible_timer > 0):
            self.invincible_timer -= 1
            canvas_room.itemconfig(self.playermodel, fill="#FF0000")
        else:
            self.invincible = False
            canvas_room.itemconfig(self.playermodel, fill=self.COLOR)

    def logic(self):
        self.handle_invincible()
        self.handle_movement()
        self.handle_shooting()


class Enemy:
    def __init__(self, spawnx, spawny):
        self.movement_speed = random.randint(2, 5)
        self.health = random.randint(3, 8)
        self.forces = [0, 0]
        self.image_ref = []

        window.enemy_img = enemy_img = PhotoImage(file=rf'images/common_enemy_{random.randint(0,3)}.png')
        self.enemymodel = canvas_room.create_image(spawnx, spawny, image=enemy_img, anchor="nw", tag="enemy")
        self.image_ref.append(enemy_img)

        self.width = enemy_img.width()
        self.height = enemy_img.height()

        self.coords = (canvas_room.coords(self.enemymodel)[0],
                        canvas_room.coords(self.enemymodel)[1],
                        canvas_room.coords(self.enemymodel)[0] + self.width,
                        canvas_room.coords(self.enemymodel)[1] + self.height)

    def move_towards_player(self):
        x, y = canvas_room.coords(self.enemymodel)

        x += int(self.width/2)
        y += int(self.height/2)

        tx = (player.coords[0]+player.coords[2])/2
        ty = (player.coords[1]+player.coords[3])/2

        self.apply_forces(x, tx, 0, 3)
        self.apply_forces(y, ty, 1, 3)

        canvas_room.move(self.enemymodel, self.forces[0], self.forces[1])
        self.coords = (
            canvas_room.coords(self.enemymodel)[0],
            canvas_room.coords(self.enemymodel)[1],
            canvas_room.coords(self.enemymodel)[0] + self.width,
            canvas_room.coords(self.enemymodel)[1] + self.height)

    def apply_forces(self, coord, tcoord, force_id, center_offset):
        if(coord < tcoord + center_offset and coord > tcoord - center_offset):
            self.forces[force_id] = 0
        elif(coord > tcoord):
            self.forces[force_id] = -self.movement_speed
        else:
            self.forces[force_id] = self.movement_speed


    def check_collisions(self, target_coords):
        collision_detected = False

        x_coords = (self.coords[0], self.coords[2])
        y_coords = (self.coords[1], self.coords[3])
        target_x_coords = (target_coords[0], target_coords[2])
        target_y_coords = (target_coords[1], target_coords[3])

        target_inside_x = self.in_between(target_x_coords, x_coords)
        target_inside_y = self.in_between(target_y_coords, y_coords)

        if(target_inside_x and target_inside_y):
            return True

        return False

    def in_between(self, a_coords, b_coords):
        # t -> target
        for t in a_coords:
            if(t > b_coords[0] and t < b_coords[1]):
                return True
        return False

    def logic(self):

        player_collision = self.check_collisions(player.coords)

        if(player_collision and not player.invincible):
            player.lose_health(1)

        for bullet in player.bullets:
            bullet_collision = self.check_collisions(bullet.coords)

            if(bullet_collision):
                self.health -= 1
                canvas_room.delete(bullet.bulletmodel)
                player.bullets.remove(bullet)
        
        self.move_towards_player()


class Bullet:
    def __init__(self, direction):
        self.SPEED = random.randint(player.SPEED_CAP-player.REMOVE_SPEED, player.SPEED_CAP)     
        self.fly_dir = {
            "up":   -self.SPEED,
            "left": -self.SPEED,
            "down": self.SPEED,
            "right":self.SPEED
        }   
        self.SIZE = 14
        self.COLOR = "#FFFFFF"
        self.lifecycle = 40
        self.id = 0

        self.forces = [0,0]

        self.direction = direction
        self.init_x = player.coords[0] - self.SIZE
        self.init_y = player.coords[1] - self.SIZE

        if(direction == "up" or direction == "down"):
            self.init_x = random.randint(
                int(player.coords[0] + player.SIZE/6),
                int(player.coords[2] - player.SIZE/3))
        elif(direction == "left" or direction == "right"):
            self.init_y = random.randint(
                int(player.coords[1] + player.SIZE/6),
                int(player.coords[3] - player.SIZE/3))
        if(direction == "down"):
            self.init_y = player.coords[3]
        elif(direction == "right"):
            self.init_x = player.coords[2]

        self.bulletmodel = canvas_room.create_oval(
                self.init_x, self.init_y, 
                self.init_x + self.SIZE, self.init_y + self.SIZE,
                fill=self.COLOR, outline="#000000", width=3, tag="bullet")

        self.coords = canvas_room.coords(self.bulletmodel)

    def fly(self):
        self.lifecycle -= 1

        if(self.lifecycle > 8):
            for bullet_dir, bullet_speed in self.fly_dir.items(): 
                if(self.direction == bullet_dir):
                    if(bullet_dir == "up" or bullet_dir == "down"):
                        self.forces[1] = bullet_speed
                    elif(bullet_dir == "left" or bullet_dir == "right"):
                        self.forces[0] = bullet_speed 
        elif(self.lifecycle > 0):
            self.forces[0] += random.randint(-1,1)
            self.forces[1] += random.randint(-1,1)
        else:
            canvas_room.delete(self.bulletmodel)
            player.bullets.pop(self.id)

        """ 
        for key, val in self.keys.items():
            if(val):
                if(key == "up"):    self.forces[1] -= self.MOVEMENT_SPEED
                if(key == "left"):  self.forces[0] -= self.MOVEMENT_SPEED
                if(key == "down"):  self.forces[1] += self.MOVEMENT_SPEED
                if(key == "right"): self.forces[0] += self.MOVEMENT_SPEED"""

        canvas_room.move(self.bulletmodel, self.forces[0], self.forces[1]) 
        self.coords = canvas_room.coords(self.bulletmodel)


class Room:
    WIDTH = 1216
    HEIGHT = 760
    GRID_SPACING = 152 # for 152 -> grid goes 8x5
    GRID_WIDTH = int(WIDTH/GRID_SPACING)
    GRID_HEIGHT = int(HEIGHT/GRID_SPACING)

    """ 8x5 room
    [][][][][][][][]
    [][][][][][][][]
    [][][][][][][][]
    [][][][][][][][]
    [][][][][][][][]
    """

    def __init__(self):
        global canvas_room, room_tile_images # room_tile_images global because tkinter is weird
                                             # and only loads last image in list otherwise
        
        self.room_tile_images= []

        self.enemies = []
        self.spawn_enemy_timer = 0
        self.spawn_enemy_cooldown = 40


        for i in range(5):
            window.room_tile_img = room_tile_img = PhotoImage(file=fr'images/tile_{i}.png')
            self.room_tile_images.append(room_tile_img)

        canvas_room = Canvas(canvas_game, bg=BACKGROUND_COLOR, height=self.HEIGHT, width=self.WIDTH)
        canvas_room.place(relx = 0.5, rely = 0.55, anchor=CENTER)
        
        self.room_tiles = [[0 for x in range(self.GRID_HEIGHT)]
                             for y in range(self.GRID_WIDTH)]

        # fill with random room tiles
        for r in range(self.GRID_HEIGHT):
            for c in range(self.GRID_WIDTH):
                
                room_tile = canvas_room.create_image((c*self.GRID_SPACING,r*self.GRID_SPACING), 
                                                    image=self.room_tile_images[random.randint(0, 4)], anchor='nw', tag="room_tile")
                self.room_tiles[c][r] = room_tile
    
    def check_enemies_health(self):
        for enemy in self.enemies:
            if(enemy.health < 1):
                canvas_room.delete(enemy.enemymodel)
                self.enemies.remove(enemy)
                player.score += 1

    def spawn_enemy(self):
        flip_coin_x_y = random.randint(0,1)
        xside = random.randint(0,1)
        yside = random.randint(0,1)
        x = random.randint(0, self.WIDTH)
        y = random.randint(0, self.HEIGHT)

        if(flip_coin_x_y):  
            if(xside): x = -72
            else: x = self.WIDTH + 72
        else:
            if(yside): y = -72
            else: y = self.HEIGHT + 72

        self.enemies.append(Enemy(x, y))

    def spawn_enemies(self):
        if(self.spawn_enemy_timer == 0):
            self.spawn_enemy()
            self.spawn_enemy_timer = self.spawn_enemy_cooldown
        else:
            self.spawn_enemy_timer -= 1

    def game_events_logic(self):
        
        self.spawn_enemies() #shouldn't be a thing according to my initial game idea

        self.check_enemies_health()


class User():
    #max_points = -1
    #self.can_continue = False

    def __init__(self, username, points):
        self.max_points = points
        self.name = username

    def __lt__(self, other):
        return self.max_points > other.max_points

    def update_points(self, points):
        if(self.max_points < points):
            self.max_points = points


def create_game_over():
    reset_window()

    global can_continue
    can_continue = False

    canvas_over = Canvas(window, width = GAME_WIDTH, height = GAME_HEIGHT)
    canvas_over.pack()

    window.background_image = background_image = PhotoImage(file=r"images/menu_background.png")
    background_label = Label(canvas_over, image=background_image)
    background_label.place(relwidth=1, relheight=1)

    background_label.columnconfigure(0, weight=1)
    background_label.columnconfigure(1, weight=1)
    background_label.columnconfigure(2, weight=1)

    background_label.rowconfigure(0, weight=1)
    background_label.rowconfigure(1, weight=1)
    background_label.rowconfigure(2, weight=1)
    background_label.rowconfigure(3, weight=1)
    background_label.rowconfigure(4, weight=1)

    txt_game_over = Label(background_label, text="GAME OVER", bg="#8383A3", fg="#FFFFFF", borderwidth=10, relief="sunken", font=("Roboto 100 bold"))
    txt_game_over.grid(column=1, row=1, ipadx = 100, sticky=S)

    txt_game_over = Label(background_label, text=f"SCORE: {player.score}", bg="#8383A3", fg="#FFFFFF", borderwidth=10, relief="sunken", font=("Roboto 100 bold"))
    txt_game_over.grid(column=1, row=2, ipadx = 100, sticky=N)

    btn_play_again = Button(background_label, text="TRY AGAIN", font=("Roboto 50 bold"), borderwidth = 10, relief="ridge", command=create_game_window)
    btn_play_again.grid(column=1, row=3, sticky=EW)

    btn_exitmenu = Button(background_label, text="EXIT TO MENU", font=("Roboto", 50), borderwidth = 10, relief="ridge", command=create_main_menu)
    btn_exitmenu.grid(column=1, row=4, sticky=EW)

    current_user.update_points(player.score)


def create_pause():
    global can_continue, canvas_pause
    can_continue = True

    canvas_pause = Canvas(window, width = GAME_WIDTH, height = GAME_HEIGHT)
    canvas_pause.pack()

    window.background_image = background_image = PhotoImage(file=r"images/menu_background.png")
    background_label = Label(canvas_pause, image=background_image)
    background_label.place(relwidth=1, relheight=1)

    background_label.columnconfigure(0, weight=1)
    background_label.columnconfigure(1, weight=1)
    background_label.columnconfigure(2, weight=1)

    background_label.rowconfigure(0, weight=1)
    background_label.rowconfigure(1, weight=2)
    background_label.rowconfigure(2, weight=1)
    background_label.rowconfigure(3, weight=1)
    background_label.rowconfigure(4, weight=1)

    txt_paused = Label(background_label, text="PAUSED", bg="#8383A3", fg="#FFFFFF", borderwidth=10, relief="sunken", font=("Roboto 100 bold"))
    txt_paused.grid(column=1, row=1, ipadx = 100, sticky=N)

    btn_continue = Button(background_label, text="CONTINUE", font=("Roboto", 50), borderwidth = 10, relief="ridge", command=pause)
    #btn_continue.grid(column=1, row=1, padx=400, ipadx=400, ipady=30)
    btn_continue.grid(column=1, row=2, sticky=EW)

    btn_exitmenu = Button(background_label, text="EXIT TO MENU", font=("Roboto", 50), borderwidth = 10, relief="ridge", command=create_main_menu)
    btn_exitmenu.grid(column=1, row=3, sticky=EW)


def pause():
    global game_paused_state

    if(game_paused_state): 
        game_paused_state = False
        canvas_pause.destroy()
        canvas_game.pack()
        next_frame()
    else: 
        game_paused_state = True
        canvas_game.pack_forget()
        create_pause()


def boss_key():
    global game_bosskey_state, window_bosskey

    if(game_bosskey_state):
        try:    pause()
        except: print("Game not running. Can't Pause")
        game_bosskey_state = False
        window_bosskey.destroy()

    else:
        try:    pause()
        except: print("Game not running. Can't Pause")

        game_bosskey_state = True

        window_bosskey = Toplevel(window)
        window_bosskey.title("Photoshop CC 2017")
        window_bosskey.geometry(f"{GAME_WIDTH}x{GAME_HEIGHT}")
        window_bosskey.bind("b", lambda event: boss_key())

        window.bossimage = bossimage = PhotoImage(file=r"images/bosskey.png")   
        background_label = Label(window_bosskey, image=bossimage)
        background_label.place(relwidth=1, relheight=1)


def next_frame():
    global game_paused_state

    score_text.set(f"SCORE: {player.score}")
    health_text.set(f"HEALTH: {player.health}")

    try:
        if(not game_paused_state):
            room.game_events_logic()
            
            player.logic()
            
            for enemy in room.enemies:
                enemy.logic()

            if(player.health < 1):
                create_game_over()          
                return None

            window.after(GAME_SPEED, next_frame)
    except:
        #print("Runtime error, did you spam the pause button?")
        pass


def reset_window():
    for child in window.winfo_children():
        child.destroy()

    window.unbind("p")


def cheat_add(character):
    global unfinished_string

    cheat_codes = ["rock", "gun", "victory"]
    unfinished_string += character

    for cheat in cheat_codes:
        if cheat in unfinished_string:
            execute_cheat(cheat)
            unfinished_string = ""

    if(len(unfinished_string) > 20):
        unfinished_string = unfinished_string[-10:]


def execute_cheat(cheat):
    if(cheat == "rock"): player.health += 100
    if(cheat == "gun"): player.next_shot_sec = 1
    if(cheat == "victory"): player.score += 10


def create_game_window():
    reset_window()

    # creates game window
    global canvas_game # background canvas
    canvas_game = Canvas(window, bg="#333333", height=GAME_HEIGHT, width=GAME_WIDTH)
    canvas_game.pack()

    # create instances
    global room, player, score_text, health_text
    room = Room() # must be created before Player()
    player = Player()

    score_text = StringVar()
    lbl_score = Label(canvas_game, textvariable=score_text, font="Roboto 40", bg="#333333", fg="#ffffff")
    lbl_score.place(relx = 0.3, rely = 0.06, anchor=CENTER)

    health_text = StringVar()
    lbl_health = Label(canvas_game, textvariable=health_text, font="Roboto 40", bg="#333333", fg="#ffffff")
    lbl_health.place(relx = 0.7, rely = 0.06, anchor=CENTER)

    # key presses
    window.bind("<KeyPress-w>", lambda event: player.key_pressed("up"))
    window.bind("<KeyPress-a>", lambda event: player.key_pressed("left"))
    window.bind("<KeyPress-s>", lambda event: player.key_pressed("down"))
    window.bind("<KeyPress-d>", lambda event: player.key_pressed("right"))
    window.bind("<KeyRelease-w>", lambda event: player.key_released("up"))
    window.bind("<KeyRelease-a>", lambda event: player.key_released("left"))
    window.bind("<KeyRelease-s>", lambda event: player.key_released("down"))
    window.bind("<KeyRelease-d>", lambda event: player.key_released("right"))

    # uppercase equivalent to eliminate shift problems
    window.bind("<KeyPress-W>", lambda event: player.key_pressed("up"))
    window.bind("<KeyPress-A>", lambda event: player.key_pressed("left"))
    window.bind("<KeyPress-S>", lambda event: player.key_pressed("down"))
    window.bind("<KeyPress-D>", lambda event: player.key_pressed("right"))
    window.bind("<KeyRelease-W>", lambda event: player.key_released("up"))
    window.bind("<KeyRelease-A>", lambda event: player.key_released("left"))
    window.bind("<KeyRelease-S>", lambda event: player.key_released("down"))
    window.bind("<KeyRelease-D>", lambda event: player.key_released("right"))

    window.bind("<KeyPress-Up>", lambda event: player.shoot_pressed("up"))
    window.bind("<KeyPress-Left>", lambda event: player.shoot_pressed("left"))
    window.bind("<KeyPress-Down>", lambda event: player.shoot_pressed("down"))
    window.bind("<KeyPress-Right>", lambda event: player.shoot_pressed("right"))
    window.bind("<KeyRelease-Up>", lambda event: player.shoot_released("up"))
    window.bind("<KeyRelease-Left>", lambda event: player.shoot_released("left"))
    window.bind("<KeyRelease-Down>", lambda event: player.shoot_released("down"))
    window.bind("<KeyRelease-Right>", lambda event: player.shoot_released("right"))

    window.bind("r", lambda event: cheat_add("r"))
    window.bind("o", lambda event: cheat_add("o"))
    window.bind("c", lambda event: cheat_add("c"))
    window.bind("k", lambda event: cheat_add("k"))
    window.bind("g", lambda event: cheat_add("g"))
    window.bind("u", lambda event: cheat_add("u"))
    window.bind("n", lambda event: cheat_add("n"))
    window.bind("v", lambda event: cheat_add("v"))
    window.bind("i", lambda event: cheat_add("i"))
    window.bind("t", lambda event: cheat_add("t"))
    window.bind("y", lambda event: cheat_add("y"))

    window.bind("p", lambda event: pause())

    # main game logic
    next_frame()


def create_main_menu():
    reset_window()

    global game_paused_state, can_continue
    game_paused_state = False
    game_over_state = True

    global canvas_menu

    canvas_menu = Canvas(window, width = GAME_WIDTH, height = GAME_HEIGHT)
    canvas_menu.pack()

    window.background_image = background_image = PhotoImage(file=r"images/menu_background.png")
    background_label = Label(canvas_menu, image=background_image)
    background_label.place(relwidth=1, relheight=1)

    background_label.columnconfigure(0, weight=1)
    background_label.columnconfigure(1, weight=1)
    for i in range(7):
        background_label.rowconfigure(i, weight=1)

    font_size = 50

    #btn_new_game = FixedButtonSize(background_label, text="New Game", font=("Roboto",50), width=500, height=100)
    btn_new_game = Button(background_label, text="NEW GAME", font=(f"Roboto {font_size} bold"), borderwidth = 10, relief="ridge", command = create_game_window)
    btn_new_game.grid(column=1, row=1, sticky="ew", padx = 100)

    if(can_continue): 
        bg_color = btn_new_game.cget('bg') 
        click_state = "normal"
    else:
        bg_color = "#FFFFFF"
        click_state = "disabled"

    btn_continue = Button(background_label, text="Continue", font=("Roboto",font_size), state=click_state, bg=bg_color, borderwidth = 10, relief="ridge")
    btn_continue.grid(column=1, row=2, sticky="ew",  padx = 100)

    btn_leaderboard = Button(background_label, text="Leaderboard", font=("Roboto",font_size), borderwidth = 10, relief="ridge", command=create_leaderboard)
    btn_leaderboard.grid(column=1, row=3, sticky="ew", padx = 100)

    btn_cheats = Button(background_label, text="Cheats", font=("Roboto",font_size), borderwidth = 10, relief="ridge", command=create_cheats)
    btn_cheats.grid(column=1, row=4, sticky="ew", padx = 100)

    btn_logout = Button(background_label, text="Log out", font=("Roboto",font_size), borderwidth = 10, relief="ridge", command=create_login)
    btn_logout.grid(column=1, row=5, sticky="ew", padx = 100)


def create_cheats():
    reset_window()

    canvas_cheat = Canvas(window, width = GAME_WIDTH, height = GAME_HEIGHT)
    canvas_cheat.pack()

    window.background_image = background_image = PhotoImage(file=r"images/menu_background.png")
    background_label = Label(canvas_cheat, image=background_image)
    background_label.place(relwidth=1, relheight=1)

    for i in range(7):
        background_label.rowconfigure(i, weight=1)
        background_label.columnconfigure(i, weight=1)

    txt_name1 = Label(background_label, text="[GUN] faster reload", bg="#404040", fg="#FFFFFF", borderwidth=10, relief="sunken", font=("Roboto 30 bold"))
    txt_name1.grid(column=3, row=1)

    txt_name2= Label(background_label, text="[VICTORY] + 10 points", bg="#404040", fg="#FFFFFF", borderwidth=10, relief="sunken", font=("Roboto 30 bold"))
    txt_name2.grid(column=3, row=2)

    txt_name3= Label(background_label, text="[ROCK] + 100 HP", bg="#404040", fg="#FFFFFF", borderwidth=10, relief="sunken", font=("Roboto 30 bold"))
    txt_name3.grid(column=3, row=3)

    btn_return = Button(background_label, text="RETURN", font=("Roboto", 30), borderwidth = 10, relief="ridge", command=create_main_menu)
    btn_return.grid(column=3, row=4, sticky="ew")


def create_leaderboard():
    reset_window()

    canvas_leadb = Canvas(window, width = GAME_WIDTH, height = GAME_HEIGHT)
    canvas_leadb.pack()

    window.background_image = background_image = PhotoImage(file=r"images/menu_background.png")
    background_label = Label(canvas_leadb, image=background_image)
    background_label.place(relwidth=1, relheight=1)

    for i in range(3):
        background_label.rowconfigure(i, weight=1)
        background_label.columnconfigure(i, weight=1)

    txt_name = Label(background_label, text="LEADERBOARD", bg="#404040", fg="#FFFFFF", borderwidth=10, relief="sunken", font=("Roboto 100 bold"))
    txt_name.grid(column=1, row=0)

    ld_label = Label(background_label, bg="#202020", fg="#FFFFFF", borderwidth=10, relief="groove")
    ld_label.grid(column=1, row=1, sticky="ew", ipady=100)

    for c in range(9):
        ld_label.columnconfigure(c, weight=1)

    users.sort()

    #print(len(users))

    for i in range(5):
        if(i >= len(users)):
            print_name = "########"
            print_points = "##"
        else:
            print_name = users[i].name
            print_points = users[i].max_points

        ld_label.rowconfigure(i, weight=1)
        id_text = Label(ld_label, text=f"{i+1}.", bg="#202020", fg="#FFFFFF", font=("Roboto 22"))
        name_text = Label(ld_label, text=print_name, bg="#202020", fg="#FFFFFF", font=("Roboto 22"))
        pts_text = Label(ld_label, text=f"{print_points} pts", bg="#202020", fg="#FFFFFF", font=("Roboto 22"))
        
        id_text.grid(column=3, row=i)
        name_text.grid(column=4, row=i)
        pts_text.grid(column=5, row=i)
            

    btn_return = Button(background_label, text="RETURN", font=("Roboto", 30), borderwidth = 10, relief="ridge", command=create_main_menu)
    btn_return.grid(column=1, row=2, sticky="ew")


def submit_login():
    global current_user, first_open

    #users = []

    name = name_var.get()
    if((not name) or (':' in name)):
        return None

    with open('users.txt', 'r+') as users_file:
        is_new = True

        for line in users_file:
            username, points = line.split(':')

            if(first_open):
                user = User(username, int(points))
                users.append(user)

            if name == username: 
                current_user = user
                is_new = False

        if is_new:
            user = User(name, 0)
            users.append(user)
            current_user = user

    first_open = False
    create_main_menu()


def create_login():
    reset_window()
    update_user_file()

    global name_var

    canvas_login = Canvas(window, width = GAME_WIDTH, height = GAME_HEIGHT)
    canvas_login.pack()

    window.background_image = background_image = PhotoImage(file=r"images/menu_background.png")
    background_label = Label(canvas_login, image=background_image)
    background_label.place(relwidth=1, relheight=1)

    background_label.columnconfigure(0, weight=1)
    background_label.columnconfigure(1, weight=1)
    background_label.columnconfigure(2, weight=1)

    for i in range(10):
        background_label.rowconfigure(i, weight=1)

    txt_name = Label(background_label, text="ENTER NAME", bg="#404040", fg="#FFFFFF", borderwidth=10, relief="sunken", font=("Roboto 100 bold"))
    txt_name.grid(column=1, row=0, ipadx = 50, sticky=S)

    name_var = StringVar()
    name_entry = Entry(background_label, textvariable = name_var, font=("Roboto", 50))
    name_entry.grid(column=1, row=4, sticky="ew", ipady=20)

    btn_login = Button(background_label, text="ENTER", font=("Roboto", 30), borderwidth = 10, relief="ridge", command=submit_login)
    btn_login.grid(column=1, row=7, sticky="ew")
    btn_login = Button(background_label, text="EXIT PROGRAM", font=("Roboto", 30), borderwidth = 10, relief="ridge", command=sys.exit)
    btn_login.grid(column=1, row=8, sticky="ew")


def create_parent_window():
    reset_window()

    # center window on launch
    window.update()

    window_width = GAME_WIDTH  #window.winfo_width()
    window_height = GAME_HEIGHT  #window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = int((screen_width/2) - (window_width/2))
    y = int((screen_height/2) - (window_height/2))

    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    window.bind("b", lambda event: boss_key())


def start_game():
    create_parent_window()
    create_login()

    window.mainloop()


def update_user_file():
    if(users):
        with open("users.txt", "r+") as users_file:
            users_file.truncate(0)
            for user in users:
                users_file.write(f"{user.name}:{user.max_points}\n")

if __name__ == "__main__":

    # main game code logic
    window = Tk()
    window.title("m31234gv")
    window.resizable(False, False)

    game_over_state = False
    game_paused_state = False
    game_bosskey_state = False
    can_continue = False
    first_open = True
    unfinished_string = ""

    users = []

    atexit.register(update_user_file)

    start_game()