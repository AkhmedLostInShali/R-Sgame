import pygame
import os
import sys

pygame.init()
size = width, height = 1920, 980
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
    def __init__(self, coords, im_build, pos, *group):
        super().__init__(*group)
        self.image = im_build
        self.rect = self.image.get_rect()
        self.rect.x = coords[0]
        self.rect.y = coords[1]
        self.pos = pos
        self.mother = group[0]

    def update(self, *args):
        x, y = self.pos
        self.image = self.mother.build(x, y)


class SceneBoard(pygame.sprite.Group):
    def __init__(self, width, height, *sprites):
        super().__init__(*sprites)
        self.width = width
        self.height = height
        self.board = [['.' for _ in range(width)] for _ in range(height)]
        self.left = 10
        self.top = 10
        self.cell_size = 40

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def build(self, x, y):
        im = pygame.surface.Surface((40, 40))
        im.fill((100, 100, 120))
        up = 0 < y and self.board[y - 1][x].isdigit()
        down = y + 1 < self.height and self.board[y + 1][x].isdigit()
        right = x + 1 < self.width and self.board[y][x + 1].isdigit()
        left = x > 0 and self.board[y][x - 1].isdigit()
        if not up:
            pygame.Surface.blit(im, load_image('top'), (0, 0))
            if not right:
                pygame.Surface.blit(im, load_image('top_right'), (0, 0))
                if down:
                    pygame.Surface.blit(im, load_image('low_right'), (0, 0))
            if not left:
                pygame.Surface.blit(im, load_image('top_left'), (0, 0))
                if down:
                    pygame.Surface.blit(im, load_image('low_left'), (0, 0))
        if not down:
            pygame.Surface.blit(im, load_image('bottom'), (0, 0))
            if not right:
                pygame.Surface.blit(im, load_image('bottom_right'), (0, 0))
                if up:
                    pygame.Surface.blit(im, load_image('high_right'), (0, 0))
            if not left:
                pygame.Surface.blit(im, load_image('bottom_left'), (0, 0))
                if up:
                    pygame.Surface.blit(im, load_image('high_left'), (0, 0))
        if not right and up and down:
            pygame.Surface.blit(im, load_image('high_right'), (0, 0))
            pygame.Surface.blit(im, load_image('low_right'), (0, 0))
        if not left and up and down:
            pygame.Surface.blit(im, load_image('high_left'), (0, 0))
            pygame.Surface.blit(im, load_image('low_left'), (0, 0))
        if left and down and not self.board[y + 1][x - 1].isdigit():
            pygame.Surface.blit(im, load_image('inner_top_right'), (0, 0))
        if right and down and not self.board[y + 1][x + 1].isdigit():
            pygame.Surface.blit(im, load_image('inner_top_left'), (0, 0))
        if left and up and not self.board[y - 1][x - 1].isdigit():
            pygame.Surface.blit(im, load_image('inner_bottom_right'), (0, 0))
        if right and up and not self.board[y - 1][x + 1].isdigit():
            pygame.Surface.blit(im, load_image('inner_bottom_left'), (0, 0))
        return im

    def render(self, screen):
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(screen, pygame.Color('white'), (self.left + j * self.cell_size,
                                                                 self.top + i * self.cell_size, self.cell_size,
                                                                 self.cell_size), 1)
        self.draw(screen)

    def get_cell(self, pos):
        x, y = pos[0] - self.left, pos[1] - self.top
        if 0 <= x <= self.width * self.cell_size and 0 <= y <= self.height * self.cell_size:
            w, h = x // self.cell_size, y // self.cell_size
            return w, h

    def on_click(self, data):
        x, y = data
        if not self.board[y][x].isdigit():
            built = self.build(x, y)
            self.board[y][x] = '1'
            Floor((x * self.cell_size + self.left, y * self.cell_size + self.top), built, data, self)
            self.update()

    def get_click(self, mouse):
        cell = self.get_cell(mouse.pos)
        if cell:
            self.on_click(cell)
        return cell

    def check(self):
        first = self.board[0][0]
        if all(all(x == first for x in i) for i in self.board):
            print('red won' if first == 0 else 'blue won')
            return True

    def save(self, filename):
        text = ''
        for i in range(self.height):
            for j in range(self.width):
                text += self.board[i][j]
            text += '\n'
        with open(filename, 'wt', encoding='utf-8') as f:
            f.write(text)


if __name__ == '__main__':
    pygame.display.set_caption('')
    running = True
    board = SceneBoard(32, 18)
    screen.fill((0, 0, 0))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = board.get_click(event)
            if event.type == pygame.KEYDOWN:
                board.save(input() + '.txt')
        board.render(screen)
        pygame.display.flip()
    pygame.quit()
