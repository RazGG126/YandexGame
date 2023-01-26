import os
import sys
import pygame
import json
import random
import math
from User import User, LEVELS
from pygame.sprite import AbstractGroup

# initialization of important variables
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()
WIDTH = 1000
HEIGHT = 500
SIZE = WIDTH, HEIGHT
SCREEN = pygame.display.set_mode(SIZE)
SCREEN.fill(pygame.Color('black'))
CLOCK = pygame.time.Clock()
FPS = 30
ground_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
sprites = pygame.sprite.Group()
sprites_ = pygame.sprite.Group()
unmoving_sprites = pygame.sprite.Group()
mousePos = {'x': 0, 'y': 0}
user = None
hero = None
cat = None
luke = None
lamp = False
restarts = 0
cat_number = None
congratulations = False

w
# function of loading images
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# dictionary with frames
DICT_IMAGES = {
    'hero_frames_default': [load_image(rf'sprites\default\{i}.png') for i in range(1, 7)],
    'hero_frames_colorit': [load_image(rf'sprites\colorit\{i}.png') for i in range(1, 7)],
    'hero_frames_extra_pink': [load_image(rf'sprites\extra_pink\{i}.png') for i in range(1, 7)],
    'hero_frames_radiation': [load_image(rf'sprites\radiation\{i}.png') for i in range(1, 7)],
    'enemy_frames': [load_image(rf'sprites\enemy_skin\enemy.{i}.png') for i in range(1, 7)],
    'hero_frames_default_bag': [load_image(rf'sprites\default\{i}.{i}.png') for i in range(1, 7)],
    'hero_frames_colorit_bag': [load_image(rf'sprites\colorit\{i}.{i}.png') for i in range(1, 7)],
    'hero_frames_extra_pink_bag': [load_image(rf'sprites\extra_pink\{i}.{i}.png') for i in range(1, 7)],
    'hero_frames_radiation_bag': [load_image(rf'sprites\radiation\{i}.{i}.png') for i in range(1, 7)],
    'death_frames': [load_image(rf'death\{i}.png') for i in range(1, 8)],
    'ak47': load_image(r'weapon\ak47.png'),
    'm4a1': load_image(r'weapon\m4a1.png'),
    'menu_bg': load_image(r'textures\bg-menu.png'),
    'keys_wasd': load_image(r'textures\keys_wasd.png'),
    'keys_arrows': load_image(r'textures\keys_arrows.png'),
    'ground_ender': load_image(r'textures\ender_block.png'),
    'stone_block': load_image(r'textures\stone_block.png'),
    'tree_block': load_image(r'textures\tree-block.png'),
    'red_block': load_image(r'textures\red-block.png'),
    'white_block': load_image(r'textures\white-block.png'),
    'wood-block': load_image(r'textures\wood-block.png'),
    'fire': load_image(r'textures\Fire.png'),
    'cat1': [load_image(r'sprites\cats\murzik\cat.png'), load_image(r'sprites\cats\murzik\cat_2.png'),
             load_image(r'sprites\cats\murzik\cat.png'), load_image(r'sprites\cats\murzik\cat_3.png')],
    'cat2': [load_image(r'sprites\cats\treha\cat_treha.png'), load_image(r'sprites\cats\treha\cat_treha_2.png'),
             load_image(r'sprites\cats\treha\cat_treha_4.png'), load_image(r'sprites\cats\treha\cat_treha_3.png')],
    'box': load_image(r'textures\box.jpg'),
    'ground_sand': load_image(r'textures\ground_sand.png'),
    'ground_stone': load_image(r'textures\ground_stone.jpg'),
    'bush': load_image(r'textures\bush_mine.png'),
    'branch': load_image(r'textures\branch.png'),
    'luke_h': load_image(r'textures\trapdoor_h.png'),
    'luke': load_image(r'textures\trapdoor.png'),
    'lamp': load_image(r'textures\glowstone.png'),
}


# function of loading <<user>> statistics
def load_json():
    global user
    data = json.load(open(r'data\User\user.json', 'r', encoding='utf-8'))
    user = User(level=data['level'], coins=data['coins'],
                skin=data['skin'], skins_have=data['skins_have'], gun=data['gun'], gun_have=data['gun_have'],
                kills=data['kills'], restarts=data['restarts'], game_replays=data['game_replays'],
                ammo_spend=data['ammo_spend'], caught_cat=data['caught_cat'],
                menu_music_volume=data['menu_music_volume'], control=data['control'])


load_json()


# function of saving <<user>> statistics
def dump_json():
    global user
    data = user.create_dict()

    json.dump(data, open(r'data\User\user.json', 'w', encoding='utf-8'))


# <<gun>> class
class Gun(pygame.sprite.Sprite):
    def __init__(self, power, ammo, gun_image, *groups: AbstractGroup):
        super().__init__(*groups)
        self.image = gun_image
        self.rect = self.image.get_rect()
        self.power = power
        self.ammo = ammo
        self.ammo_now = ammo
        self.wait = 0
        self.wait_max = 100


# <<cat>> class
class Cat(pygame.sprite.Sprite):
    def __init__(self, x, y, frames, static=False, number='1', *groups: AbstractGroup):
        super().__init__(all_sprites, *groups)
        self.frames = frames
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 4
        self.speed_y = 4
        self.moving_left = True
        self.moving_right = False

        self.was_meow = False
        self.count_meow = 0

        self.number = number

        self.static = static

    def sound_meow(self, hero):
        # lodig of sound <<meow>>
        if not hero.catch_cat:
            dl_x = self.rect.x - hero.rect.x
            dl_y = self.rect.y - hero.rect.y
            distance = (dl_x ** 2 + dl_y ** 2) ** 0.5
            if distance < 300:
                if self.count_meow == 100:
                    self.was_meow = False
                    self.count_meow = 0
                if not self.was_meow:
                    meow.set_volume((10 - distance / 100 * 3) / 10)
                    meow.play()
                    self.was_meow = True
                else:
                    self.count_meow += 1

    def update_frame(self):
        self.cur_frame += 1
        if self.cur_frame > 15:
            self.cur_frame = 0

        if self.moving_left:
            self.image = pygame.transform.flip(self.frames[self.cur_frame // 4], True, False)
        elif self.moving_right:
            self.image = self.frames[self.cur_frame // 4]

    def update(self, *args):
        self.update_frame()


# <<hero>> class
class Hero(pygame.sprite.Sprite):
    def __init__(self, x, y, gun, frames, *groups: AbstractGroup):
        super().__init__(all_sprites, *groups)
        self.frames = frames
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 4
        self.speed_y = 4

        self.angle = 0
        self.heavy = 0

        self.health = 100

        self.was_walk = False
        self.count_walk = 0

        self.catch_cat = False
        self.on_the_luke = False

        self.moving = False
        self.moving_left = False
        self.moving_right = True
        self.move_x = 0
        self.move_y = 0

        self.gun = gun  # <<gun>> class
        self.gun_image = gun.image
        self.strike_can = True

        self.reloading = False
        self.count_reloading = 0

        self.home = False

    def change_gun(self, gun):
        self.gun = gun
        self.gun_image = gun.image

    def sound_walk(self):
        # logic of sound <<walk>>
        if self.moving:
            if self.count_walk == 10:
                self.was_walk = False
                self.count_walk = 0
            if not hero.was_walk:
                walk.play()
                self.was_walk = True
            else:
                self.count_walk += 1

    def update_frame(self, stand=False):
        if stand:
            if self.moving_left:
                self.image = pygame.transform.flip(self.frames[self.cur_frame // 4], True, False)
            elif self.moving_right:
                self.image = self.frames[self.cur_frame // 4]
        else:
            self.cur_frame += 1
            if self.cur_frame > 19:
                self.cur_frame = 0
        if self.moving_left:
            self.image = pygame.transform.flip(self.frames[self.cur_frame // 4], True, False)
        elif self.moving_right:
            self.image = self.frames[self.cur_frame // 4]

    def move_gun(self):
        if self.moving_left:
            # function of centering character's weapon
            self.gun.image = pygame.transform.flip(self.gun_image, True, False)
            self.gun.image = pygame.transform.rotate(self.gun.image, -90)
            if self.angle <= -80:
                self.strike_can = True
                self.gun.image = pygame.transform.rotate(self.gun.image, 360 - (self.angle + 90))
                SCREEN.blit(self.gun.image, (self.rect.x - 20,
                                             (self.rect.y + self.image.get_size()[1] // 2 - (
                                                     90 + (self.angle + 90)) // 4)))
            elif 90 <= self.angle <= 180:
                self.strike_can = True
                self.gun.image = pygame.transform.rotate(self.gun.image, 360 - (self.angle + 90))
                SCREEN.blit(self.gun.image, ((self.rect.x - 20) - 1 * (self.angle - 180) // 4,
                                             (self.rect.y + self.image.get_size()[1] // 2 + 1 * (
                                                     self.angle - 180) // 4)))
            else:
                self.strike_can = False
                self.gun.image = pygame.transform.flip(self.gun_image, True, False)
                SCREEN.blit(self.gun.image, (self.rect.x - 20,
                                             (self.rect.y + self.image.get_size()[1] // 2)))

        elif self.moving_right:
            # function of centering character's weapon
            self.gun.image = self.gun_image
            self.gun.image = pygame.transform.rotate(self.gun.image, 360 - self.angle)
            if -55 <= self.angle < 0:
                self.strike_can = True
                SCREEN.blit(self.gun.image, (self.rect.x,
                                             (self.rect.y + self.image.get_size()[1] // 2) + self.angle // 2))
            elif -100 <= self.angle < -55:
                self.strike_can = True
                SCREEN.blit(self.gun.image, (self.rect.x - self.angle // 9,
                                             (self.rect.y + self.image.get_size()[1] // 2) + self.angle // 2))
            elif 0 < self.angle < 100:
                self.strike_can = True
                SCREEN.blit(self.gun.image, (self.rect.x,
                                             (self.rect.y + self.image.get_size()[1] // 2) - self.angle // 4))
            else:
                self.strike_can = False
                self.gun.image = self.gun_image
                SCREEN.blit(self.gun.image, (self.rect.x,
                                             (self.rect.y + self.image.get_size()[1] // 2)))

    def update(self, cube, cube_2, sprites, enemy_sprites, cat, luke):
        global user, cat_number
        # logic of moving and collision with different sprites
        if not self.home:
            self.move_gun()
        self.rect.x += self.move_x
        self.rect.y += self.move_y

        if (not pygame.sprite.spritecollideany(self, horizontal_borders)) and (
                not pygame.sprite.spritecollideany(self, vertical_borders)):
            self.rect.x -= self.move_x
            self.rect.y -= self.move_y
            self.rect.x += self.move_x
            if pygame.sprite.spritecollideany(self, sprites):
                self.rect.x -= self.move_x
            self.rect.y += self.move_y
            if pygame.sprite.spritecollideany(self, sprites):
                self.rect.y -= self.move_y
            self.rect.x -= self.move_x
            self.rect.y -= self.move_y
            if not pygame.sprite.collide_rect(cube, cube_2):
                self.rect.x += self.move_x
                if pygame.sprite.collide_rect(cube, cube_2):
                    self.heavy = 1 if self.move_x >= 0 else -1
                    self.rect.x -= self.move_x
                    self.rect.x += self.heavy
                    cube_2.move(self.heavy, 0)
                    if not cube_2.can_move(sprites, enemy_sprites):
                        cube_2.move(-self.heavy, 0)
                        self.rect.x -= self.heavy
                self.rect.y += self.move_y
                if pygame.sprite.collide_rect(cube, cube_2):
                    self.heavy = 1 if self.move_y >= 0 else -1
                    self.rect.y -= self.move_y
                    self.rect.y += self.heavy
                    cube_2.move(0, self.heavy)
                    if not cube_2.can_move(sprites, enemy_sprites):
                        cube_2.move(0, -self.heavy)
                        self.rect.y -= self.heavy
            else:
                self.rect.x += self.move_x
                self.rect.y += self.move_y
        else:
            self.rect.x -= self.move_x
            self.rect.y -= self.move_y
        if self.moving:
            self.update_frame()
        else:
            self.update_frame(True)
        if not self.home:
            if pygame.sprite.collide_mask(self, cat):
                if not self.catch_cat:
                    cat_number = cat.number
                    # user.caught_cat += cat.number
                cat.kill()
                self.catch_cat = True
                self.frames = DICT_IMAGES[f'hero_frames_{user.skin}_bag']
        if pygame.sprite.collide_rect(self, luke):
            self.on_the_luke = True
        else:
            self.on_the_luke = False
        self.move_x = 0
        self.move_y = 0
        cube.moving = False


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, gun, frames, hero=None, *groups: AbstractGroup):
        super().__init__(all_sprites, *groups)
        self.frames = frames
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 2
        self.speed_y = 2

        self.health = 100

        self.hero = hero

        self.angle = 0
        self.strike_distance = 350
        self.stop_distance = self.strike_distance - random.randrange(200, 250)
        self.d = self.stop_distance
        self.can_strike = True

        self.moving = False
        self.moving_left = False
        self.moving_right = True
        self.move_x = 0
        self.move_y = 0
        self.move_x_v = 2
        self.move_y_v = 2

        self.gun = gun  # <<gun>> class

        self.gun_image = gun.image

        self.count = 0
        self.fires_list = []

        self.dead = False
        self.dead_anim_end = False

    def update_frame(self, dead=False):
        if not dead:
            if not self.moving:
                if self.moving_left:
                    self.image = pygame.transform.flip(self.frames[self.cur_frame // 4], True, False)
                elif self.moving_right:
                    self.image = self.frames[self.cur_frame // 4]
            else:
                self.cur_frame += 1
                if self.cur_frame > 19:
                    self.cur_frame = 0
            if self.moving_left:
                self.image = pygame.transform.flip(self.frames[self.cur_frame // 4], True, False)
            elif self.moving_right:
                self.image = self.frames[self.cur_frame // 4]
        else:
            self.cur_frame += 1
            if self.cur_frame > 23:
                self.kill()
            if self.moving_left:
                self.image = pygame.transform.flip(self.frames[self.cur_frame // 4], True, False)
            elif self.moving_right:
                self.image = self.frames[self.cur_frame // 4]

    def update(self, camera):
        if not self.dead:
            self.move_gun(camera)
            if self.moving:
                # logic of moving
                dl_x = self.hero.rect.x - self.rect.x
                dl_y = self.hero.rect.y - self.rect.y

                self.move_x = self.speed_x if dl_x >= 0 else -self.speed_x
                self.move_y = self.speed_y if dl_y >= 0 else -self.speed_y

                if abs(dl_x) >= abs(dl_y):
                    self.rect.x += self.move_x
                    self.move_x_v = self.move_x
                    if pygame.sprite.spritecollideany(self, unmoving_sprites):
                        self.rect.x -= self.move_x
                        self.rect.y += self.move_y_v
                        if pygame.sprite.spritecollideany(self, unmoving_sprites):
                            self.rect.y -= self.move_y_v
                            self.move_y_v = -self.move_y_v
                        self.stop_distance = 0
                    else:
                        self.stop_distance = self.d
                else:
                    self.rect.y += self.move_y
                    self.move_y_v = self.move_y
                    if pygame.sprite.spritecollideany(self, unmoving_sprites):
                        self.rect.y -= self.move_y
                        self.rect.x += self.move_x_v
                        if pygame.sprite.spritecollideany(self, unmoving_sprites):
                            self.rect.x -= self.move_x_v
                            self.move_x_v = -self.move_x_v
                        self.stop_distance = 0
                    else:
                        self.stop_distance = self.d
            self.update_frame()
            self.render_health()
            self.move_x = 0
            self.move_y = 0
        else:
            self.update_frame(dead=True)

    def render_health(self):
        pygame.draw.rect(SCREEN, pygame.Color('red'),
                         (self.rect.x, self.rect.y - 10, abs(self.health) / (100 / 46), 10))

    def move_gun(self, camera):

        x_hero = self.hero.rect.x + self.hero.image.get_rect()[2] // 2
        y_hero = self.hero.rect.y + self.hero.image.get_rect()[3] // 2
        x = self.rect.x + self.image.get_rect()[2] // 2
        y = self.rect.y + self.image.get_rect()[3] // 2
        #
        # self.stop_distance = self.strike_distance - random.randrange(120, 150)

        if ((x_hero - x) ** 2 + (y_hero - y) ** 2) ** 0.5 < self.strike_distance + 50:
            if (x_hero - x) < 0:
                self.moving_left = True
                self.moving_right = False
            else:
                self.moving_left = False
                self.moving_right = True

        if self.moving_left:
            repeat = True
            if ((x_hero - x) ** 2 + (y_hero - y) ** 2) ** 0.5 < self.strike_distance:
                if (((x_hero - x) ** 2 + (y_hero - y) ** 2) ** 0.5) < (self.strike_distance - 100):
                    self.moving = True
                    self.fire(x, y, x_hero, y_hero, camera, True)
                    repeat = False  # отрисовка пуль без повторов
                if (((x_hero - x) ** 2 + (y_hero - y) ** 2) ** 0.5) < self.stop_distance:
                    self.moving = False

                # function of centering character's weapon

                angleR = math.atan2(y_hero - y,
                                    x_hero - x)
                self.angle = angleR * 180 / math.pi

                self.gun.image = pygame.transform.flip(self.gun_image, True, False)
                self.gun.image = pygame.transform.rotate(self.gun.image, -90)
                if self.angle <= -80:
                    self.gun.image = pygame.transform.rotate(self.gun.image, 360 - (self.angle + 90))
                    SCREEN.blit(self.gun.image, (self.rect.x - 20,
                                                 (self.rect.y + self.image.get_size()[1] // 2 - (
                                                         90 + (self.angle + 90)) // 4)))
                elif 90 <= self.angle <= 180:
                    self.gun.image = pygame.transform.rotate(self.gun.image, 360 - (self.angle + 90))
                    SCREEN.blit(self.gun.image, ((self.rect.x - 20) - 1 * (self.angle - 180) // 4,
                                                 (self.rect.y + self.image.get_size()[1] // 2 + 1 * (
                                                         self.angle - 180) // 4)))
                # it's need to solve the problem with repeating shots
                if repeat:
                    self.fire(x, y, x_hero, y_hero, camera)
            else:
                self.fire(x, y, x_hero, y_hero, camera)

        elif self.moving_right:
            repeat = True
            if ((x_hero - x) ** 2 + (y_hero - y) ** 2) ** 0.5 < self.strike_distance:
                if (((x_hero - x) ** 2 + (y_hero - y) ** 2) ** 0.5) < (self.strike_distance - 100):
                    self.moving = True
                    self.fire(x, y, x_hero, y_hero, camera, True)
                    repeat = False  # отрисовка пуль без повторов
                if (((x_hero - x) ** 2 + (y_hero - y) ** 2) ** 0.5) < self.stop_distance:
                    self.moving = False

                # function of centering character's weapon
                angleR = math.atan2(y_hero - y,
                                    x_hero - x)
                self.angle = angleR * 180 / math.pi

                self.gun.image = self.gun_image
                self.gun.image = pygame.transform.rotate(self.gun.image, 360 - self.angle)
                if -55 <= self.angle < 0:
                    SCREEN.blit(self.gun.image, (self.rect.x,
                                                 (self.rect.y + self.image.get_size()[1] // 2) + self.angle // 2))
                elif -100 <= self.angle < -55:
                    SCREEN.blit(self.gun.image, (self.rect.x - self.angle // 9,
                                                 (self.rect.y + self.image.get_size()[1] // 2) + self.angle // 2))
                elif 0 < self.angle < 100:
                    SCREEN.blit(self.gun.image, (self.rect.x,
                                                 (self.rect.y + self.image.get_size()[1] // 2) - self.angle // 4))
                if repeat:
                    self.fire(x, y, x_hero, y_hero, camera)
            else:
                self.fire(x, y, x_hero, y_hero, camera)

    def fire(self, x, y, x_2, y_2, camera, status=False):
        if status:
            self.count += 1
            # 15 - it's the speed of shooting. The higher the number, the slower the shooting
            if self.count % 15 == 0:
                self.count = 0
                self.fires_list.append(
                    [
                        math.atan2(y_2 - y,
                                   x_2 - x),
                        x - 10,
                        y,
                        x,
                        y,
                        True
                    ]
                )
        for x, elem in enumerate(self.fires_list):
            sX = math.cos(elem[0]) * 20
            sY = math.sin(elem[0]) * 20

            elem[1] += sX
            elem[2] += sY

            dl_x, dl_y = camera.apply(pref='p', x=elem[1], y=elem[2])

            elem[1] = dl_x
            elem[2] = dl_y

            dl_x, dl_y = camera.apply(pref='p', x=elem[3], y=elem[4])

            elem[3] = dl_x
            elem[4] = dl_y

            x_ = elem[1] - elem[3]
            y_ = elem[2] - elem[4]

            sprite = pygame.sprite.Sprite()

            image = pygame.Surface((2 * 5, 2 * 5),
                                   pygame.SRCALPHA, 32)
            sprite.image = image
            sprite.rect = sprite.image.get_rect()
            sprite.rect.x = elem[1]
            sprite.rect.y = elem[2]

            if (x_ ** 2 + y_ ** 2) ** 0.5 > 80:
                if elem[5]:
                    shoot.play()
                    elem[5] = False

            if (x_ ** 2 + y_ ** 2) ** 0.5 > 320:
                self.fires_list.remove(elem)
            elif pygame.sprite.collide_rect(sprite, self.hero):
                # logic of shot's sound
                if elem[5]:
                    shoot.play()
                    elem[5] = False
                self.hero.health -= max(self.gun.power - 5, 5)
                self.fires_list.remove(elem)
            elif pygame.sprite.spritecollideany(sprite, horizontal_borders) or pygame.sprite.spritecollideany(sprite,
                                                                                                              vertical_borders):
                self.fires_list.remove(elem)
            elif pygame.sprite.spritecollideany(sprite, sprites_) or pygame.sprite.collide_rect(sprite, moving_cube):

                self.fires_list.remove(elem)
            else:
                pygame.draw.circle(image, pygame.Color("red"),
                                   (5, 5), 5)
            if (x_ ** 2 + y_ ** 2) ** 0.5 > 50:
                SCREEN.blit(image, [elem[1], elem[2]])


# <<groundtexture>> class. Bacground texture in the game
class GroundTexture(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, d):
        super().__init__(ground_sprites, all_sprites)
        self.image = DICT_IMAGES[tile_type]
        self.width = d
        self.height = d
        self.rect = self.image.get_rect().move(
            self.width * pos_x, self.height * pos_y)


# <<cube>> class
class Cube(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y, image=DICT_IMAGES['box'], type=None, *groups: AbstractGroup):
        super().__init__(all_sprites, *groups)
        self.image = image if type is None else DICT_IMAGES['stone_block']
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 0
        self.speed_y = 0

        self.move_x = 0
        self.move_y = 0

    def can_move(self, *sprite_args):
        for sprite_lst in sprite_args:
            if pygame.sprite.spritecollideany(self, sprite_lst):
                return False
        return True

    def move(self, move_x, move_y):
        self.rect.x += move_x
        self.rect.y += move_y


# <<moving_cube>> - it's the cube with texture of a big stone which you can move.
moving_cube = None


# <<border>> class. (game map border)
class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2, pos):
        super().__init__(all_sprites)
        if x1 == x2:  # вертикальная стенка
            if pos == 'l':
                self.add(vertical_borders)
                self.image = pygame.Surface([50, y2 - y1])
                self.rect = pygame.Rect(x1 - 50, y1, 50, y2 - y1)
            elif pos == 'r':
                self.add(vertical_borders)
                self.image = pygame.Surface([50, y2 - y1])
                self.rect = pygame.Rect(x1 + 60, y1, 50, y2 - y1)
        else:  # горизонтальная стенка
            if pos == 't':
                self.add(horizontal_borders)
                self.image = pygame.Surface([x2 - x1, 50])
                self.rect = pygame.Rect(x1, y1 - 50, x2 - x1, 50)
            elif pos == 'b':
                self.add(horizontal_borders)
                self.image = pygame.Surface([x2 - x1, 50])
                self.rect = pygame.Rect(x1, y1 + 60, x2 - x1, 50)


# initialization of weapon
dict_weapon = {
    'ak47': Gun(power=15, ammo=25, gun_image=DICT_IMAGES['ak47']),
    'm4a1': Gun(power=30, ammo=20, gun_image=DICT_IMAGES['m4a1'])
}


# <<button>> class
class Button:
    def __init__(self, width, height, inactive_color, active_color):
        self.width = width
        self.height = height
        self.inactive_color = inactive_color
        self.active_color = active_color

    def draw(self, x, y, message, dl_x=10, dl_y=10, action=None, font_size=30, gun=None, skin=None, price=None, buy=None):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pygame.draw.rect(SCREEN, self.active_color, (x, y, self.width, self.height))
            print_text(text=message, color=self.inactive_color, x=x + 10, y=y + 10, font=font_size)
            if click[0] == 1 and action is not None:
                if buy is not None:
                    if buy:
                        if skin is not None:
                            action(skin, price)
                        else:
                            action(gun, price)
                    else:
                        if skin is not None:
                            action(skin)
                        else:
                            action(gun)
                else:
                    action()

        else:
            pygame.draw.rect(SCREEN, self.inactive_color, (x, y, self.width, self.height))
            print_text(text=message, color=self.active_color, x=x + dl_x, y=y + dl_y, font=font_size)


# <<camera>> class
class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj=None, pref=None, x=0, y=0):
        if pref is None:
            obj.rect.x += self.dx
            obj.rect.y += self.dy
        else:
            return x + self.dx, y + self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


# one of the main fuctions which places game objects.
def init_frames(map):
    global moving_cube, hero, cat, luke, lamp

    if map == 'game_map_4.txt':
        d = 50
        image = 'ground_sand'
    else:
        d = 86
        image = 'ground_ender'
    for y in range((2000 // d) + 1):
        for x in range((2000 // d) + 1):
            GroundTexture(image, x, y, d)

    world = []
    file = open(fr'data\levels\{map}', 'r')
    for line in file:
        line = line.strip()
        arr = []
        for elem in line:
            try:
                arr.append(int(elem))
            except ValueError:
                arr.append(elem)
        world.append(arr)
    file.close()

    boxes = []
    ground = []
    cube_r = []
    enemies = []
    hero_l = []
    cat_l = []
    luke_l = []
    lamp_l = []

    for row in range(len(world)):
        for col in range(len(world[row])):
            x, y = col * 10, row * 10

            if world[row][col] == 1 or world[row][col] == 7 or world[row][col] == 'h' or world[row][col] == 'j':
                boxes.append((x, y, world[row][col]))
            elif world[row][col] == 2:
                cube_r.append((x, y))
            elif world[row][col] == 3:
                enemies.append((x, y))
            elif world[row][col] == 4:
                hero_l.append((x, y))
            elif world[row][col] == 5 or world[row][col] == 6 or world[row][col] == 8 \
                    or world[row][col] == 'd' or world[row][col] == 'q' or world[row][col] == 'a':
                ground.append((x, y, world[row][col]))
            elif world[row][col] == 9:
                cat_l.append((x, y))
            elif world[row][col] == 'l':
                luke_l.append((x, y))
            elif world[row][col] == 'w':
                lamp_l.append((x, y))

    for elem in ground:
        image = DICT_IMAGES['ground_sand']
        if elem[2] == 6:
            image = DICT_IMAGES['ground_stone']
        elif elem[2] == 8:
            image = DICT_IMAGES['branch']
        elif elem[2] == 'd':
            image = DICT_IMAGES['tree_block']
        elif elem[2] == 'q':
            image = DICT_IMAGES['red_block']
        elif elem[2] == 'a':
            image = DICT_IMAGES['white_block']

        cube = Cube(width=50, height=50, x=elem[0], y=elem[1],
                    image=image)
        sprites.add(cube)

    for elem in luke_l:
        luke = Cube(width=80, height=80, x=elem[0],
                    y=elem[1], image=DICT_IMAGES['luke'] if map != 'home.txt' else DICT_IMAGES['luke_h'])
        sprites.add(luke)

    for elem in lamp_l:
        lamp = Cube(width=80, height=80, x=elem[0], y=elem[1], image=DICT_IMAGES['lamp'])
        sprites.add(lamp)

    if len(cat_l) == 0:
        if not user.caught_cat is None:
            for x, i in enumerate(user.caught_cat, 0):
                sprites.add(Cat(410 + (150 * x), 240, frames=DICT_IMAGES['cat' + i], number=i))
    else:
        for elem in cat_l:
            n = str(random.randint(1, 2))
            cat = Cat(elem[0], elem[1], frames=DICT_IMAGES['cat' + n], number=n)
            sprites.add(cat)

    for elem in hero_l:
        gun = None
        hero = Hero(elem[0], elem[1], gun=dict_weapon[user.gun], frames=DICT_IMAGES['hero_frames_' + user.skin])
        sprites.add(hero)

    for elem in enemies:
        enemy = Enemy(elem[0], elem[1], gun=dict_weapon['ak47'],
                      frames=DICT_IMAGES['enemy_frames'], hero=hero)
        enemy_sprites.add(enemy)

    for elem in boxes:
        image = DICT_IMAGES['box']
        if elem[2] == 7:
            image = DICT_IMAGES['bush']
        elif elem[2] == 'h':
            image = DICT_IMAGES['wood-block']
        elif elem[2] == 'j':
            image = DICT_IMAGES['fire']
        cube = Cube(width=50, height=50, x=elem[0], y=elem[1],
                    image=image)
        sprites.add(cube)
        sprites_.add(cube)
        unmoving_sprites.add(cube)

    for elem in cube_r:
        moving_cube = Cube(width=50, height=50, x=elem[0], y=elem[1], type='moving_cube')
        sprites.add(moving_cube)
        unmoving_sprites.add(moving_cube)


# function of printing a text
def print_text(text, color, font, x=None, y=None, center=False):
    font = pygame.font.Font(None, font)
    text = font.render(text, True, color)
    if x is None and y is None:
        text_x = WIDTH // 2 - text.get_width() // 2
        text_y = HEIGHT // 2 - text.get_height() // 2
    elif not center:
        text_x = x
        text_y = y
    else:
        text_x = WIDTH // 2 - text.get_width() // 2 - x
        text_y = HEIGHT // 2 - text.get_height() // 2 - y
    SCREEN.blit(text, (text_x, text_y))


# function of exit
def terminate():
    dump_json()  # save statistics
    pygame.quit()
    sys.exit()


# show <<user>> statistics
def show_stat():
    paused = True
    btn = Button(150, 50, active_color=(255, 255, 255), inactive_color=(255, 202, 134))
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                paused = False
        pygame.draw.rect(SCREEN, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
        print_text("STATA.", (255, 255, 255), 75, x=0, y=90, center=True)
        print_text(f"level: {user.level}    coins: {user.coins}", (255, 202, 134), 50, x=0, y=40, center=True)
        print_text(f"kills: {user.kills}    restarts: {user.restarts}", (255, 202, 134), 50, x=0, y=5, center=True)
        print_text(f"ammo spend: {user.ammo_spend}", (255, 202, 134), 50, x=150, y=-30, center=True)
        print_text(f"game replays: {user.game_replays}", (255, 202, 134), 50, x=-150, y=-30, center=True)
        btn.draw(WIDTH // 2 - 75, HEIGHT // 2 + 70, dl_x=45, dl_y=18, message='BACK', action=show_menu, font_size=30)
        pygame.display.flip()
        CLOCK.tick(FPS)


# function of pause in the game
def pause(value=False):
    paused = True
    button = Button(100, 50, active_color=(255, 255, 255), inactive_color=(229, 190, 1))
    play = False
    pause_ = False
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                paused = False
                if value:
                    play = True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pause_ = True
                paused = False
        if value:
            keys = pygame.key.get_pressed()
            if user.control:
                if keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w] or keys[pygame.K_s]:
                    paused = False
                    play = False
            else:
                if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                    paused = False
                    play = False

        pygame.draw.rect(SCREEN, (21, 23, 25), (WIDTH // 2 - 300, HEIGHT // 2 - 80, 600, 230))
        if not value:
            print_text("PAUSED.", (243, 165, 5), 75, x=0, y=30, center=True)
            print_text("PRESS ENTER TO CONTINUE", (255, 202, 134), 50, x=0, y=-30, center=True)
            button.draw(x=WIDTH // 2 - 50, y=HEIGHT // 2 + 75, message='МЕНЮ', action=show_menu, dl_x=15, dl_y=15)
        if value:
            print_text(f"LEVEL {user.level}.", (243, 165, 5), 75, x=0, y=30, center=True)
            print_text("PRESS ENTER TO START", (255, 202, 134), 50, x=0, y=-30, center=True)
            button.draw(x=WIDTH // 2 - 50, y=HEIGHT // 2 + 75, message='МЕНЮ', action=show_menu, dl_x=15, dl_y=15)
        pygame.display.flip()
        CLOCK.tick(FPS)
    if pause_:
        pause()
    if play:
        return True
    return False


# function to print <<user>> info
def print_info(home):
    font = pygame.font.SysFont('monserat', 25)
    text = font.render("hero health:", True, pygame.Color(127, 255, 0))
    text_x = WIDTH // 2 - text.get_width() // 2 - 55
    text_y = HEIGHT - text.get_height()
    pygame.draw.rect(SCREEN, pygame.Color(0, 0, 0),
                     (0, HEIGHT - 18, WIDTH, 25))
    pygame.draw.rect(SCREEN, pygame.Color(127, 255, 0),
                     (WIDTH // 2, HEIGHT - text.get_height() + 4, abs(hero.health), 10))
    if not home:
        print_text(F'Ammo: {hero.gun.ammo_now}', color=(243, 165, 5), x=0, y=HEIGHT - text.get_height(), font=25)
        # self.catch_cat = False
        # self.on_the_luke = False
        if hero.on_the_luke and hero.catch_cat:
            text_ = font.render("RUN AWAY | PRESS <<ENTER>>", True, pygame.Color(255, 255, 255))
        elif hero.catch_cat:
            text_ = font.render("FIND THE LUKE", True, pygame.Color(255, 255, 255))
        else:
            text_ = font.render("FIND AND SAVE THE CAT", True, pygame.Color(255, 255, 255))
        SCREEN.blit(text_, (WIDTH - text_.get_width(), HEIGHT - text_.get_height()))
    if hero.gun.wait != 0:
        print_text(F'reloading: {hero.gun.wait}%', color=(243, 165, 5), x=100, y=HEIGHT - text.get_height(), font=25)
    pygame.draw.rect(SCREEN, pygame.Color(127, 255, 0),
                     (WIDTH // 2, HEIGHT - text.get_height() + 4, abs(hero.health), 10))
    SCREEN.blit(text, (text_x, text_y))


# one of the main functions. level function
def main_action():
    global congratulations, restarts, cat_number
    running = True

    init_frames(LEVELS[user.level - 1])

    Border(-50, 0, 2100, 0, 't')
    Border(-50, 2000, 2100, 2000, 'b')
    Border(0, 0, 0, 2100, 'l')
    Border(2000, 0, 2000, 2100, 'r')

    camera = Camera()

    firesList = []

    win = False
    hero.home = False
    if user.level == 1:
        user.caught_cat = ''

    kills = 0
    ammo_spend = 0
    # control using wasd TRUE|FALSE
    control_wasd = user.control
    while running:
        SCREEN.fill(pygame.Color('black'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEMOTION:
                mousePos['x'], mousePos['y'] = pygame.mouse.get_pos()
                x = hero.rect.x + hero.image.get_rect()[2] // 2
                y = hero.rect.y + hero.image.get_rect()[3] // 2
                angleR = math.atan2(mousePos['y'] - y,
                                    mousePos['x'] - x)
                hero.angle = angleR * 180 / math.pi
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hero.gun is not None:
                    mousePos['x'], mousePos['y'] = pygame.mouse.get_pos()
                    x = hero.rect.x + hero.image.get_rect()[2] // 2
                    y = hero.rect.y + hero.image.get_rect()[3] // 2
                    angleR = math.atan2(mousePos['y'] - y,
                                        mousePos['x'] - x)
                    if hero.strike_can:
                        if hero.gun.ammo_now == 0:
                            continue
                        hero.gun.ammo_now -= 1
                        user.ammo_spend += 1
                        ammo_spend += 1
                        # added a shot to list
                        firesList.append(
                            [
                                angleR,
                                x - 10,
                                y,
                                x,
                                y
                            ]
                        )
                        # sound of shot
                        shoot.play()

        # camera
        if hero.gun.ammo_now == 0:
            if not hero.reloading:
                hero.reloading = True
                reloading.play()
            hero.gun.wait += 1
            # reload_function
            if hero.gun.wait_max == hero.gun.wait:
                hero.gun.ammo_now = hero.gun.ammo
                hero.gun.wait = 0
                hero.reloading = False

        camera.update(hero)
        for sprite in all_sprites:
            camera.apply(sprite)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            if hero.catch_cat and hero.on_the_luke:
                # add coins to user
                coins = user.level * 2 + 24
                coins += kills * 2
                if restarts == 0:
                    coins += 10
                elif 1 <= restarts <= 2:
                    coins += 4
                user.coins += coins
                # new level logic
                user.new_level()
                if user.level == len(LEVELS) + 1:
                    user.level = 1
                    user.game_replays += 1
                    congratulations = True
                win = True
                running = False
        if keys[pygame.K_r]:
            if hero.gun.wait == 0:
                hero.gun.ammo_now = 0
        if control_wasd:
            up = pygame.K_w
            down = pygame.K_s
            left = pygame.K_a
            right = pygame.K_d
        else:
            up = pygame.K_UP
            down = pygame.K_DOWN
            left = pygame.K_LEFT
            right = pygame.K_RIGHT
        if keys[left]:
            hero.moving = True
            hero.moving_left = True
            hero.moving_right = False
            hero.move_x -= hero.speed_x
        if keys[right]:
            hero.moving = True
            hero.moving_left = False
            hero.moving_right = True
            hero.move_x += hero.speed_x
        if keys[up]:
            hero.moving = True
            hero.move_y -= hero.speed_y
        if keys[down]:
            hero.moving = True
            hero.move_y += hero.speed_y

        hero.sound_walk()
        cat.sound_meow(hero)

        ground_sprites.draw(SCREEN)
        sprites.draw(SCREEN)
        enemy_sprites.draw(SCREEN)
        sprites.update(hero, moving_cube, sprites_, enemy_sprites, cat, luke)
        enemy_sprites.update(camera)
        # drawing shooting
        for elem in firesList:
            sX = math.cos(elem[0]) * 30
            sY = math.sin(elem[0]) * 30

            elem[1] += sX
            elem[2] += sY

            dl_x, dl_y = camera.apply(pref='p', x=elem[1], y=elem[2])

            elem[1] = dl_x
            elem[2] = dl_y

            dl_x, dl_y = camera.apply(pref='p', x=elem[3], y=elem[4])

            elem[3] = dl_x
            elem[4] = dl_y

            x_ = elem[1] - elem[3]
            y_ = elem[2] - elem[4]

            sprite = pygame.sprite.Sprite()

            image = pygame.Surface((2 * 5, 2 * 5),
                                   pygame.SRCALPHA, 32)
            sprite.image = image
            sprite.rect = sprite.image.get_rect()
            sprite.rect.x = elem[1]
            sprite.rect.y = elem[2]

            if (x_ ** 2 + y_ ** 2) ** 0.5 > 230:
                firesList.remove(elem)
            elif pygame.sprite.spritecollideany(sprite, enemy_sprites):
                lst = pygame.sprite.spritecollide(sprite, enemy_sprites, False)
                for person in pygame.sprite.spritecollide(sprite, enemy_sprites, False):
                    person.health -= hero.gun.power
                    if person.health <= 0 and not person.dead:
                        person.dead = True
                        person.frames = DICT_IMAGES['death_frames']
                        person.cur_frame = 0
                        user.kills += 1
                        kills += 1
                firesList.remove(elem)
            elif pygame.sprite.spritecollideany(sprite, horizontal_borders) or pygame.sprite.spritecollideany(sprite,
                                                                                                              vertical_borders):
                firesList.remove(elem)
            elif pygame.sprite.spritecollideany(sprite, sprites_) or pygame.sprite.collide_rect(sprite, moving_cube):
                firesList.remove(elem)
            else:
                pygame.draw.circle(image, pygame.Color("orange"),
                                   (5, 5), 5)
            if (x_ ** 2 + y_ ** 2) ** 0.5 > 50:
                SCREEN.blit(image, [elem[1], elem[2]])
        print_info(hero.home)
        if keys[pygame.K_ESCAPE]:
            pause()
        if hero.health <= 0:
            running = False
        CLOCK.tick(FPS)
        pygame.display.flip()
    if win:
        user.caught_cat += cat_number
        return game_over_win(True, coins)
    user.restarts += 1
    restarts += 1
    return game_over_win()


# window which shows when you lose or win
def game_over_win(value=False, coins=0):
    stopped = True
    button_lose = Button(100, 50, active_color=(255, 255, 255), inactive_color=(180, 76, 67))
    button_win = Button(100, 50, active_color=(255, 255, 255), inactive_color=(76, 187, 23))
    while stopped:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return True
        if value == 'access':
            return True
        pygame.draw.rect(SCREEN, (21, 23, 25), (WIDTH // 2 - 300, HEIGHT // 2 - 80, 600, 230))
        if value is False:
            print_text("YOU LOSE.", (255, 0, 51), 75, x=0, y=30, center=True)
            print_text("PRESS ENTER TO RETURN HOME", (217, 80, 48), 50, x=0, y=-30, center=True)
            button_lose.draw(x=WIDTH // 2 - 50, y=HEIGHT // 2 + 75, message='МЕНЮ', action=show_menu, dl_x=15, dl_y=15)
        elif value is True:
            print_text("YOU WIN.", (124, 252, 0), 75, x=0, y=30, center=True)
            print_text(f"YOU ERNED {coins} COINS", 'gold', 50, x=0, y=-20, center=True)
            print_text("PRESS ENTER TO CONTINUE", (189, 218, 87), 45, x=0, y=-60, center=True)
            button_win.draw(x=WIDTH // 2 - 50, y=HEIGHT // 2 + 75, message='МЕНЮ', action=show_menu, dl_x=15, dl_y=20)

        pygame.display.flip()
        CLOCK.tick(FPS)


def show_setting_menu():
    paused = True
    btn = Button(150, 50, active_color=(255, 255, 255), inactive_color=(255, 202, 134))
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                paused = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = pygame.mouse.get_pos()
                if (WIDTH // 2 + 49 <= x <= WIDTH // 2 + 221) and (HEIGHT // 2 - 1 <= y <= HEIGHT // 2 + 113):
                    user.control = True
                elif (WIDTH // 2 - 225 <= x <= WIDTH // 2 - 53) and (HEIGHT // 2 - 1 <= y <= HEIGHT // 2 + 113):
                    user.control = False

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_UP]:
            pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() + 0.01)
        elif key_pressed[pygame.K_DOWN]:
            pygame.mixer.music.set_volume(pygame.mixer.music.get_volume() - 0.01)

        pygame.draw.rect(SCREEN, (0, 0, 0), (0, 0, WIDTH, HEIGHT))
        print_text("SETTINGS.", (255, 255, 255), 75, x=0, y=180, center=True)
        print_text(f"THE VOLUME OF MUSIC: {round(pygame.mixer.music.get_volume() * 100)}",
                   color=(255, 202, 134), font=40, x=0, y=120, center=True)
        print_text("KEY UP + | KEY DOWN -", (255, 255, 255), 20, x=0, y=90, center=True)
        user.menu_music_volume = pygame.mixer.music.get_volume()

        # left side
        print_text(f"CONTROL", color=(255, 202, 134), font=40, x=0, y=30, center=True)
        SCREEN.blit(DICT_IMAGES['keys_wasd'], (WIDTH // 2 + 50, HEIGHT // 2))
        # right sided
        SCREEN.blit(DICT_IMAGES['keys_arrows'], (WIDTH // 2 - 224, HEIGHT // 2))

        if user.control:
            pygame.draw.rect(SCREEN, (255, 255, 255), (WIDTH // 2 + 49, HEIGHT // 2 - 1, 172, 114), width=2)
        else:
            pygame.draw.rect(SCREEN, (255, 255, 255), (WIDTH // 2 - 225, HEIGHT // 2 - 1, 172, 114), width=2)
        btn.draw(WIDTH // 2 - 75, HEIGHT // 2 + 150, dl_x=45, dl_y=18, message='BACK', action=show_menu, font_size=30)
        pygame.display.flip()
        CLOCK.tick(FPS)


# window which shows when you passed the game
def congratulations_window():
    paused = True
    button = Button(100, 50, active_color=(255, 255, 255), inactive_color=(76, 187, 23))
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                paused = False

        pygame.draw.rect(SCREEN, (21, 23, 25), (WIDTH // 2 - 300, HEIGHT // 2 - 80, 600, 230))
        print_text("YOU PASSED THE GAME.", (124, 252, 0), 60, x=0, y=30, center=True)
        print_text("IF YOU WANT TO CONTINUE YOU'LL START OVER", (189, 218, 87), 30, x=0, y=-20, center=True)
        print_text("PRESS ENTER TO CONTINUE", (189, 218, 87), 20, x=0, y=-50, center=True)
        button.draw(x=WIDTH // 2 - 50, y=HEIGHT // 2 + 75, message='МЕНЮ', action=show_menu, dl_x=15, dl_y=15)
        pygame.display.update()
        CLOCK.tick(FPS)


# show main menu
def show_menu():
    global from_game
    if from_game:
        pygame.mixer.music.play(-1)
        from_game = False
    menu_background = DICT_IMAGES['menu_bg']

    btn = Button(200, 100, active_color=(255, 255, 255), inactive_color=(0, 0, 0))
    settings_btn = Button(150, 50, active_color=(255, 255, 255), inactive_color=(0, 0, 0))
    dl_x = -50
    show = True
    while show:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        SCREEN.blit(menu_background, (0, 0))
        btn.draw(150 + dl_x, 80, dl_x=35, dl_y=25, message='PLAY.', action=start_game, font_size=70)
        settings_btn.draw(175 + dl_x, 205, dl_x=25, dl_y=18, message='SETTINGS.', action=show_setting_menu, font_size=30)
        settings_btn.draw(175 + dl_x, 280, dl_x=40, dl_y=18, message='STATА.', action=show_stat, font_size=30)
        settings_btn.draw(175 + dl_x, 355, dl_x=50, dl_y=18, message='EXIT.', action=terminate, font_size=30)
        pygame.display.update()
        CLOCK.tick(FPS)


def use_skin(skin):
    user.skin = skin
    hero.frames = DICT_IMAGES['hero_frames_' + user.skin]


def buy_skin(skin, price):
    if user.coins >= price:
        user.coins -= price
        user.skins_have.append(skin)


def use_gun(gun):
    user.gun = gun
    hero.change_gun(dict_weapon[user.gun])


def buy_gun(gun, price):
    if user.coins >= price:
        user.coins -= price
        user.gun_have.append(gun)


def shop_menu():
    show = True
    # for skins
    buy_default = Button(80, 35, active_color=(255, 255, 255), inactive_color='green')
    dl_x = 20
    dl_y = 100
    while show:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                show = False
        SCREEN.fill((0, 0, 0))
        print_text(f'COINS: {user.coins}', color='gold', font=35, x=437, y=58)
        # skins
        print_text('SKINS', color=(255, 255, 255), font=50, x=150, y=50)
        SCREEN.blit(DICT_IMAGES['hero_frames_default'][0], (100, 100))
        print_text("default", color=(255, 255, 255), font=20, x=100, y=168)
        print_text(text='used' if user.skin == 'default' else '', color='green', font=20, x=275, y=160)
        print_text('price: 0', color=(255, 255, 255), font=30, x=150, y=130)
        buy_default.draw(x=250, y=120, message='BUY' if 'default' not in user.skins_have else 'USE',
                         font_size=24, action=buy_skin if 'default' not in user.skins_have else use_skin,
                         skin='default', price=0, buy=True if 'default' not in user.skins_have else False)

        SCREEN.blit(DICT_IMAGES['hero_frames_colorit'][0], (100, 100 + dl_y))
        print_text("colorit", color=(255, 255, 255), font=20, x=100, y=168 + dl_y)
        print_text(text='used' if user.skin == 'colorit' else '', color='green', font=20, x=275, y=160 + dl_y)
        print_text('price: 75', color=(255, 255, 255), font=30, x=150, y=130 + dl_y)
        buy_default.draw(x=250, y=120 + dl_y, message='BUY' if 'colorit' not in user.skins_have else 'USE',
                         font_size=24, action=buy_skin if 'colorit' not in user.skins_have else use_skin,
                         skin='colorit', price=75, buy=True if 'colorit' not in user.skins_have else False)

        SCREEN.blit(DICT_IMAGES['hero_frames_radiation'][0], (100, 100 + dl_y * 2))
        print_text("radiation", color=(255, 255, 255), font=20, x=98, y=168 + dl_y * 2)
        print_text(text='used' if user.skin == 'radiation' else '', color='green', font=20, x=275, y=160 + dl_y * 2)
        print_text('price: 100', color=(255, 255, 255), font=30, x=150, y=130 + dl_y * 2)
        buy_default.draw(x=250, y=120 + dl_y * 2, message='BUY' if 'radiation' not in user.skins_have else 'USE',
                         font_size=24, action=buy_skin if 'radiation' not in user.skins_have else use_skin,
                         skin='radiation', price=100, buy=True if 'radiation' not in user.skins_have else False)

        SCREEN.blit(DICT_IMAGES['hero_frames_extra_pink'][0], (100, 100 + dl_y * 3))
        print_text("extra pink", color=(255, 255, 255), font=20, x=95, y=168 + dl_y * 3)
        print_text(text='used' if user.skin == 'extra_pink' else '', color='green', font=20, x=275, y=160 + dl_y * 3)
        print_text('price: 50', color=(255, 255, 255), font=30, x=150, y=130 + dl_y * 3)
        buy_default.draw(x=250, y=120 + dl_y * 3, message='BUY' if 'extra_pink' not in user.skins_have else 'USE',
                         font_size=24, action=buy_skin if 'extra_pink' not in user.skins_have else use_skin,
                         skin='extra_pink', price=50, buy=True if 'extra_pink' not in user.skins_have else False)
        # weapon
        print_text('WEAPON', color=(255, 255, 255), font=50, x=700, y=50)
        SCREEN.blit(DICT_IMAGES['ak47'], (650, 120))
        print_text('ak47', color=(255, 255, 255), font=20, x=670, y=160)
        print_text(f"power: {dict_weapon['ak47'].power}", color=(255, 255, 255), font=20, x=710, y=160)
        print_text(f"ammo: {dict_weapon['ak47'].ammo}", color=(255, 255, 255), font=20, x=780, y=160)
        print_text(text='used' if user.gun == 'ak47' else '', color='green', font=20, x=865, y=160)
        print_text('price: 0', color=(255, 255, 255), font=30, x=735, y=130)
        buy_default.draw(x=840, y=120, message='BUY' if 'ak47' not in user.gun_have else 'USE',
                         font_size=24, action=buy_gun if 'ak47' not in user.gun_have else use_gun,
                         gun='ak47', price=0, buy=True if 'ak47' not in user.gun_have else False)

        SCREEN.blit(DICT_IMAGES['m4a1'], (650, 120 + dl_y))
        print_text('m4a1', color=(255, 255, 255), font=20, x=670, y=160 + dl_y)
        print_text(f"power: {dict_weapon['m4a1'].power}", color=(255, 255, 255), font=20, x=710, y=160 + dl_y)
        print_text(f"ammo: {dict_weapon['m4a1'].ammo}", color=(255, 255, 255), font=20, x=780, y=160 + dl_y)
        print_text(text='used' if user.gun == 'm4a1' else '', color='green', font=20, x=865, y=160 + dl_y)
        print_text('price: 140', color=(255, 255, 255), font=30, x=735, y=130 + dl_y)
        buy_default.draw(x=840, y=120 + dl_y, message='BUY' if 'm4a1' not in user.gun_have else 'USE',
                         font_size=24, action=buy_gun if 'm4a1' not in user.gun_have else use_gun,
                         gun='m4a1', price=140, buy=True if 'm4a1' not in user.gun_have else False)

        print_text('PRESS ENTER TO EXIT', color=(255, 255, 255), font=20, x=WIDTH // 2 - 78, y=HEIGHT - 40)
        CLOCK.tick(FPS)
        pygame.display.flip()


# function of resetting values the variables
def reset():
    global ground_sprites, \
        enemy_sprites, all_sprites, vertical_borders, \
        horizontal_borders, sprites, sprites_, unmoving_sprites, mousePos, dict_weapon
    ground_sprites = pygame.sprite.Group()
    enemy_sprites = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    horizontal_borders = pygame.sprite.Group()
    sprites = pygame.sprite.Group()
    sprites_ = pygame.sprite.Group()
    unmoving_sprites = pygame.sprite.Group()
    mousePos = {'x': 0, 'y': 0}
    dict_weapon = {
        'ak47': Gun(power=15, ammo=30, gun_image=DICT_IMAGES['ak47']),
        'm4a1': Gun(power=30, ammo=20, gun_image=DICT_IMAGES['m4a1'])
    }


# one of the main functions. home level function
def home_action():
    global congratulations
    running = True

    init_frames('home.txt')

    Border(-50, 0, 2100, 0, 't')
    Border(-50, 2000, 2100, 2000, 'b')
    Border(0, 0, 0, 2100, 'l')
    Border(2000, 0, 2000, 2100, 'r')

    camera = Camera()

    hero.home = True
    #control using wasd TRUE|FALSE
    control_wasd = user.control
    while running:
        SCREEN.fill(pygame.Color('black'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        camera.update(hero)
        for sprite in all_sprites:
            camera.apply(sprite)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            if pygame.sprite.collide_rect(hero, lamp):
                shop_menu()
        if control_wasd:
            up = pygame.K_w
            down = pygame.K_s
            left = pygame.K_a
            right = pygame.K_d
        else:
            up = pygame.K_UP
            down = pygame.K_DOWN
            left = pygame.K_LEFT
            right = pygame.K_RIGHT
        if keys[left]:
            hero.moving = True
            hero.moving_left = True
            hero.moving_right = False
            hero.move_x -= hero.speed_x
        if keys[right]:
            hero.moving = True
            hero.moving_left = False
            hero.moving_right = True
            hero.move_x += hero.speed_x
        if keys[up]:
            hero.moving = True
            hero.move_y -= hero.speed_y
        if keys[down]:
            hero.moving = True
            hero.move_y += hero.speed_y

        hero.sound_walk()

        ground_sprites.draw(SCREEN)
        sprites.draw(SCREEN)
        enemy_sprites.draw(SCREEN)
        sprites.update(hero, moving_cube, sprites_, enemy_sprites, cat, luke)
        enemy_sprites.update(camera)
        print_info(hero.home)
        if congratulations:
            congratulations_window()
            congratulations = False
        if keys[pygame.K_ESCAPE]:
            pause()
        if keys[pygame.K_RETURN]:
            if hero.on_the_luke:
                if pause(True):
                    running = False
        CLOCK.tick(FPS)
        pygame.display.flip()
    return game_over_win('access')


# the main function which starts the game
def start_game():
    global from_game
    from_game = True
    pygame.mixer.music.stop()
    reset()
    home_action()
    reset()
    while main_action():
        from_game = True
        reset()
        home_action()
        reset()


from_game = False

pygame.mixer.music.load('data/sounds/bg-tack.ogg')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(user.menu_music_volume)

shoot = pygame.mixer.Sound('data/sounds/shoot.ogg')
shoot.set_volume(0.5)
walk = pygame.mixer.Sound('data/sounds/walk.ogg')
meow = pygame.mixer.Sound('data/sounds/meow.ogg')
reloading = pygame.mixer.Sound('data/sounds/reloading.ogg')
reloading.set_volume(0.3)

show_menu()
terminate()