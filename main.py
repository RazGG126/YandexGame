import os
import sys
import pygame
from pygame.sprite import AbstractGroup

pygame.init()
WIDTH = 1280
HEIGHT = 720
SIZE = WIDTH, HEIGHT
SCREEN = pygame.display.set_mode(SIZE)
SCREEN.fill(pygame.Color('black'))
CLOCK = pygame.time.Clock()
FPS = 30
hero_main_frames = []


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


class CubeMain(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y, color, frames, *groups: AbstractGroup):
        super().__init__(*groups)
        self.frames = frames
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 5
        self.speed_y = 5

        self.heavy = 0

        self.moving = False
        self.moving_left = False
        self.moving_right = True
        self.move_x = 0
        self.move_y = 0

    def update_frame(self, stand=False):
        if stand:
            self.cur_frame = 0
        else:
            self.cur_frame += 1
            if self.cur_frame > 19:
                self.cur_frame = 0
        if self.moving_left:
            self.image = pygame.transform.flip(self.frames[self.cur_frame // 4], True, False)
        elif self.moving_right:
            self.image = self.frames[self.cur_frame // 4]

    def update(self, cube, cube_2, sprites):
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
                if not cube_2.can_move(sprites):
                    cube_2.move(-self.heavy, 0)
                    self.rect.x -= self.heavy

            self.rect.y += self.move_y
            if pygame.sprite.collide_rect(cube, cube_2):
                self.heavy = 1 if self.move_y >= 0 else -1
                self.rect.y -= self.move_y
                self.rect.y += self.heavy
                cube_2.move(0, self.heavy)
                if not cube_2.can_move(sprites):
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


class Cube(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y, color, *groups: AbstractGroup):
        super().__init__(*groups)
        self.image = load_image('box.png')
        self.rect = pygame.Rect(x, y, width, height)
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 0
        self.speed_y = 0

        self.move_x = 0
        self.move_y = 0

    def can_move(self, sprites):
        if pygame.sprite.spritecollideany(self, sprites):
            return False
        return True

    def move(self, move_x, move_y):
        self.rect.x += move_x
        self.rect.y += move_y


def init_frames():
    global hero_main_frames
    for i in range(1, 7):
        hero_main_frames.append(load_image(rf'walk\{i}.png'))


def main_action():
    running = True

    init_frames()

    sprites = pygame.sprite.Group()
    sprites_godmode = pygame.sprite.Group()
    sprites_ = pygame.sprite.Group()

    cube = CubeMain(width=50, height=50,  x=200, y=600, color='green', frames=hero_main_frames)
    cube_new = Cube(width=50, height=50,  x=500, y=300, color='blue')
    cube_new2 = Cube(width=50, height=50,  x=100, y=340, color='blue')
    cube_new3 = Cube(width=50, height=50,  x=900, y=100, color='blue')
    cube_red = Cube(width=50, height=50, x=700, y=400, color='red')

    sprites.add(cube_red)
    sprites.add(cube, cube_red, cube_new, cube_new2, cube_new3)
    sprites_.add(cube_new, cube_new2, cube_new3)
    sprites_godmode.add(cube_red)
    while running:
        SCREEN.fill(pygame.Color('black'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            cube.moving = True
            cube.moving_left = True
            cube.moving_right = False
            cube.move_x -= cube.speed_x
        if keys[pygame.K_RIGHT]:
            cube.moving = True
            cube.moving_left = False
            cube.moving_right = True
            cube.move_x += cube.speed_x
        if keys[pygame.K_UP]:
            cube.moving = True
            cube.move_y -= cube.speed_y
        if keys[pygame.K_DOWN]:
            cube.moving = True
            cube.move_y += cube.speed_y

        sprites.draw(SCREEN)
        sprites.update(cube, cube_red, sprites_)
        CLOCK.tick(FPS)
        pygame.display.flip()
    pygame.quit()


main_action()