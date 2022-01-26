import pygame
import os
import sys

presets = {'0': [[False], [True, True], [True]], '1': [[True], [True, False], [True]],
           '2': [[True], [True, True], [False]], '3': [[True], [False, True], [True]],
           '4': [[False], [True, False], [True]], '5': [[True], [True, False], [False]],
           '6': [[True], [False, True], [False]], '7': [[False], [False, True], [True]],
           '8': [[False], [True, False], [False]], '9': [[False], [False, True], [False]],
           '10': [[False], [True, True], [False]], '11': [[False], [False, False], [True]],
           '12': [[True], [False, False], [True]], '13': [[True], [False, False], [False]],
           '18': [[False], [False, False], [False]], '19': [[True], [True, True], [True]]}
pygame.init()
size = width, height = 1920, 1080
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name + '.png')
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


class Floor(pygame.sprite.Sprite):
    def __init__(self, pos, im_build, *group):
        super().__init__(*group)
        self.image = load_image(im_build)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def update(self, *args):
        self.image = load_image(args[0])


class Board:
    def __init__(self, width, height, group):
        self.width = width
        self.height = height
        self.group = group
        self.board = [['' for _ in range(width)] for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 40

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def build(self, x, y):
        preset = [[0 < y and self.board[y - 1][x].isdigit()], [0 < x and self.board[y][x - 1].isdigit(),
                                                               x + 1 < self.width and self.board[y][x + 1].isdigit()],
                  [y + 1 > self.height and self.board[y + 1][x].isdigit()]]
        im = [key for key, pres in presets.items() if pres == preset][0]
        if im == '7':
            if not self.board[y + 1][x + 1].isdigit():
                im = '14'
        elif im == '6':
            if not self.board[y - 1][x + 1].isdigit():
                im = '17'
        elif im == '5':
            if not self.board[y - 1][x - 1].isdigit():
                im = '16'
        elif im == '4':
            if not self.board[y + 1][x - 1].isdigit():
                im = '15'
        return im

    def update(self, x, y):
        pass

    def render(self, screen):
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(screen, pygame.Color('white'), (self.left + j * self.cell_size,
                                                                 self.top + i * self.cell_size, self.cell_size,
                                                                 self.cell_size), 1)

    def get_cell(self, pos):
        x, y = pos[0] - self.left, pos[1] - self.top
        if 0 <= x <= self.width * self.cell_size and 0 <= y <= self.height * self.cell_size:
            w, h = x // self.cell_size, y // self.cell_size
            return w, h

    def on_click(self, data):
        x, y = data
        if not self.board[y][x].isdigit():
            built = self.build(x, y)
            self.board[y][x] = built
            if built != '19':
                Floor((x * self.cell_size + self.left, y * self.cell_size + self.top), built, self.group)

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell:
            self.on_click(cell)

    def check(self):
        first = self.board[0][0]
        if all(all(x == first for x in i) for i in self.board):
            print('red won' if first == 0 else 'blue won')
            return True


if __name__ == '__main__':
    pygame.display.set_caption('')
    running = True
    all_sprites = pygame.sprite.Group()
    board = Board(48, 27, all_sprites)
    screen.fill((0, 0, 0))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                board.get_click(event.pos)
        board.render(screen)
        all_sprites.draw(screen)
        pygame.display.flip()
    pygame.quit()
