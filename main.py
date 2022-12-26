import os
import sys
import pygame
from pygame.sprite import AbstractGroup

pygame.init()
WIDTH = 1280
HEIGHT = 720
SIZE = WIDTH, HEIGHT
SCREEN = pygame.display.set_mode(SIZE)
SCREEN.fill(pygame.Color('white'))
CLOCK = pygame.time.Clock()
FPS = 30
main_hero_images = []


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((1, 1))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class CubeMain(pygame.sprite.Sprite):
    def __init__(self, width, height, x, y, color, images, *groups: AbstractGroup):
        super().__init__(*groups)
        self.hero_image_number = 0
        self.images = images
        self.image = self.images[self.hero_image_number]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 5
        self.speed_y = 5

        self.heavy = 0

        self.move_x = 0
        self.move_y = 0

    def update_image(self):
        self.image = self.images[self.hero_image_number // 5]

    def update(self, cube, cube_2, sprites):
        self.update_image()
        self.rect.x += self.move_x
        self.rect.y += self.move_y
        if pygame.sprite.spritecollideany(self, sprites):
            self.rect.x -= self.move_x
            self.rect.y -= self.move_y
        self.rect.x -= self.move_x
        self.rect.y -= self.move_y

        if not pygame.sprite.collide_mask(cube, cube_2):
            self.rect.x += self.move_x
            if pygame.sprite.collide_mask(cube, cube_2):
                self.heavy = 1 if self.move_x >= 0 else -1
                self.rect.x -= self.move_x
                self.rect.x += self.heavy
                cube_2.move(self.heavy, 0)
                if not cube_2.can_move(sprites):
                    cube_2.move(-self.heavy, 0)
                    self.rect.x -= self.heavy

            self.rect.y += self.move_y
            if pygame.sprite.collide_mask(cube, cube_2):
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
        self.move_x = 0
        self.move_y = 0


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


def init_images():
    global main_hero_images

    for i in range(1, 7):
        main_hero_images.append(load_image(f'walk\\{i}.png'))


def main_action():
    running = True

    init_images()

    sprites = pygame.sprite.Group()
    sprites_godmode = pygame.sprite.Group()
    sprites_ = pygame.sprite.Group()

    cube = CubeMain(width=50, height=50, x=200, y=600, color='green', images=main_hero_images)
    cube_new = Cube(width=50, height=50, x=500, y=300, color='blue')
    cube_new2 = Cube(width=50, height=50, x=100, y=340, color='blue')
    cube_new3 = Cube(width=50, height=50, x=900, y=100, color='blue')
    cube_red = Cube(width=50, height=50, x=700, y=400, color='red')

    sprites.add(cube, cube_red, cube_new, cube_new2, cube_new3)
    sprites_.add(cube_new, cube_new2, cube_new3)
    sprites_godmode.add(cube_red)

    while running:
        SCREEN.fill(pygame.Color('white'))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            cube.hero_image_number += 1
            cube.move_x -= cube.speed_x
        elif keys[pygame.K_RIGHT]:
            cube.hero_image_number += 1
            cube.move_x += cube.speed_x
        elif keys[pygame.K_UP]:
            cube.hero_image_number += 1
            cube.move_y -= cube.speed_y
        elif keys[pygame.K_DOWN]:
            cube.hero_image_number += 1
            cube.move_y += cube.speed_y
        else:
            cube.hero_image_number = 0

        if cube.hero_image_number > 29:
            cube.hero_image_number = 0

        sprites.draw(SCREEN)
        sprites.update(cube, cube_red, sprites_)
        CLOCK.tick(FPS)
        pygame.display.flip()
    pygame.quit()


main_action()
