import pygame
from main import enemy_group, all_sprites, ENEMY_STATS, cut_sheet, load_image, tile_width


class Enemy(pygame.sprite.Sprite):
    def __init__(self, name, frames, pos):
        super().__init__(enemy_group, all_sprites)
        all_sprites.change_layer(self, 3)
        self.hp = self.max_hp = ENEMY_STATS['HP']
        self.frames = cut_sheet(load_image(name), frames)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * tile_width
        self.rect.bottom = (pos[1] + 1) * tile_width
        self.float_x, self.float_y = self.rect.x, self.rect.y

    def take_damage(self, damage):
        global enemy_health
        self.hp -= damage
        if self.hp <= 0:
            self.death()
        if not enemy_health:
            enemy_health = EnemyHealthBar(self.hp, self.max_hp)
        else:
            enemy_health.kill()
            enemy_health = EnemyHealthBar(self.hp, self.max_hp)

    def death(self):
        self.kill()


class Mortar(Enemy):
    def __init__(self, pos, orientation='bottom'):
        super().__init__("mortar_" + orientation, 5, pos)
        self.cur_frame = 2
        # self.rect.x += 20
        self.charge_effect = cut_sheet(load_image('mortar_charge'), 8)
        self.charge = 0
        self.image = self.frames[self.cur_frame]
        self.image.blit(self.charge_effect[self.charge], (25, 32))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * tile_width
        self.rect.bottom = (pos[1] + 1) * tile_width - 2
        self.speed = 12 / FPS

    def update(self, *args, **kwargs):
        self.rect.x -= 64
        left = pygame.sprite.spritecollideany(self, rail_group)
        self.rect.x += 64
        self.rect.x += 64
        right = pygame.sprite.spritecollideany(self, rail_group)
        self.rect.x -= 64
        if PLAYER.rect.x < self.rect.x and left:
            self.float_x -= self.speed
        elif PLAYER.rect.x > self.rect.x and right:
            self.float_x += self.speed
        self.rect.x = round(self.float_x)
        self.charge += 2 / FPS
        point = pygame.math.Vector2(PLAYER.rect.centerx, PLAYER.rect.centery)
        mort_pos = pygame.math.Vector2((self.rect.centerx, self.rect.bottom - 11))
        angle = (mort_pos - point).as_polar()[1] - 90
        self.cur_frame = 2 + max((-2, min([round(angle // 22.5), 2])))
        self.image = self.frames[self.cur_frame]
        self.image.blit(self.charge_effect[round(self.charge % 7)], (25, 33))
        if self.charge > 6:
            self.attack()
            self.charge = 0

    def attack(self):
        vectors = [(-0.5, -0.5), (-0.25, -0.75), (0, -1), (0.25, -0.75), (0.5, -0.5)]
        Plasma((self.rect.centerx, self.rect.bottom - 11), 22.5 * (self.cur_frame - 2), vectors[self.cur_frame])


