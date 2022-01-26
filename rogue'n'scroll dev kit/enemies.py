from random import randrange

import pygame

from data_funcs import load_image, cut_sheet
from initialisation import projectile_group, portal_group, player_group
from interface import EnemyHealthBar
from projectiles_n_movings import Plasma, Orb, Defence
from settings_n_variables import FPS, tile_width, tile_height


class Enemy(pygame.sprite.Sprite):
    def __init__(self, name, frames, pos, target, stats, hits, *group):
        super().__init__(*group)
        self.static = 'float'
        group[-1].change_layer(self, 3)
        self.hp = self.max_hp = stats['HP']
        self.bar = None
        self.dmg = stats['damage']
        self.defence = 0
        self.target = target
        self.hits = hits
        self.frames = cut_sheet(load_image(name), frames)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * tile_width
        self.rect.bottom = (pos[1] + 1) * tile_height
        self.float_x, self.float_y = self.rect.x, self.rect.y
        self.invincibility = 0

    def defend(self, value):
        self.defence = value

    def take_damage(self, damage):
        if not self.invincibility:
            self.hp -= (damage - self.defence)
            self.invincibility = 0.75 * FPS
        if not self.bar:
            self.bar = EnemyHealthBar(self.hp, self.max_hp, self.groups()[-1])
        else:
            self.bar.kill()
            self.bar = EnemyHealthBar(self.hp, self.max_hp, self.groups()[-1])
        if self.hp <= 0:
            self.death()

    def death(self):
        self.bar.kill()
        self.bar = None
        Orb((randrange(0, 20), 0, randrange(10, 20)), self.rect.center, player_group.sprites()[0],
            projectile_group, self.groups()[-1])
        Orb((0, randrange(10, 20), 0), self.rect.center, portal_group.sprites()[0],
            projectile_group, self.groups()[-1])
        self.kill()


class Mortar(Enemy):
    def __init__(self, pos, rails, target, stats, hits, *group, orientation='bottom'):
        super().__init__("mortar_" + orientation, 5, pos, target, stats, hits, *group)
        self.rails = rails
        self.dmg *= 1.8
        self.cur_frame = 2
        # self.rect.x += 20
        self.charge_effect = cut_sheet(load_image('mortar_charge'), 8)
        self.charge = 0
        self.image = self.frames[self.cur_frame]
        self.image.blit(self.charge_effect[self.charge], (25, 32))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * tile_width
        self.rect.bottom = (pos[1] + 1) * tile_width - 2
        self.speed = 36 / FPS

    def update(self):
        self.rect.x -= 64
        left = pygame.sprite.spritecollideany(self, self.rails)
        self.rect.x += 64
        self.rect.x += 64
        right = pygame.sprite.spritecollideany(self, self.rails)
        self.rect.x -= 64
        if self.target.rect.x < self.rect.x and left:
            self.float_x -= self.speed
        elif self.target.rect.x > self.rect.x and right:
            self.float_x += self.speed
        self.rect.x = round(self.float_x)
        self.charge += 1 / FPS
        point = pygame.math.Vector2(self.target.rect.centerx, self.target.rect.centery)
        mort_pos = pygame.math.Vector2((self.rect.centerx, self.rect.bottom - 11))
        angle = (mort_pos - point).as_polar()[1] - 90
        self.cur_frame = 2 + max((-2, min([round(angle // 22.5), 2])))
        self.image = self.frames[self.cur_frame]
        self.image.blit(self.charge_effect[round(self.charge % 7)], (25, 33))
        if self.charge > 6:
            self.attack()
            self.charge = 0
        self.invincibility = max(self.invincibility - 1, 0)
        self.defence = 0

    def attack(self):
        vectors = [(-0.5, -0.5), (-0.25, -0.75), (0, -1), (0.25, -0.75), (0.5, -0.5)]
        Plasma((self.rect.centerx, self.rect.bottom - 11), 22.5 * (self.cur_frame - 2), vectors[self.cur_frame],
               self.dmg, self.hits, projectile_group, self.groups()[-1])


class Defender(Enemy):
    def __init__(self, pos, stats, hits, *group):
        super().__init__("defender", 8, pos, None, stats, hits, *group)
        self.dmg *= 0.25
        self.max_hp *= 0.5
        self.hp = self.max_hp
        self.sphere = Defence(self.rect.center, self.dmg, self.hits, projectile_group, self.groups()[-1])

    def update(self):
        self.cur_frame = (self.cur_frame + 3 / FPS)
        self.image = self.frames[round(self.cur_frame) % len(self.frames)]
        self.invincibility = max(self.invincibility - 1, 0)

    def death(self):
        self.sphere.detonate()
        super().death()
