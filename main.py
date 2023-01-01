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
mousePos = {'x': 0, 'y': 0}


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
    'ground_ender': load_image(r'ground\ender_block.png'),
    'enemy_red': load_image(r'enemy_red.png'),
    'stone_block': load_image(r'stone_block.png'),
    'cat': [load_image('cat.png'), load_image('cat_2.png'), load_image('cat.png'), load_image('cat_3.png')]
}


class Gun(pygame.sprite.Sprite):
    def __init__(self, gun_image, *groups: AbstractGroup):
        super().__init__(*groups)
        self.gun_image = gun_image
        self.image = load_image(gun_image)
        self.rect = self.image.get_rect()


class HeroMain(pygame.sprite.Sprite):
    def __init__(self, x, y, gun, frames, *groups: AbstractGroup):
        super().__init__(all_sprites, *groups)
        self.frames = frames
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 5
        self.speed_y = 5

        self.angle = 0
        self.heavy = 0

        self.moving = False
        self.moving_left = False
        self.moving_right = True
        self.move_x = 0
        self.move_y = 0

        self.gun = gun #class
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

    def update(self, cube, cube_2, sprites, enemy_sprites):
        self.move_gun()
        self.rect.x += self.move_x
        self.rect.y += self.move_y
        if pygame.sprite.spritecollideany(self, sprites):
            self.rect.x -= self.move_x
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
        if self.moving:
            self.update_frame()
        else:
            self.update_frame(True)

        self.move_x = 0
        self.move_y = 0

        cube.moving = False


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, gun, frames, cat=False, hero=None, *groups: AbstractGroup):
        super().__init__(all_sprites, *groups)
        self.frames = [frames] if not cat else frames
        self.cur_frame = 0
        self.cat = cat
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 5
        self.speed_y = 5

        self.hero = hero

        self.angle = 0
        self.strike_distance = 350

        self.moving = False
        self.moving_left = False
        self.moving_right = True
        self.move_x = 0
        self.move_y = 0

        self.gun = gun #class
        self.gun_image = gun.image

    def update_frame(self, stand=False):
        if self.cat:
            if stand:
                if self.moving_left:
                    self.image = pygame.transform.flip(self.frames[self.cur_frame // 4], True, False)
                elif self.moving_right:
                    self.image = self.frames[self.cur_frame // 4]
            else:
                self.cur_frame += 1
                if self.cur_frame > 15:
                    self.cur_frame = 0
            if self.moving_left:
                self.image = pygame.transform.flip(self.frames[self.cur_frame // 4], True, False)
            elif self.moving_right:
                self.image = self.frames[self.cur_frame // 4]
        else:
            if not stand:
                if self.moving_left:
                    self.image = pygame.transform.flip(self.frames[self.cur_frame // 4], True, False)
                elif self.moving_right:
                    self.image = self.frames[self.cur_frame // 4]

    def update(self):
        self.move_gun()
        self.update_frame()

    def move_gun(self):

        x_hero = self.hero.rect.x + self.hero.image.get_rect()[2] // 2
        y_hero = self.hero.rect.y + self.hero.image.get_rect()[3] // 2
        x = self.rect.x + self.image.get_rect()[2] // 2
        y = self.rect.y + self.image.get_rect()[3] // 2

        if ((x_hero - x) ** 2 + (y_hero - y) ** 2) ** 0.5 < self.strike_distance + 50:
            if (x_hero - x) < 0:
                self.moving_left = True
                self.moving_right = False
            else:
                self.moving_left = False
                self.moving_right = True

        if self.moving_left:
            if ((x_hero - x) ** 2 + (y_hero - y) ** 2) ** 0.5 < self.strike_distance:
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
            # else:
            #     self.gun.image = pygame.transform.flip(self.gun_image, True, False)
            #     SCREEN.blit(self.gun.image, (self.rect.x,
            #                                  (self.rect.y + self.image.get_size()[1] // 2)))

        elif self.moving_right:
            if ((x_hero - x) ** 2 + (y_hero - y) ** 2) ** 0.5 < self.strike_distance:
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
            # else:
            #     self.gun.image = self.gun_image
            #     SCREEN.blit(self.gun.image, (self.rect.x,
            #                                  (self.rect.y + self.image.get_size()[1] // 2)))


class GroundTexture(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(ground_sprites, all_sprites)
        self.image = DICT_IMAGES[tile_type]
        self.width = 86
        self.height = 86
        self.rect = self.image.get_rect().move(
            self.width * pos_x, self.height * pos_y)


class Cube(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y, color=None, *groups: AbstractGroup):
        super().__init__(all_sprites, *groups)
        self.image = load_image('box.png') if color is None else DICT_IMAGES['stone_block']
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


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


def init_frames():
    global hero_main_frames
    for i in range(1, 7):
        hero_main_frames.append(load_image(rf'walk\{i}.png'))

    for y in range((2000 // 86) + 1):
        for x in range((2000 // 86) + 1):
            GroundTexture('ground_ender', x, y)


def main_action():
    running = True

    init_frames()

    camera = Camera()

    sprites = pygame.sprite.Group()
    sprites_ = pygame.sprite.Group()

    firesList = []

    ak47 = Gun('gun.png')

    hero = HeroMain(x=200, y=600, gun=ak47, frames=hero_main_frames)

    cube_new = Cube(width=50, height=50,  x=500, y=300)
    cube_new2 = Cube(width=50, height=50,  x=100, y=340)
    cube_new3 = Cube(width=50, height=50,  x=900, y=100)
    cube_red = Cube(width=50, height=50, x=700, y=400, color='red')

    for i in range(5):
        enemy = Enemy(100 * random.randint(1, 10), 100 * random.randint(1, 6),gun=ak47, frames=DICT_IMAGES['enemy_red'], hero=hero)
        enemy_sprites.add(enemy)

    enemy_sprites.add(Enemy(1000, 500, gun=ak47, frames=DICT_IMAGES['cat'], cat=True, hero=hero))

    sprites.add(hero, cube_red, cube_new, cube_new2, cube_new3)
    sprites_.add(cube_new, cube_new2, cube_new3)
    while running:
        SCREEN.fill(pygame.Color('black'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
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
                        firesList.append(
                            [
                                angleR,
                                x - 10,
                                y,
                                x,
                                y
                            ]
                        )
        #camera
        camera.update(hero)
        for sprite in all_sprites:
            camera.apply(sprite)
        #
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            hero.moving = True
            hero.moving_left = True
            hero.moving_right = False
            hero.move_x -= hero.speed_x
        if keys[pygame.K_RIGHT]:
            hero.moving = True
            hero.moving_left = False
            hero.moving_right = True
            hero.move_x += hero.speed_x
        if keys[pygame.K_UP]:
            hero.moving = True
            hero.move_y -= hero.speed_y
        if keys[pygame.K_DOWN]:
            hero.moving = True
            hero.move_y += hero.speed_y

        ground_sprites.draw(SCREEN)
        enemy_sprites.draw(SCREEN)
        sprites.draw(SCREEN)
        sprites.update(hero, cube_red, sprites_, enemy_sprites)
        enemy_sprites.update()
        for elem in firesList:
            sX = math.cos(elem[0]) * 30
            sY = math.sin(elem[0]) * 30

            elem[1] += sX
            elem[2] += sY

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
                firesList.remove(elem)
            elif elem[1] < 0 or elem[1] > WIDTH or elem[2] < 0 or elem[2] > HEIGHT:
                firesList.remove(elem)
            elif pygame.sprite.spritecollideany(sprite, sprites_) or pygame.sprite.collide_rect(sprite, cube_red):
                firesList.remove(elem)
            else:
                pygame.draw.circle(image, pygame.Color("orange"),
                               (5, 5), 5)
                SCREEN.blit(image, [elem[1], elem[2]])

        # print(firesList)
        CLOCK.tick(FPS)
        pygame.display.flip()
    pygame.quit()


main_action()