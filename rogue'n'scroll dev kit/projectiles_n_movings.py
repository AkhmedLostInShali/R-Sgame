import pygame
from data_funcs import load_image, cut_sheet
from settings_n_variables import FPS
from buildings import Platform


class Projectile(pygame.sprite.Sprite):
    def __init__(self, name, pos, trajectory, vector, dmg, collides, *group):
        super().__init__(*group)
        group[-1].change_layer(self, 2)
        self.dmg = dmg
        self.trajectory = trajectory[0]
        self.collides = list(collides)
        self.change_x, self.change_y = vector
        self.frames = cut_sheet(load_image(name + '_projectile'), 8)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.centerx, self.rect.centery = pos
        # rot_image = pygame.transform.rotate(self.image, trajectory[1])
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

# class Explosion(Projectile):
#     def __init__(self, pos):
#         super().__init__('explosion', pos, (0, 0), (0, 0))


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
        self.speed = 25 / FPS
        self.timer = 1.5

    def update(self, *args, **kwargs):
        super().update()
        self.cur_frame = (self.cur_frame + 8 / FPS)
        self.image = self.frames[round(self.cur_frame) % len(self.frames)]
        if self.timer == 1.5:
            collisions = pygame.sprite.spritecollideany(self, self.collides[0],
                                                        collided=pygame.sprite.collide_circle_ratio(1.65))
            if collisions:
                self.timer -= 1 / FPS
        elif 0 < self.timer < 2.5:
            self.timer -= 1 / FPS
        else:
            self.detonate()
        for group in self.collides:
            self.collisions(.4375, group)

    def detonate(self):
        self.kill()
