import pygame
from math import hypot
from data_funcs import load_image, cut_sheet
from settings_n_variables import FPS
from buildings import Platform


class Projectile(pygame.sprite.Sprite):
    def __init__(self, name, pos, trajectory, vector, dmg, collides, *group):
        super().__init__(*group)
        group[-1].change_layer(self, 2)
        self.static = 'float'
        self.dmg = dmg
        self.trajectory = trajectory[0]
        self.collides = list(collides)
        self.change_x, self.change_y = vector
        self.frames = cut_sheet(load_image(name + '_projectile'), 8)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = pos
        # rot_image = pygame.transform.rotate(self.image, trajectory[1]) !!!this part can be used in future!!!
        # rot_rect = self.rect.copy()
        # rot_rect.center = rot_image.get_rect().center
        # self.image = rot_image.subsurface(rot_rect).copy()
        self.float_x, self.float_y = self.rect.x, self.rect.y
        self.speed = 400 / FPS

    def update(self, *args, **kwargs):
        if self.trajectory == 'parabolic':
            self.change_y += 9.8 / FPS
        self.float_x += self.change_x * self.speed
        self.float_y += self.change_y * self.speed
        self.rect.x = round(self.float_x)
        self.rect.y = round(self.float_y)

    def collisions(self, ratio, group):
        pl_collisions = pygame.sprite.spritecollideany(self, group,
                                                       collided=pygame.sprite.collide_circle_ratio(ratio))
        if pl_collisions and not isinstance(pl_collisions, Platform):
            pl_collisions.take_damage(self.dmg)
            self.detonate()

    def detonate(self):
        self.kill()


class Explosion(Projectile):
    def __init__(self, pos, dmg, collides, *group):
        super().__init__('explosion', pos, (0, 0), (0, 0), dmg, collides, *group)
        group[-1].change_layer(self, 5)
        self.rect.center = pos

    def update(self):
        self.cur_frame = (self.cur_frame + 16 / FPS)
        self.image = self.frames[round(self.cur_frame) % len(self.frames)]
        for group in self.collides:
            self.collisions(round(self.cur_frame) % len(self.frames) / 8, group)
        if self.cur_frame > 7:
            self.detonate()

    def collisions(self, ratio, group):
        pl_collisions = pygame.sprite.spritecollideany(self, group,
                                                       collided=pygame.sprite.collide_circle_ratio(ratio))
        if pl_collisions and not isinstance(pl_collisions, Platform):
            pl_collisions.take_damage(self.dmg)


class SunDrop(Projectile):
    def __init__(self, pos, trajectory, vector, dmg, collides, *group):
        super().__init__('drop', pos, (trajectory, 0), vector, dmg, collides, *group)

    def update(self, *args, **kwargs):
        super().update()
        self.cur_frame = (self.cur_frame + 8 / FPS)
        self.image = self.frames[round(self.cur_frame) % len(self.frames)]
        for group in self.collides:
            self.collisions(.625, group)

    def detonate(self):
        self.kill()


class Plasma(Projectile):
    def __init__(self, pos, trajectory, vector, dmg, collides, *group):
        super().__init__('plasma', pos, (trajectory, 0), vector, dmg, collides, *group)
        self.speed = 120 / FPS
        self.timer = 0.35 * FPS

    def update(self, *args, **kwargs):
        super().update()
        self.cur_frame = (self.cur_frame + 12 / FPS)
        self.image = self.frames[round(self.cur_frame) % len(self.frames)]
        if self.timer == 0.35 * FPS:
            collisions = pygame.sprite.spritecollideany(self, self.collides[0],
                                                        collided=pygame.sprite.collide_circle_ratio(1.65))
            if collisions:
                self.timer -= 1
        elif 0 < self.timer < 0.35 * FPS:
            self.timer -= 1
        else:
            self.detonate()
        for group in self.collides:
            self.collisions(.4375, group)

    def detonate(self):
        Explosion(self.rect.center, self.dmg, self.collides, *self.groups())
        self.kill()


class Defence(Projectile):
    def __init__(self, pos, dmg, collides, *group):
        super().__init__('defence', pos, (0, 0), (0, 0), dmg, collides, *group)
        self.rect.center = pos

    def collisions(self, ratio, group):
        pl_collisions = pygame.sprite.spritecollide(self, group, False,
                                                    collided=pygame.sprite.collide_circle_ratio(ratio))
        for col in pl_collisions:
            col.defend(self.dmg)

    def update(self):
        self.cur_frame = (self.cur_frame + 3 / FPS)
        self.image = self.frames[round(self.cur_frame) % len(self.frames)]
        for group in self.collides:
            self.collisions(1.0, group)


class Orb(pygame.sprite.Sprite):
    def __init__(self, value, pos, target, *group):
        self.static = 'float'
        super().__init__(*group)
        group[-1].change_layer(self, 5)
        self.value = value
        self.color = (min(155 + value[0] * 5, 255), min(155 + value[1] * 3, 255), min(155 + value[2], 255))
        self.image = pygame.surface.Surface((10, 10), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, self.color, (5, 5), 4, 0)
        pygame.draw.circle(self.image, (100, 100, 100), (5, 5), 4, 1)
        self.target = target
        self.rect = self.image.get_rect()
        self.rect.center = pos
        a = target.rect.centerx - pos[0]
        b = target.rect.centery - pos[1]
        self.change_x, self.change_y = a/hypot(a, b), b/hypot(a, b)
        self.float_x, self.float_y = self.rect.x, self.rect.y
        self.speed = 40 / FPS

    def update(self, *args, **kwargs):
        self.float_x += self.change_x * self.speed
        self.float_y += self.change_y * self.speed
        self.rect.x = round(self.float_x)
        self.rect.y = round(self.float_y)
        a = self.target.rect.centerx - self.rect.centerx
        b = self.target.rect.centery - self.rect.centery
        self.change_x, self.change_y = a/hypot(a, b), b/hypot(a, b)
        self.speed += 0.6 / FPS
        self.collisions()

    def collisions(self):
        if self.target.rect.collidepoint(self.rect.center):
            self.target.add_values(self.value)
            self.detonate()

    def detonate(self):
        self.kill()
