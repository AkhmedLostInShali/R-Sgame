import pygame
import os
import sys
pygame.init()
FULL_SIZE = WIDTH, HEIGHT = 1920, 1080
pre_screen = pygame.display.set_mode(FULL_SIZE)


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


def cut_sheet(sheet, columns):
    rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height())
    frames = []
    for i in range(columns):
        frame_location = (rect.w * i, 0)
        frames.append(sheet.subsurface(pygame.Rect(frame_location, rect.size)))
    return frames


def load_level(filename):
    if not os.path.isfile(os.path.join('levels', filename)):
        print(f"Файл с уровнем '{filename}' не найден")
        sys.exit()
    with open("levels/" + filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map[:-2])) + [level_map[-2:]]


def build(matrix, x, y):
    im = pygame.surface.Surface((40, 40))
    im.fill((100, 100, 120))
    up = 0 < y and matrix[y - 1][x] == '1'
    down = y + 1 < len(matrix) and matrix[y + 1][x] == '1'
    right = x + 1 < len(matrix[0]) and matrix[y][x + 1] == '1'
    left = x > 0 and matrix[y][x - 1] == '1'
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
    if left and down and not matrix[y + 1][x - 1] == '1':
        pygame.Surface.blit(im, load_image('inner_top_right'), (0, 0))
    if right and down and not matrix[y + 1][x + 1] == '1':
        pygame.Surface.blit(im, load_image('inner_top_left'), (0, 0))
    if left and up and not matrix[y - 1][x - 1] == '1':
        pygame.Surface.blit(im, load_image('inner_bottom_right'), (0, 0))
    if right and up and not matrix[y - 1][x + 1] == '1':
        pygame.Surface.blit(im, load_image('inner_bottom_left'), (0, 0))
    return im
