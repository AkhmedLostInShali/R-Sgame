import os
import sys
import pygame
from math import hypot
from data_funcs import load_image, load_level, build, cut_sheet
from buildings import Tile, Platform, Rail, Portal, Background
from settings_n_variables import FPS, FULL_SIZE, WIDTH, HEIGHT, tile_width, tile_height, STATS, ENEMY_STATS
from projectiles_n_movings import Projectile, Plasma, SunDrop
from enemies import Enemy, Mortar
from initialisation import enemy_group, player_group, projectile_group, all_sprites, portal_group, rail_group
from initialisation import floor_group, weapon_group
from interface import StatBar, EnemyHealthBar

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode(FULL_SIZE)
player = None


def generate_level(level):
    new_player, x, y = None, None, None
    player_xy = (15, 8)
    new_player = Player(*player_xy)
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '1':
                Tile((x, y), build(level, x, y), floor_group, all_sprites)
            elif level[y][x] == '2':
                Platform((x, y), floor_group, all_sprites)
            elif level[y][x] == '3':
                Rail((x, y), rail_group, all_sprites)
            elif level[y][x] == '4':
                Portal((x, y), portal_group, all_sprites)
            elif level[y][x] == 'm':
                Rail((x, y), rail_group, all_sprites)
                Mortar((x, y), rail_group, new_player, [player_group, floor_group], enemy_group, all_sprites)
    # floor_group.update(level)
    return new_player, x, y


class Player(pygame.sprite.Sprite):
    player_image = load_image('torso')

    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.static = 'float'
        all_sprites.change_layer(self, 4)
        self.image = self.player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x - 24, tile_height * pos_y - 24)
        self.change_x = 0
        self.change_y = 0
        self.fall = 0
        self.float_x = self.rect.x
        self.float_y = self.rect.y
        self.speed = 120 / FPS
        self.invincibility = 0
        self.stat_bar = StatBar(all_sprites)
        self.weapon = CosmoWeapon()

    def add_values(self, value):
        self.stat_bar.change_health(value[0])
        self.stat_bar.change_mana(value[2])

    def take_damage(self, damage):
        if not self.invincibility:
            self.stat_bar.change_health(-damage)
            self.invincibility = 1.25 * FPS

    def check_pulse(self):
        return self.stat_bar.is_alive()

    def update(self, *args):
        if not self.check_pulse():
            return 'death'
        self.calc_grav()
        self.float_x += self.change_x
        self.rect.x = round(self.float_x)
        block_hit = pygame.sprite.spritecollide(self, floor_group, False)
        floor_hit = list(filter(lambda x: not isinstance(x, Platform), block_hit)) if block_hit else None
        if floor_hit:
            if self.change_x > 0:
                self.rect.right = floor_hit[0].rect.left
                self.float_x = self.rect.x
            elif self.change_x < 0:
                self.rect.left = floor_hit[0].rect.right
                self.float_x = self.rect.x
        self.float_y += self.change_y
        self.rect.y = round(self.float_y)
        block_hit = pygame.sprite.spritecollideany(self, floor_group)
        if block_hit:
            if not isinstance(block_hit, Platform):
                if self.change_y < 0:
                    self.rect.top = block_hit.rect.bottom
                    self.float_y = self.rect.y
                elif self.change_y > 0:
                    self.rect.bottom = block_hit.rect.top
                    self.float_y = self.rect.y
                self.change_y = 0
            else:
                if self.change_y > 0 and self.rect.bottom - self.change_y < block_hit.rect.top + 1 and not self.fall:
                    self.rect.bottom = block_hit.rect.top
                    self.float_y = self.rect.y
                    self.change_y = 0
        self.fall -= 1 if self.fall else 0
        self.weapon.rect.x = self.rect.x + 8
        self.weapon.rect.y = self.rect.y + 2
        self.invincibility = max(self.invincibility - 1, 0)

    def calc_grav(self):
        if self.change_y == 0:
            self.change_y = .5 / FPS
        else:
            self.change_y += 9.8 / FPS
            self.change_y = 280 / FPS if self.change_y > 280 / FPS else self.change_y
        # if self.rect.y >= FULL_SIZE[1] - self.rect.height and and self.change_y >= 0:
        #     self.change_y = 0
        #     self.rect.y = FULL_SIZE[1] - self.rect.height

    def jump(self):
        self.rect.y += 1
        ground_hit = pygame.sprite.spritecollideany(self, floor_group)
        on_ground = ground_hit and (not isinstance(ground_hit, Platform) or self.rect.bottom == ground_hit.rect.top + 1)
        self.rect.y -= 1
        if on_ground:
            self.change_y = -500 / FPS

    def dismount(self):
        self.rect.y += 1
        ground_hit = pygame.sprite.spritecollideany(self, floor_group)
        on_platform = ground_hit and isinstance(ground_hit, Platform) and self.rect.bottom == ground_hit.rect.top + 1
        self.rect.y -= 1
        if on_platform:
            self.fall = FPS // 3

    def go_left(self):
        self.change_x = -self.speed

    def go_right(self):
        self.change_x = self.speed

    def stop(self):
        self.change_x = 0


class CosmoWeapon(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(weapon_group, all_sprites)
        self.static = False
        all_sprites.change_layer(self, 5)
        self.color = (215, 215, 185)
        self.dmg = STATS['damage'] * 0.7
        self.image = pygame.surface.Surface((48, 48), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, self.color, (24, 24), 10, 0)
        self.image.blit(load_image('cosmo_weapon'), (0, 0))
        self.orig_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.cooldown = [0, 1 * FPS]
        self.angle = 0

    def update(self, angle):
        rot_image = pygame.transform.rotate(self.orig_image, angle)
        rot_rect = self.rect.copy()
        rot_rect.center = rot_image.get_rect().center
        self.image = rot_image.subsurface(rot_rect).copy()
        self.angle = angle
        self.cooldown[0] -= 1 if self.cooldown[0] else 0

    def attack(self, vector):
        if not self.cooldown[0]:
            SunDrop(self.rect.center, ('straight', self.angle), vector, self.dmg,
                    (enemy_group, floor_group), projectile_group, all_sprites)
            self.cooldown[0] = self.cooldown[1]


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
        if obj.static and obj.static != 'float':
            return
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        if obj.static == 'float':
            obj.float_x += self.dx
            obj.float_y += self.dy

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


def bridge():
    pass


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


def death_screen():
    terminate()


def main():
    global player
    running = True
    player, level_x, level_y = generate_level(load_level('level1.txt'))
    Background('wall_background', all_sprites)
    FULL_SIZE = ((level_x + 1) * tile_width, (level_y + 1) * tile_height)
    view_size = (min((1920, FULL_SIZE[0])), min((1080, FULL_SIZE[1])))
    screen = pygame.display.set_mode(FULL_SIZE)
    camera = Camera(FULL_SIZE, view_size)
    portal = portal_group.sprites()[0]
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_UP]:
                    player.jump()
                if pressed[pygame.K_DOWN]:
                    player.dismount()
                if pressed[pygame.K_RIGHT]:
                    player.go_right()
                if pressed[pygame.K_LEFT]:
                    player.go_left()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    player.stop()
                if event.key == pygame.K_LEFT:
                    player.stop()
            if event.type == pygame.MOUSEBUTTONUP:
                a = event.pos[0] - player.weapon.rect.centerx
                b = event.pos[1] - player.weapon.rect.centery
                player.weapon.attack((a/hypot(a, b), b/hypot(a, b)))
        point = pygame.math.Vector2(player.weapon.rect.centerx, player.weapon.rect.centery)
        mouse_pos = pygame.math.Vector2(*pygame.mouse.get_pos())
        radius, angle = (mouse_pos - point).as_polar()
        if player.update() == 'death':
            death_screen()
        weapon_group.update(-angle)
        camera.update(player)
        projectile_group.update()
        rail_group.update()
        enemy_group.update()
        if not enemy_group.sprites() and portal.rect.collidepoint(player.rect.center):
            portal.activate()
        if portal.update() == 'teleport':
            return portal.xp
        for sprite in all_sprites:
            camera.apply(sprite)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == '__main__':
    # start_screen()
    print(main())
