import pygame

pygame.init()
WIDTH, HEIGHT = 1920, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

fps = 60

world = []
world_width, world_height = 192, 100
cell_size = 10


def init_map():
    for row in range(world_height):
        line = []
        for col in range(world_width):
            line.append(0)
        world.append(line)


init_map()

number = 1
running = True
while running:
    screen.fill(pygame.Color('black'))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            world.clear()
            init_map()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
            file = open('game_map.txt', 'w')
            for row in range(world_height):
                for col in range(world_width):
                    file.write(str(world[row][col]))
                file.write('\n')
            file.close()
            print('Карта сохранена')
        if event.type == pygame.KEYDOWN and event.key == pygame.K_o:
            try:
                file = open('game_map.txt', 'r')

                row, col = 0, 0
                for line in file:
                    line = line.strip()
                    for elem in line:
                        world[row][col] = int(elem)
                        col += 1
                    row += 1
                    col = 0
                file.close()
                print('Карта загружена')
            except Exception:
                print('Файл карты не найден')

    keys = pygame.key.get_pressed()

    if keys[pygame.K_b]:
        number = 2
    elif keys[pygame.K_v]:
        number = 1
    elif keys[pygame.K_e]:
        number = 3
    elif keys[pygame.K_p]:
        number = 4
    elif keys[pygame.K_g]:
        number = 5
    elif keys[pygame.K_t]:
        number = 6
    elif keys[pygame.K_x]:
        number = 7

    mousePX, mousePY = pygame.mouse.get_pos()
    b1, b2, b3 = pygame.mouse.get_pressed()

    mouse_row, mouse_col = mousePY // cell_size, mousePX // cell_size

    if b1:
        world[mouse_row][mouse_col] = number
    elif b3:
        world[mouse_row][mouse_col] = 0

    for row in range(world_height):
        for col in range(world_width):
            x, y = col * cell_size, row * cell_size
            if world[row][col] == 1:
                pygame.draw.rect(screen, pygame.Color('orange'), (x, y, cell_size * 5, cell_size * 5))
            elif world[row][col] == 2:
                pygame.draw.rect(screen, pygame.Color('green'), (x, y, cell_size * 7, cell_size * 15))
            elif world[row][col] == 3:
                pygame.draw.rect(screen, pygame.Color('red'), (x, y, cell_size * 5, cell_size * 7))
            elif world[row][col] == 4:
                pygame.draw.rect(screen, pygame.Color('blue'), (x, y, cell_size * 5, cell_size * 7))
            elif world[row][col] == 5:
                pygame.draw.rect(screen, pygame.Color('yellow'), (x, y, cell_size * 5, cell_size * 5))
            elif world[row][col] == 6:
                pygame.draw.rect(screen, pygame.Color('gray'), (x, y, cell_size * 5, cell_size * 5))
            elif world[row][col] == 7:
                pygame.draw.rect(screen, pygame.Color(68, 148, 74), (x, y, cell_size * 5, cell_size * 5))
            else:
                pygame.draw.rect(screen, pygame.Color('gray'), (x, y, cell_size, cell_size), 1)

    pygame.display.flip()
    clock.tick(fps)
pygame.quit()