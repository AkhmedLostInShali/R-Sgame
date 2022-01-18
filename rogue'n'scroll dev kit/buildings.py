import pygame
from data_funcs import load_image, cut_sheet
from settings_n_variables import tile_width, tile_height, FPS


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, im_build, *group):
        super().__init__(*group)
        group[-1].change_layer(self, 1)
        self.image = im_build
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * tile_width
        self.rect.y = pos[1] * tile_height

    def take_damage(self, *args):
        pass

    # def update(self, level):
    #     x, y = self.rect.x // tile_width, self.rect.y // tile_height
    #     self.image = build(level, x, y)


class Platform(Tile):
    platform_image = load_image('platforms')

    def __init__(self, pos, *group):
        super().__init__(pos, self.platform_image, *group)
        self.rect.height = 7


class Portal(pygame.sprite.Sprite):
    charged_frames = cut_sheet(load_image('portal_charged'), 18)
    uncharged_frames = cut_sheet(load_image('portal_uncharged'), 18)

    def __init__(self, pos, *group):
        super().__init__(*group)
        group[-1].change_layer(self, 1)
        self.charged = False
        self.cur_frames = 0
        self.image = self.uncharged_frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * tile_width
        self.rect.y = pos[1] * tile_height

    def activate(self):
        if round(self.cur_frames) == 0:
            self.charged = True
        # self.cur_frames = 0

    def update(self):
        self.cur_frames = (self.cur_frames + 6 / FPS) % 18
        if self.charged:
            self.image = self.charged_frames[round(self.cur_frames // 1)]
            if self.cur_frames > 17:
                return 'teleport'
        else:
            self.image = self.uncharged_frames[round(self.cur_frames // 1)]

    def teleport(self):
        pass


class Rail(pygame.sprite.Sprite):
    rail_frames = cut_sheet(load_image('rail'), 8)

    def __init__(self, pos, *group):
        super().__init__(*group)
        group[-1].change_layer(self, 3)
        self.cur_frame = 0
        self.image = self.rail_frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * tile_width
        self.rect.y = pos[1] * tile_height - 5

    def update(self):
        self.cur_frame = (self.cur_frame + 6 / FPS) % 7
        self.image = self.rail_frames[round(self.cur_frame)]
