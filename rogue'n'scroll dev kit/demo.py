import os
import sys
import pygame

FPS = 50
pygame.init()
clock = pygame.time.Clock()
size = WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode(size)
PLAYER = None
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y = None, None, None
    player_xy = (0, 0)
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '1':
                Tile('empty', x, y, (len(level[y]), len(level)))
                player_xy = (x, y)
    new_player = Player(*player_xy, (len(level[y]), len(level)))

    return new_player, x, y


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


def load_level(filename):
    if not os.path.isfile(os.path.join('data', filename)):
        print(f"Файл с уровнем '{filename}' не найден")
        sys.exit()
    with open("data/" + filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {
    'wall': load_image('box.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('mar.png')
tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y, board_size):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.type = tile_type
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.matrix = board_size

    def get_type(self):
        return self.type

    def update(self, shift):
        self.rect.x = (self.rect.x + shift[0]) % ((self.matrix[0]) * tile_width)
        self.rect.y = (self.rect.y + shift[1]) % ((self.matrix[1]) * tile_height)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, board_size):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 15, tile_height * pos_y + 5)
        self.matrix = board_size

    def update(self, shift):
        old_rect = self.rect.copy()
        self.rect.x = (self.rect.x - shift[0]) % ((self.matrix[0]) * tile_width)
        self.rect.y = (self.rect.y - shift[1]) % ((self.matrix[1]) * tile_height)
        collision = pygame.sprite.spritecollideany(self, tiles_group).get_type() != 'wall'
        self.rect = old_rect
        return collision


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, full, view):
        self.dx = 0
        self.full_size = full
        self.view_size = view
        self.total_shift = [0, 0]
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - self.view_size[0] // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - self.view_size[1] // 2)
        if not (-self.full_size[0] + self.view_size[0] < self.total_shift[0] + self.dx < 0):
            if self.dx > 0:
                self.dx = -self.total_shift[0]
            elif self.dx < 0:
                self.dx = -(self.full_size[0] - self.view_size[0]) - self.total_shift[0]
        if not -self.full_size[1] + self.view_size[1] < self.total_shift[1] + self.dy < 0:
            if self.dy > 0:
                self.dy = -self.total_shift[1]
            elif self.dy < 0:
                self.dy = -(self.full_size[1] - self.view_size[1]) - self.total_shift[1]
        self.total_shift[0] += self.dx
        self.total_shift[1] += self.dy


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def main():
    running = True
    player, level_x, level_y = generate_level(load_level(input('в формате "lvl"цифра') + '.txt'))
    full_size = ((level_x + 1) * tile_width, (level_y + 1) * tile_height)
    # view_size = ((level_x // 2 + 1) * tile_width, (level_y // 2 + 1) * tile_height)
    screen = pygame.display.set_mode(full_size)
    pygame.mouse.set_visible(False)
    # camera = Camera(full_size, view_size)
    while running:
        screen.fill((255, 255, 255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                pressed = pygame.key.get_pressed()
                shift = [0, 0]
                if pressed[pygame.K_DOWN]:
                    shift[1] = -tile_height
                elif pressed[pygame.K_UP]:
                    shift[1] = +tile_height
                elif pressed[pygame.K_RIGHT]:
                    shift[0] = -tile_width
                elif pressed[pygame.K_LEFT]:
                    shift[0] = +tile_width
                if player_group.sprites()[0].update(shift):
                    tiles_group.update(shift)
        # camera.update(player)
        # for sprite in all_sprites:
        #     camera.apply(sprite)
        all_sprites.draw(screen)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    start_screen()
    main()
