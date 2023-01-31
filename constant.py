import json
import random
import pygame, os, sys
from User import User

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
shoot = pygame.mixer.Sound('../../YandexProject_STC/Save The Cat code/data/sounds/shoot.ogg')
shoot.set_volume(0.5)
walk = pygame.mixer.Sound('../../YandexProject_STC/Save The Cat code/data/sounds/walk.ogg')
meow = pygame.mixer.Sound('../../YandexProject_STC/Save The Cat code/data/sounds/meow.ogg')
reloading = pygame.mixer.Sound('../../YandexProject_STC/Save The Cat code/data/sounds/reloading.ogg')
reloading.set_volume(0.3)
user = None
hero = None
cat = None
luke = None
lamp = False
restarts = 0
cat_number = None
congratulations = False
moving_cube = None  # <<moving_cube>> - it's the cube with texture of a big stone which you can move.
from_game = False


# function of loading images
def load_image(name, colorkey=None):
    fullname = os.path.join('../../YandexProject_STC/YandexProject_STC/Save The Cat code/data', name)
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


# function of starting music
def start_music():
    global user
    pygame.mixer.music.load('../../YandexProject_STC/YandexProject_STC/Save The Cat code/data/sounds/bg-tack.ogg')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(user.menu_music_volume)


# function of loading <<user>> statistics
def load_json():
    global user
    data = json.load(open(r'../../YandexProject_STC/YandexProject_STC/Save The Cat code/data/User/user.json', 'r', encoding='utf-8'))
    user = User(level=data['level'], coins=data['coins'],
                skin=data['skin'], skins_have=data['skins_have'], gun=data['gun'], gun_have=data['gun_have'],
                kills=data['kills'], restarts=data['restarts'], game_replays=data['game_replays'],
                ammo_spend=data['ammo_spend'], caught_cat=data['caught_cat'],
                menu_music_volume=data['menu_music_volume'], control=data['control'])


# function of saving <<user>> statistics
def dump_json():
    global user
    data = user.create_dict()

    json.dump(data, open(r'../../YandexProject_STC/YandexProject_STC/Save The Cat code/data/User/user.json', 'w', encoding='utf-8'))


load_json()