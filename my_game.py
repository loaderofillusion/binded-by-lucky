from arcade import check_for_collision_with_list

from pause import PauseView
import arcade
from arcade.camera import Camera2D
from arcade.examples.camera_platform import TILE_SCALING
from pyglet.graphics import Batch
SCREEN_W = 1280
SCREEN_H = 720
TITLE = "Прыгскокология"
MEMORY_TIME = 0.01
TILE_SCALING = 1
# Физика и движение
GRAVITY = 1            # Пикс/с^2
MOVE_SPEED_ACELERATION = 80  # Пикс/с
MOVE_MAX_SPEED = 10
JUMP_SPEED = 15          # Начальный импульс прыжка, пикс/с
LADDER_SPEED = 3
GRAB_SPEED = 3
DASH_SPEED = 15
HORIZONTAL_GRAVITY = 25
MAX_STAMINA = 10
# Качество жизни прыжка
COYOTE_TIME = 0.08        # Сколько после схода с платформы можно ещё прыгнуть
JUMP_BUFFER = 0.12
MAX_JUMPS = 1             # С двойным прыжком всё лучше, но не сегодня
MAX_DASH_TIME = 0.63
MAX_DASHES = 1
# Камера
CAMERA_LERP = 0.12        # Плавность следования камеры
WORLD_COLOR = arcade.color.SKY_BLUE
class GameView(arcade.View):
    def __init__(self):
        super().__init__()
        self.tile_map = None
        arcade.set_background_color(WORLD_COLOR)

        # Камеры
        self.world_camera = Camera2D()
        self.gui_camera = Camera2D()

        # Списки спрайтов
        self.player_list = arcade.SpriteList()
        self.grab_list = arcade.SpriteList()
        self.walls = arcade.SpriteList(use_spatial_hash=True)  # Очень много статичных — хэш спасёт вас
        self.platforms = arcade.SpriteList()  # Двигающиеся платформы
        self.ladders = arcade.SpriteList()
        self.coins = arcade.SpriteList()
        self.hazards = arcade.SpriteList()  # Шипы/лава
        self.inertion_platforms = arcade.SpriteList()
        self.grab_list = arcade.SpriteList()
        self.dashing_platforms = arcade.SpriteList()
        self.dashing_platforms = arcade.SpriteList(use_spatial_hash=True)
        self.crystal_list = arcade.SpriteList()


        # Игрок
        self.player = None
        self.spawn_point = (10, 200)  # Куда респавнить после шипов
        self.player_speed_x = 0
        self.player_speed_y = 0

        # Физика
        self.engine = None

        # Ввод
        self.left = self.right = self.up = self.down = self.jump_pressed = self.dash_pressed = self.grab_pressed = False
        self.jump_buffer_timer = 0.0
        self.time_since_ground = 999.0
        self.jumps_left = MAX_JUMPS
        self.dashes_left = MAX_DASHES
        self.max_walk_speed = MOVE_MAX_SPEED
        self.dash_time = 0
        self.dashing = False
        self.dash_l_vector = False
        self.dash_r_vector = False
        self.dash_u_vector = False
        self.dash_d_vector = False
        self.memory_time = 0
        self.stamina = MAX_STAMINA
        self.dash_save = False

        # Счёт
        self.score = 0
        self.batch = Batch()


    def setup(self, lvl_name):
        # --- Игрок ---
        self.player_list.clear()
        self.player = arcade.Sprite(":resources:images/animated_characters/female_person/femalePerson_idle.png",
                                    scale=0.8)
        self.player.center_x, self.player.center_x = self.spawn_point
        self.player_list.append(self.player)



        # ===== ВОЛШЕБСТВО ЗАГРУЗКИ КАРТЫ! (Почти без магии.) =====
        # Грузим тайловую карту
        self.tile_map = arcade.load_tilemap(f'assets/levels/{lvl_name}.tmx', scaling=TILE_SCALING)

        # --- Достаём слои из карты как спрайт-листы ---
        self.collisions = self.tile_map.sprite_lists["collisions"]
        self.wall_list = self.tile_map.sprite_lists["walls"]
        self.grab_list = self.tile_map.sprite_lists["grab"]
        self.hazards = self.tile_map.sprite_lists["hazards"]
        self.dash_zones = self.tile_map.sprite_lists["dash"]
        self.crystal_list = self.tile_map.sprite_lists["crystals"]

        # --- Физический движок платформера ---
        self.engine = arcade.PhysicsEnginePlatformer(
            player_sprite=self.player,
            gravity_constant=GRAVITY,
            walls=self.collisions,
            platforms=self.platforms,
            ladders=self.ladders
        )

        # Сбросим вспомогательные таймеры
        self.jump_buffer_timer = 0
        self.time_since_ground = 999.0
        self.jumps_left = MAX_JUMPS

    def on_draw(self):
        self.clear()

        # --- Мир ---
        self.world_camera.use()
        self.wall_list.draw()
        self.platforms.draw()
        self.ladders.draw()
        self.hazards.draw()
        self.coins.draw()
        self.crystal_list.draw()
        self.dash_zones.draw()
        self.player_list.draw()
        #необязательно к отрисовке
        '''
        self.grab_list.draw()
        self.inertion_platforms.draw()
        '''


        # --- GUI ---
        self.gui_camera.use()
        self.batch.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            pause_view = PauseView(self)  #
            self.window.show_view(pause_view)
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = True
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = True
        elif key == arcade.key.SPACE:
            self.jump_pressed = True
            self.jump_buffer_timer = JUMP_BUFFER
        elif key == arcade.key.LSHIFT:
            self.dash_pressed = True
        elif key == arcade.key.ENTER:
            self.grab_pressed = True

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.A):
            self.left = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right = False
        elif key in (arcade.key.UP, arcade.key.W):
            self.up = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down = False
        elif key == arcade.key.SPACE:
            self.jump_pressed = False
            # Вариативная высота прыжка: отпустили рано — подрежем скорость вверх
            if self.player.change_y > 0:
                self.player.change_y *= 0.45
        elif key == arcade.key.ENTER:
            self.grab_pressed = False

    def on_update(self, dt: float):
        for i in range(len(self.platforms)):
            self.inertion_platforms[i].change_x = self.platforms[i].change_x
        self.inertion_platforms.update()
        move = 0
        if self.left and not self.right:
            move = -MOVE_SPEED_ACELERATION
            if self.dash_time == 0:
                self.dash_l_vector = True
                self.dash_r_vector = False
        elif self.right and not self.left:
            move = MOVE_SPEED_ACELERATION
            if  self.dash_time == 0:
                self.dash_r_vector = True
                self.dash_l_vector = False
        if self.up and not self.down and self.dash_time == 0:
            self.dash_u_vector = True
            self.dash_d_vector = False
        elif self.down and not self.up and self.dash_time == 0:
            self.dash_d_vector = True
            self.dash_u_vector = False

        if self.max_walk_speed > self.player.change_x + move * dt > -self.max_walk_speed:
            self.player.change_x += move * dt




        # зацеп
        grabable_walls = arcade.check_for_collision_with_list(self.player, self.grab_list)   # стены, за которые можно зацепиться
        grabable_platforms = arcade.check_for_collision_with_list(self.player, self.inertion_platforms)
        can_grab = self.stamina > 0 and self.grab_pressed and (grabable_walls or grabable_platforms)
        if can_grab:
            if self.player.change_x == 15 or self.player.change_x == -15:
                self.dash_time = MAX_DASH_TIME
                self.dashes_left -= 1
                self.dash_pressed = False
            if grabable_platforms:
                self.player.change_x = self.platforms[self.inertion_platforms.index(grabable_platforms[0])].change_x
            else:
                self.player.change_x = 0
            if self.up:
                self.player.change_y = GRAB_SPEED + 1
            elif self.down:
                self.player.change_y = -GRAB_SPEED + 1
            elif not self.down and not self.up:
                self.player.change_y = 1

            self.stamina -= dt


        if (self.dash_l_vector or self.dash_r_vector or self.dash_d_vector or self.dash_u_vector) and not (self.up or self.down or self.left or self.right) and self.dash_time == 0:
            self.memory_time += dt # копим время жизни векторов

        if self.memory_time > MEMORY_TIME:
            self.dash_l_vector = self.dash_r_vector = self.dash_d_vector = self.dash_u_vector = False
            self.memory_time = 0 # убиваем векторы и таймер

        # Лестницы имеют приоритет над гравитацией: висим/лезем
        on_ladder = self.engine.is_on_ladder()  # На лестнице?
        if on_ladder:
            # По лестнице вверх/вниз
            self.jumps_left = 1
            if self.up and not self.down:
                self.player.change_y = LADDER_SPEED
            elif self.down and not self.up:
                self.player.change_y = -LADDER_SPEED
            else:
                self.player.change_y = 0

        # Если не на лестнице — работает обычная гравитация движка
        grounded = self.engine.can_jump(y_distance=6)  # Есть пол под ногами?

        if grounded:
            self.time_since_ground = 0
            self.jumps_left = MAX_JUMPS
            self.dashes_left = MAX_DASHES
            self.stamina = MAX_STAMINA
            if (self.player_speed_x != 0 and not(self.right or self.left)) or (self.player.change_x > 20 and self.left) or (self.player.change_x < -20 and self.right):
                self.player.change_x = 0
            elif self.player_speed_x > 10:
                self.player.change_x -= HORIZONTAL_GRAVITY * dt * 0.8
            elif self.player_speed_x < -10:
                self.player.change_x += HORIZONTAL_GRAVITY * dt * 0.8
            if self.dash_time > MAX_DASH_TIME:
                self.dash_time = 0
            elif self.player_speed_x > 25 and not(self.right or self.left):
                self.player.change_x -= HORIZONTAL_GRAVITY * dt
            elif self.player_speed_x < -25 and not(self.right or self.left):
                self.player.change_x += HORIZONTAL_GRAVITY * dt
            if abs(HORIZONTAL_GRAVITY * dt - self.player_speed_x) < 0.01:
                self.player.change_x = 0

        elif not grounded:
            self.time_since_ground += dt
            if self.dash_time > MAX_DASH_TIME + 0.2:
                self.dash_time = 0
            if self.dash_time == 0 and self.player_speed_x > 23:
                self.player.change_x -= HORIZONTAL_GRAVITY * dt
            elif self.dash_time == 0 and self.player_speed_x < -23:
                self.player.change_x += HORIZONTAL_GRAVITY * dt
            if self.right and self.player_speed_x < -10:
                self.player.change_x += HORIZONTAL_GRAVITY * dt
            elif self.left and self.player_speed_x > 10:
                self.player.change_x -= HORIZONTAL_GRAVITY * dt

            # кристаллы
            touched_crystals = check_for_collision_with_list(self.player, self.crystal_list)
            if touched_crystals and (self.stamina < 10 or self.dashes_left < MAX_DASHES):
                self.dashes_left = MAX_DASHES
                self.stamina = MAX_STAMINA
                self.crystal_list.remove(touched_crystals[0])

        # Учтём «запомненный» пробел
        if self.jump_buffer_timer > 0:
            self.jump_buffer_timer -= dt

        want_jump = self.jump_pressed or (self.jump_buffer_timer > 0)
        want_dash = self.dash_pressed
        can_dash = self.dash_time < MAX_DASH_TIME and (self.dashes_left > 0)
        in_dash_zone = check_for_collision_with_list(self.player, self.dash_zones)
        if want_dash and can_dash:
            if self.dash_r_vector == self.dash_l_vector == self.dash_d_vector == self.dash_u_vector == False:
                self.dash_r_vector = True
            if in_dash_zone:
                self.dash_save = True
                self.dashes_left = MAX_DASHES
                self.dash_time = MAX_DASH_TIME * 0.8
            self.memory_time = 0
            if self.dash_r_vector:
                self.player.change_x = DASH_SPEED
            elif self.dash_l_vector:
                self.player.change_x = -DASH_SPEED
            else:
                self.player.change_x = 0
            if self.dash_u_vector:
                self.player.change_y = DASH_SPEED
            elif self.dash_d_vector:
                self.player.change_y = -DASH_SPEED
            else:
                self.player.change_y = 1
            self.dash_time += dt
            if self.dash_time > MAX_DASH_TIME * 0.9:
                if self.dash_save == False:
                    self.dashes_left -= 1
                self.dash_save = False
                self.dash_pressed = self.dash_u_vector = self.dash_d_vector = self.dash_l_vector = self.dash_r_vector = False
                self.player.change_y = 5
                self.player.change_x = 0
        if self.dash_time > 0:
            self.dash_time += dt
        # прыжок с зацепа/от стены
        if want_jump and  not self.grab_pressed and grabable_walls:
            if self.dash_time > 0:
                self.dash_pressed = False
                self.player.change_y = DASH_SPEED * 2
                if self.player.center_x < grabable_walls[0].center_x - grabable_walls[0].width * 0.1:
                    self.player.change_x = -10
                elif self.player.center_x > grabable_walls[0].center_x + grabable_walls[0].width * 0.1:
                    self.player.change_x = 10

            elif not(self.right and self.left):
                self.jump_pressed = False
                self.jump_buffer_timer = 0
                self.grab_pressed = False
                if self.player.center_x < grabable_walls[0].center_x - grabable_walls[0].width * 0.1:
                    self.right = False
                    self.player.change_x = -5
                elif self.player.center_x > grabable_walls[0].center_x + grabable_walls[0].width * 0.1:
                    self.left = False
                    self.player.change_x = 5
                else:
                    self.player.change_x += self.platforms[self.inertion_platforms.index(grabable_platforms[0])].change_x
                self.player.change_y = 12
        elif self.grab_pressed and grabable_walls and want_jump:
            self.grab_pressed = False
            if self.player.center_x < grabable_walls[0].center_x:
                self.right = False
                self.player.change_x += -10
            elif self.player.center_x > grabable_walls[0].center_x:
                self.left = False
                self.player.change_x += 10
            self.player.change_y += 5
        if grabable_platforms and want_jump:
            self.player.change_x += self.platforms[self.inertion_platforms.index(grabable_platforms[0])].change_x


        # дефолтный прыжок и комбинация с рывком
        if want_jump and (grounded or self.time_since_ground <= COYOTE_TIME or in_dash_zone):
            if not in_dash_zone:
                self.jump_pressed = False
                self.jump_buffer_timer = 0
                self.player.change_y = JUMP_SPEED
                self.jump_buffer_timer = 0
            if MAX_DASH_TIME > self.dash_time > 0:
                self.dashes_left -= 1
                if MAX_DASH_TIME > self.dash_time > MAX_DASH_TIME * 0.5:
                    self.dashes_left += 1
                self.player.change_x = self.player_speed_x * 1.5
                self.dash_pressed = self.dash_u_vector = self.dash_d_vector = self.dash_l_vector = self.dash_r_vector = False
                self.dash_time = 0
                self.player.change_y = JUMP_SPEED
                if grabable_platforms:
                    self.player.change_x += self.platforms[
                        self.inertion_platforms.index(grabable_platforms[0])].change_x



        # Обновляем физику — движок сам двинет игрока и платформы
        self.engine.update()
        # Собираем монетки и проверяем опасности
        for coin in arcade.check_for_collision_with_list(self.player, self.coins):
            coin.remove_from_sprite_lists()
            self.score += 1

        if arcade.check_for_collision_with_list(self.player, self.hazards):
            # «Ау» -> респавн
            self.player.center_x, self.player.center_y = self.spawn_point
            self.player.change_x = self.player.change_y = 0
            self.time_since_ground = 999
            self.jumps_left = MAX_JUMPS
            self.dashes_left = MAX_DASHES
            self.dash_time = MAX_DASH_TIME

        # Камера — плавно к игроку и в рамках мира
        target = (self.player.center_x, self.player.center_y)
        cx, cy = self.world_camera.position
        smooth = (cx + (target[0] - cx) * CAMERA_LERP,
                  cy + (target[1] - cy) * CAMERA_LERP)

        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        # Ограничим, чтобы за края уровня не выглядывало небо
        self.world_w = int(self.tile_map.width * self.tile_map.tile_width * TILE_SCALING)
        self.world_h = int(self.tile_map.height * self.tile_map.tile_height * TILE_SCALING)
        cam_x = max(half_w, min(self.world_w - half_w, smooth[0]))
        cam_y = max(half_h, min(self.world_h - half_h, smooth[1]))

        self.world_camera.position = (cam_x, cam_y)
        self.gui_camera.position = (SCREEN_W / 2, SCREEN_H / 2)

        # Обновим счёт
        self.text_score = arcade.Text(f"""Счёт: {self.score}
                                            speed={self.player_speed_x}""",
                                      16, SCREEN_H - 36, arcade.color.DARK_SLATE_GRAY,
                                      20, batch=self.batch)
        self.info_text = arcade.Text(f"""jumps={self.jumps_left}  stamina={self.stamina}  dashes={self.dashes_left}""",
                                     16, SCREEN_H - 72, arcade.color.DARK_SLATE_GRAY,
                                     20, batch=self.batch)
        self.player_speed_y, self.player_speed_x = self.player.change_y, self.player.change_x

