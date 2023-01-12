import os
import sys
import pygame
import random
from copy import deepcopy
import math
from pygame.sprite import AbstractGroup

pygame.init()
WIDTH = 1000
HEIGHT = 500
SIZE = WIDTH, HEIGHT
SCREEN = pygame.display.set_mode(SIZE)
SCREEN.fill(pygame.Color('black'))
CLOCK = pygame.time.Clock()
FPS = 30
hero_main_frames = []
ground_sprites = pygame.sprite.Group()
enemy_sprites = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
sprites = pygame.sprite.Group()
sprites_ = pygame.sprite.Group()
unmoving_sprites = pygame.sprite.Group()
mousePos = {'x': 0, 'y': 0}
hero = None
cat = None
luke = None


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


DICT_IMAGES = {
    'menu_bg': load_image('menu_bg.jpg'),
    'ground_ender': load_image(r'ground\ender_block.png'),
    'enemy_red': load_image(r'enemy_red.png'),
    'stone_block': load_image(r'stone_block.png'),
    'cat': [load_image('cat.png'), load_image('cat_2.png'), load_image('cat.png'), load_image('cat_3.png')],
    'box': load_image('box.jpg'),
    'ground_sand': load_image('ground_sand.png'),
    'ground_stone': load_image('ground_stone.jpg'),
    'bush': load_image('bush_mine.png'),
    'branch': load_image('branch.png'),
    'luke': load_image('luke.png')
}


class Gun(pygame.sprite.Sprite):
    def __init__(self, power, ammo, gun_image, *groups: AbstractGroup):
        super().__init__(*groups)
        self.gun_image = gun_image
        self.image = load_image(gun_image)
        self.rect = self.image.get_rect()
        self.power = power
        self.ammo = ammo
        self.ammo_now = ammo
        self.wait = 0
        self.wait_max = 100


class Cat(pygame.sprite.Sprite):
    def __init__(self,x, y, frames, *groups: AbstractGroup):
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

        self.stand = True

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


class HeroMain(pygame.sprite.Sprite):
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

        self.catch_cat = False
        self.on_the_luke = False

        self.moving = False
        self.moving_left = False
        self.moving_right = True
        self.move_x = 0
        self.move_y = 0

        self.gun = gun  # class
        self.gun_image = gun.image
        self.strike_can = True

    # def rotate(self):
    #     self.image = pygame.transform.rotate(self.image, 360 - self.angle)

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
        # self.rotate()

    def move_gun(self):
        if self.moving_left:
            self.gun.image = pygame.transform.flip(self.gun_image, True, False)
            self.gun.image = pygame.transform.rotate(self.gun.image, -90)
            if self.angle <= -80:
                self.strike_can = True
                self.gun.image = pygame.transform.rotate(self.gun.image, 360 - (self.angle + 90))
                SCREEN.blit(self.gun.image, (self.rect.x - 20,
                                             (self.rect.y + self.image.get_size()[1] // 2  - (90 + (self.angle + 90)) // 4)))
            elif 90 <= self.angle <= 180:
                self.strike_can = True
                self.gun.image = pygame.transform.rotate(self.gun.image, 360 - (self.angle + 90))
                SCREEN.blit(self.gun.image, ((self.rect.x - 20) - 1 * (self.angle - 180) // 4 ,
                                             (self.rect.y + self.image.get_size()[1] // 2 + 1 * (self.angle - 180) // 4)))
            else:
                self.strike_can = False
                self.gun.image = pygame.transform.flip(self.gun_image, True, False)
                SCREEN.blit(self.gun.image, (self.rect.x -  20,
                                             (self.rect.y + self.image.get_size()[1] // 2)))

        elif self.moving_right:
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
            # self.gun.rect.x = self.rect.x
            # self.gun.rect.y = self.rect.y + self.image.get_size()[1] // 2

    def update(self, cube, cube_2, sprites, enemy_sprites, cat, luke):
        self.move_gun()
        self.rect.x += self.move_x
        self.rect.y += self.move_y

        if (not pygame.sprite.spritecollideany(self, horizontal_borders)) and (not pygame.sprite.spritecollideany(self, vertical_borders)):
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
        if pygame.sprite.collide_mask(self, cat):
            cat.kill()
            self.catch_cat = True
        if pygame.sprite.collide_rect(self, luke):
            self.on_the_luke = True
            if self.catch_cat:
                print('True')
            else:
                print('False')
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
        self.cur_frame_cat = 0
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

        self.gun = gun  # class
        # self.gun.wait_max *= 10
        # self.ammo_now = 5 # self.gun.ammo_now
        # self.ammo = 5 # self.gun.ammo
        # self.wait = 0
        # self.wait_max = self.gun.wait_max
        self.gun_image = gun.image

        self.count = 0
        self.fires_list = []

    def update_frame(self, stand=True):
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

    # def reload(self):
    #     if self.ammo_now == 0:
    #         self.wait += 1
    #         if self.wait_max == self.wait:
    #             self.ammo_now = self.ammo
    #             self.wait = 0

    def update(self, camera):
        # self.reload()
        self.move_gun(camera)
        if self.moving:

            dl_x = self.hero.rect.x - self.rect.x
            dl_y = self.hero.rect.y - self.rect.y

            # if self.stop_distance - 50 <= (dl_x ** 2 + dl_y ** 2) ** 0.5 <= self.stop_distance:
            #     print('yes')

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
                    repeat = False #отрисовка пуль без повторов
                if (((x_hero - x) ** 2 + (y_hero - y) ** 2) ** 0.5) < self.stop_distance:
                    self.moving = False
                #
                # if (((x_hero - x) ** 2 + (y_hero - y) ** 2) ** 0.5) < (self.strike_distance - 150):
                #     self.moving = False

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
                if repeat:
                    self.fire(x, y, x_hero, y_hero, camera)
            else:
                self.fire(x, y, x_hero, y_hero, camera)
            # else:
            #     self.gun.image = pygame.transform.flip(self.gun_image, True, False)
            #     SCREEN.blit(self.gun.image, (self.rect.x,
            #                                  (self.rect.y + self.image.get_size()[1] // 2)))

        elif self.moving_right:
            repeat = True
            if ((x_hero - x) ** 2 + (y_hero - y) ** 2) ** 0.5 < self.strike_distance:
                if (((x_hero - x) ** 2 + (y_hero - y) ** 2) ** 0.5) < (self.strike_distance - 100):
                    self.moving = True
                    self.fire(x, y, x_hero, y_hero, camera, True)
                    repeat = False #отрисовка пуль без повторов
                if (((x_hero - x) ** 2 + (y_hero - y) ** 2) ** 0.5) < self.stop_distance:
                    self.moving =  False

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
            # els
            #     self.gun.image = self.gun_image
            #     SCREEN.blit(self.gun.image, (self.rect.x,
            #                                  (self.rect.y + self.image.get_size()[1] // 2)))

    def fire(self,x, y, x_2, y_2, camera, status=False):
        if status:
            self.count += 1
            if self.count % 15 == 0:
                self.count = 0
                # if self.ammo_now != 0:
                #     self.ammo_now -= 1
                self.fires_list.append(
                                [
                                    math.atan2(y_2 - y,
                                                x_2 - x),
                                    x - 10,
                                    y,
                                    x,
                                    y
                                ]
                            )
                # else:
                #     print(self.wait, 'Перезарядка')
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

            if (x_ ** 2 + y_ ** 2) ** 0.5 > 320:
                self.fires_list.remove(elem)
            elif pygame.sprite.collide_rect(sprite, self.hero):
                self.hero.health -= max(self.gun.power - 5, 5)
                print(f'Hero damaged: {self.hero.health}')
                if self.hero.health <= 0:
                    print('hero died')
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


class GroundTexture(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(ground_sprites, all_sprites)
        self.image = DICT_IMAGES[tile_type]
        self.width = 86
        self.height = 86
        self.rect = self.image.get_rect().move(
            self.width * pos_x, self.height * pos_y)


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


moving_cube = None


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


ak47 = Gun(power=15, ammo=30, gun_image='gun.png')


class Button:
    def __init__(self, width, height, inactive_color, active_color):
        self.width = width
        self.height = height
        self.inactive_color = inactive_color
        self.active_color = active_color

    def draw(self, x, y, message, dl_x=10, dl_y=10, action=None, font_size=30):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if x < mouse[0] < x + self.width and y < mouse[1] < y + self.height:
            pygame.draw.rect(SCREEN, self.active_color, (x, y, self.width, self.height))
            print_text(text=message, color=self.inactive_color, x=x + 10, y=y + 10, font=font_size)
            if click[0] == 1 and action is not None:
                action()

        else:
            pygame.draw.rect(SCREEN, self.inactive_color, (x, y, self.width, self.height))
            print_text(text=message, color=self.active_color, x=x + dl_x, y=y + dl_y, font=font_size)


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


def init_frames():
    global hero_main_frames, moving_cube, hero, cat, luke
    for i in range(1, 7):
        hero_main_frames.append(load_image(rf'walk\{i}.png'))

    for y in range((2000 // 86) + 1):
        for x in range((2000 // 86) + 1):
            GroundTexture('ground_ender', x, y)

    world = []
    file = open('game_map.txt', 'r')
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

    for row in range(len(world)):
        for col in range(len(world[row])):
            x, y = col * 10, row * 10

            if world[row][col] == 1 or world[row][col] == 7:
                boxes.append((x, y, world[row][col]))
            elif world[row][col] == 2:
                cube_r.append((x, y))
            elif world[row][col] == 3:
                enemies.append((x, y))
            elif world[row][col] == 4:
                hero_l.append((x, y))
            elif world[row][col] == 5 or world[row][col] == 6 or world[row][col] == 8:
                ground.append((x, y, world[row][col]))
            elif world[row][col] == 9:
                cat_l.append((x, y))
            elif world[row][col] == 'l':
                luke_l.append((x, y))

    for elem in ground:
        image = DICT_IMAGES['ground_sand']
        if elem[2] == 6:
            image = DICT_IMAGES['ground_stone']
        elif elem[2] == 8:
            image = DICT_IMAGES['branch']

        cube = Cube(width=50, height=50, x=elem[0], y=elem[1],
                    image=image)
        sprites.add(cube)

    for elem in luke_l:
        luke = Cube(width=80, height=80, x=elem[0], y=elem[1], image=DICT_IMAGES['luke'])
        sprites.add(luke)

    for elem in cat_l:
        cat = Cat(elem[0], elem[1], frames=DICT_IMAGES['cat'])
        sprites.add(cat)

    for elem in hero_l:
        hero = HeroMain(elem[0], elem[1], gun=ak47, frames=hero_main_frames)
        sprites.add(hero)

    for elem in enemies:
        enemy = Enemy(elem[0], elem[1], gun=ak47,
                      frames=hero_main_frames, hero=hero)
        enemy_sprites.add(enemy)

    # for elem in ground:
    #     cube = Cube(width=50, height=50, x=elem[0], y=elem[1],
    #                 image=DICT_IMAGES['ground_stone'] if elem[2] == 6 else DICT_IMAGES['ground_sand'])
    #     sprites.add(cube)

    for elem in boxes:
        cube = Cube(width=50, height=50, x=elem[0], y=elem[1],
                    image=DICT_IMAGES['box'] if elem[2] == 1 else DICT_IMAGES['bush'])
        sprites.add(cube)
        sprites_.add(cube)
        unmoving_sprites.add(cube)

    for elem in cube_r:
        moving_cube = Cube(width=50, height=50, x=elem[0], y=elem[1], type='moving_cube')
        sprites.add(moving_cube)
        unmoving_sprites.add(moving_cube)


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


def terminate():
    pygame.quit()
    sys.exit()


def pause():
    paused = True
    button = Button(100, 50, active_color=(255, 255, 255), inactive_color=(229, 190, 1))
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                paused = False
        # 21,23,25
        #27, 17, 22
        pygame.draw.rect(SCREEN, (21, 23, 25), (WIDTH // 2 - 300, HEIGHT // 2 - 80, 600, 230))
        print_text("PAUSED.", (243, 165, 5), 75, x=0, y=30, center=True)
        print_text("PRESS ENTER TO CONTINUE", (255, 202, 134), 50, x=0, y=-30, center=True)
        button.draw(x=WIDTH // 2 - 50, y=HEIGHT // 2 + 75, message='МЕНЮ', action=show_menu, dl_x=15, dl_y=15)
        pygame.display.flip()
        CLOCK.tick(FPS)


def print_info():
    font = pygame.font.SysFont('monserat', 25)
    text = font.render("Hero health:", True, pygame.Color(127,255,0))
    text_x = WIDTH // 2 - text.get_width() // 2 - 55
    text_y = HEIGHT - text.get_height()
    text_w = text.get_width()
    text_h = text.get_height()
    pygame.draw.rect(SCREEN, pygame.Color('black'), (WIDTH // 2 - text.get_width() // 2 - 62, HEIGHT - 20,
                                                     text.get_width() + 120, 20))
    pygame.draw.rect(SCREEN, pygame.Color(127,255,0), (WIDTH // 2, HEIGHT - text.get_height() + 4, abs(hero.health), 10))
    SCREEN.blit(text, (text_x, text_y))


def main_action():
    running = True

    init_frames()

    Border(-50, 0, 2100, 0, 't')
    Border(-50, 2000, 2100, 2000, 'b')
    Border(0, 0, 0, 2100, 'l')
    Border(2000, 0, 2000, 2100, 'r')

    camera = Camera()

    firesList = []

    win = False

    # cube_new = Cube(width=50, height=50,  x=500, y=300)
    # cube_new2 = Cube(width=50, height=50,  x=100, y=340)
    # cube_new3 = Cube(width=50, height=50,  x=900, y=100)

    # for sprite in enemy_sprites:
    #     sprite.hero = hero
    # for i in range(1):
    #     enemy = Enemy(100 * random.randint(1, 10), 100 * random.randint(1, 6),gun=ak47, frames=hero_main_frames, hero=hero)
    #     enemy_sprites.add(enemy)
    #
    # enemy_sprites.add(Enemy(1000, 500, gun=ak47, frames=DICT_IMAGES['cat'], cat=True, hero=hero))

    # sprites_.add(cube_new, cube_new2, cube_new3)
    # unmoving_sprites.add(cube_new, cube_new2, cube_new3, cube_red)
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
                            print(hero.gun.wait)
                            continue
                        hero.gun.ammo_now -= 1
                        firesList.append(
                            [
                                angleR,
                                x - 10,
                                y,
                                x,
                                y
                            ]
                        )
                    print(hero.gun.ammo_now)
        #camera
        if hero.gun.ammo_now == 0:
            hero.gun.wait += 1
            print(hero.gun.wait)
            if hero.gun.wait_max == hero.gun.wait:
                hero.gun.ammo_now = hero.gun.ammo
                hero.gun.wait = 0
        camera.update(hero)
        for sprite in all_sprites:
            camera.apply(sprite)
        #
        # if len(enemy_sprites) == 0:
        #     win = True
        #     running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            if hero.catch_cat and hero.on_the_luke:
                win = True
                running = False
        if keys[pygame.K_SPACE]:
            win = True
            running = False
        if keys[pygame.K_a]:
            hero.moving = True
            hero.moving_left = True
            hero.moving_right = False
            hero.move_x -= hero.speed_x
        if keys[pygame.K_d]:
            hero.moving = True
            hero.moving_left = False
            hero.moving_right = True
            hero.move_x += hero.speed_x
        if keys[pygame.K_w]:
            hero.moving = True
            hero.move_y -= hero.speed_y
        if keys[pygame.K_s]:
            hero.moving = True
            hero.move_y += hero.speed_y

        ground_sprites.draw(SCREEN)
        sprites.draw(SCREEN)
        enemy_sprites.draw(SCREEN)
        sprites.update(hero, moving_cube, sprites_, enemy_sprites, cat, luke)
        enemy_sprites.update(camera)
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
                    if person.health <= 0:
                        person.kill()
                        print('enemy died')
                firesList.remove(elem)
            elif pygame.sprite.spritecollideany(sprite, horizontal_borders) or pygame.sprite.spritecollideany(sprite, vertical_borders):
                firesList.remove(elem)
            elif pygame.sprite.spritecollideany(sprite, sprites_) or pygame.sprite.collide_rect(sprite, moving_cube):
                firesList.remove(elem)
            else:
                pygame.draw.circle(image, pygame.Color("orange"),
                               (5, 5), 5)
            if (x_ ** 2 + y_ ** 2) ** 0.5 > 50:
                SCREEN.blit(image, [elem[1], elem[2]])
        print_info()
        if keys[pygame.K_ESCAPE]:
            pause()
        if hero.health <= 0:
            running = False
        CLOCK.tick(FPS)
        pygame.display.flip()
    if win:
        return game_over_win(True)
    return game_over_win()


def game_over_win(value=False):
    stopped = True
    button_lose = Button(100, 50, active_color=(255, 255, 255), inactive_color=(180, 76, 67))
    button_win = Button(100, 50, active_color=(255, 255, 255), inactive_color=(76, 187, 23))
    while stopped:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                return True
        pygame.draw.rect(SCREEN, (21, 23, 25), (WIDTH // 2 - 300, HEIGHT // 2 - 80, 600, 230))
        if not value:
            print_text("YOU LOSE.", (255, 0, 51), 75, x=0, y=30, center=True)
            print_text("PRESS ENTER TO PLAY AGAIN", (217, 80, 48), 50, x=0, y=-30, center=True)
            button_lose.draw(x=WIDTH // 2 - 50, y=HEIGHT // 2 + 75, message='МЕНЮ', action=show_menu, dl_x=15, dl_y=15)
        else:
            #124, 252, 0
            print_text("YOU WIN.", (124, 252, 0), 75, x=0, y=30, center=True)
            print_text("PRESS ENTER TO PLAY AGAIN", (189, 218, 87), 50, x=0, y=-30, center=True)
            button_win.draw(x=WIDTH // 2 - 50, y=HEIGHT // 2 + 75, message='МЕНЮ', action=show_menu, dl_x=15, dl_y=15)

        pygame.display.flip()
        CLOCK.tick(FPS)


def show_menu():
    menu_background = DICT_IMAGES['menu_bg']

    btn = Button(200, 100, active_color=(255, 255, 255), inactive_color=(0, 0, 0))
    settings_btn = Button(150, 50, active_color=(255, 255, 255), inactive_color=(0, 0, 0))
    dl = 30
    show = True
    while show:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

        SCREEN.blit(menu_background, (0, 0))
        btn.draw(150, 80, dl_x=35, dl_y=25, message='PLAY.', action=start_game, font_size=70)
        settings_btn.draw(175, 205, dl_x=25, dl_y=18, message='SETTINGS.', font_size=30)
        settings_btn.draw(175, 280, dl_x=40, dl_y=18, message='STATА.', font_size=30)
        settings_btn.draw(175, 355, dl_x=50, dl_y=18, message='EXIT.', action=terminate, font_size=30)
        pygame.display.update()
        CLOCK.tick(FPS)


def reset():
    global hero_main_frames, ground_sprites, \
        enemy_sprites, all_sprites, vertical_borders, \
        horizontal_borders, sprites, sprites_, unmoving_sprites, mousePos, ak47
    hero_main_frames = []
    ground_sprites = pygame.sprite.Group()
    enemy_sprites = pygame.sprite.Group()
    all_sprites = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    horizontal_borders = pygame.sprite.Group()
    sprites = pygame.sprite.Group()
    sprites_ = pygame.sprite.Group()
    unmoving_sprites = pygame.sprite.Group()
    mousePos = {'x': 0, 'y': 0}
    ak47 = Gun(power=15, ammo=30, gun_image='gun.png')
#
# def home_action():
#     running = True
#
#     init_frames('home.txt')
#
#     Border(-50, 0, 2100, 0, 't')
#     Border(-50, 2000, 2100, 2000, 'b')
#     Border(0, 0, 0, 2100, 'l')
#     Border(2000, 0, 2000, 2100, 'r')
#
#     camera = Camera()


def start_game():
    reset()
    while main_action():
        reset()


show_menu()
terminate()