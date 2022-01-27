import os
import sys
from math import hypot
from random import choice, sample

import pygame

from buildings import Tile, Platform, Rail, Portal, Background
from data_funcs import load_image, load_level, build, dump_add_xp, load_xp
from enemies import Mortar, Defender
from initialisation import enemy_group, player_group, projectile_group, all_sprites, portal_group, rail_group
from initialisation import floor_group, weapon_group
from interface import StatBar, Button
from projectiles_n_movings import SunDrop, Orb
from settings_n_variables import FPS, FULL_SIZE, tile_width, tile_height, STATS, ENEMY_STATS, lvl
from settings_n_variables import buff_texts

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode(FULL_SIZE)
player = None


def generate_level(level, person=False, en_stats=ENEMY_STATS):
    new_player, x, y = None, None, None
    if not person:
        player_xy = (15, 8)
        new_player = Player(*player_xy)
    back, sound = level[-1]
    level = level[:-1]
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
                Mortar((x, y), rail_group, new_player if not player else player, en_stats,
                       [player_group, floor_group], enemy_group, all_sprites)
            elif level[y][x] == 'd':
                Defender((x, y), en_stats, [enemy_group], enemy_group, all_sprites)
    return new_player, x, y, back, sound


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
        self.buffs = []
        self.MP_regen = 3 / FPS
        self.MP_used = 0
        self.stat_bar = StatBar(all_sprites)
        self.weapon = CosmoWeapon()

    def add_values(self, value):
        experience = self.stat_bar.change_health(value[0], xp_sigil='sigil_XP_boost' in self.buffs)
        if experience:
            Orb((0, experience, 0), self.rect.center, portal_group.sprites()[0],
                projectile_group, self.groups()[-1])
        self.stat_bar.change_mana(value[2])

    def take_damage(self, damage):
        if not self.invincibility and damage > 0:
            self.stat_bar.change_health(-damage)
            self.invincibility = 1.25 * FPS

    def take_mana(self, mana):
        result = self.stat_bar.change_mana(mana)
        if result and mana < 0 and 'sigil_MP_boost' in self.buffs:
            self.MP_used += -mana
        return self.stat_bar.change_mana(mana)

    def check_pulse(self):
        return self.stat_bar.is_alive()

    def apply_buff(self, buff):
        if buff == 'temp_MP_boost':
            self.stat_bar.increase_max(mana=0.2)
        elif buff == 'temp_HP_boost':
            self.stat_bar.increase_max(health=0.15)
        elif buff == 'temp_DMG_boost':
            self.weapon.increase_dmg(0.2)
        elif buff == 'sigil_MP_boost':
            self.buffs.append(buff)
            self.MP_regen += 2 / FPS
        elif buff == 'sigil_XP_boost':
            self.buffs.append(buff)
        if 'sigil_XP_boost' in self.buffs:
            return self.stat_bar.get_value(key='MP', cur=True)

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
        elif self.change_x > self.speed or self.change_x < -self.speed:
            if not self.take_mana(-15 / FPS):
                self.change_x = self.speed * (1 if self.change_x > 0 else -1)
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
        self.take_mana(self.MP_regen)
        self.weapon.rect.x = self.rect.x + 8
        self.weapon.rect.y = self.rect.y + 2
        self.invincibility = max(self.invincibility - 1, 0)

    def calc_grav(self):
        if self.change_y == 0:
            self.change_y = .5 / FPS
        else:
            self.change_y += 9.8 / FPS
            self.change_y = 280 / FPS if self.change_y > 280 / FPS else self.change_y

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

    def go_left(self, shift=False):
        if shift:
            self.change_x = -self.speed * 1.8
        else:
            self.change_x = -self.speed

    def go_right(self, shift=False):
        if shift:
            self.change_x = self.speed * 1.8
        else:
            self.change_x = self.speed

    def stop(self, orientation):
        if orientation == 'right':
            self.change_x = min(0, self.change_x)
        if orientation == 'left':
            self.change_x = max(0, self.change_x)
        if orientation == 'both':
            self.change_x = 0

    def attack(self, vector):
        self.weapon.attack(vector, mp_buff=self.MP_used)


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

    def increase_dmg(self, bonus):
        self.dmg *= 1 + bonus

    def update(self, angle):
        rot_image = pygame.transform.rotate(self.orig_image, angle)
        rot_rect = self.rect.copy()
        rot_rect.center = rot_image.get_rect().center
        self.image = rot_image.subsurface(rot_rect).copy()
        self.angle = angle
        self.cooldown[0] -= 1 if self.cooldown[0] else 0

    def attack(self, vector, mp_buff=0):
        if not self.cooldown[0]:
            damage = self.dmg * (1 + mp_buff / 5000)
            SunDrop(self.rect.center, ('straight', self.angle), vector, damage,
                    (enemy_group, floor_group), projectile_group, all_sprites)
            self.cooldown[0] = self.cooldown[1]


class Camera:
    def __init__(self, full, view):
        self.dx = 0
        self.full_size = full
        self.view_size = view
        self.total_shift = [0, 0]
        self.dy = 0

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


def bridge(number):
    buttons_group = pygame.sprite.Group()
    all_buttons = os.listdir('data/tips')
    if number == 5:
        buttons = sample(list(filter(lambda x: 'sigil' in x, all_buttons)), k=2)
    else:
        buttons = sample(list(filter(lambda x: 'sigil' not in x, all_buttons)), k=3)
    for i in range(3):
        Button(i, buttons[i][:-4], buttons_group)
    running = True
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in buttons_group.sprites():
                    connection = button.clicked(event.pos)
                    if connection:
                        text = str(button)
                        buttons_group.empty()
                        return text
        for button in buttons_group.sprites():
            connection = button.clicked(pygame.mouse.get_pos())
            if connection:
                text = buff_texts[str(button)]
                font = pygame.font.Font(None, 100)
                heading = font.render(text[0], True, (232, 174, 70))
                screen.blit(heading, (FULL_SIZE[0] // 2 - heading.get_width() // 2, 200))
                font = pygame.font.Font(None, 50)
                for i, line in enumerate(text[1]):
                    string = font.render(line, True, (232, 174, 70))
                    screen.blit(string, (FULL_SIZE[0] // 2 - string.get_width() // 2, 750 + i * 50))
        buttons_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def death_screen(experience):
    running = True
    screen.fill((17, 30, 49))
    text = ['GAME OVER',
            f"At this run you've earn {round(experience)} xp.",
            f"Your total xp: {load_xp() + round(experience)}, lvl: {lvl}"]
    font = pygame.font.Font(None, 150)
    text_coord = 50
    for line in text:
        string_rendered = font.render(line, True, pygame.Color((232, 174, 70)))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
    while running:
        for event in pygame.event.get():
            if event.type in [pygame.QUIT, pygame.MOUSEBUTTONDOWN]:
                dump_add_xp(experience)
                terminate()
        pygame.display.flip()
        clock.tick(FPS)


def run_level(buff=None, number=0, name='level1.txt'):
    global player
    if number:
        for sprite in all_sprites:
            if isinstance(sprite, Player) or isinstance(sprite, CosmoWeapon) or isinstance(sprite, StatBar):
                pass
            else:
                sprite.kill()
    running = True
    enemy_stats = {'HP': ENEMY_STATS['HP'] * (1.1 ** number), 'damage': ENEMY_STATS['damage'] * (1.15 ** number)}
    if buff:
        player = player_group.sprites()[0]
        player.weapon = weapon_group.sprites()[0]
        xp_sigil = player.apply_buff(buff)
        player.stat_bar.update()
        _, level_x, level_y, bg, st = generate_level(load_level(name), person=player, en_stats=enemy_stats)
    else:
        xp_sigil = None
        player, level_x, level_y, bg, st = generate_level(load_level(name))
    Background(bg, all_sprites)
    pygame.mixer.init(44100)
    soundtrack = pygame.mixer.Sound('data/' + st)
    soundtrack.play(loops=-1)
    soundtrack.set_volume(0.1)
    full_size = ((level_x + 1) * tile_width, (level_y + 1) * tile_height)
    view_size = (min((1920, full_size[0])), min((1080, full_size[1])))
    camera = Camera(full_size, view_size)
    portal = portal_group.sprites()[0]
    portal.add_level()
    if xp_sigil:
        Orb((0, xp_sigil, 0), player.rect.center, portal, projectile_group, all_sprites)
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_UP]:
                    player.jump()
                if pressed[pygame.K_DOWN]:
                    player.dismount()
                if pressed[pygame.K_RIGHT]:
                    player.go_right(shift=event.mod & pygame.KMOD_SHIFT)
                elif pressed[pygame.K_LEFT]:
                    player.go_left(shift=event.mod & pygame.KMOD_SHIFT)
                if event.key == pygame.K_RIGHT:
                    player.go_right(shift=event.mod & pygame.KMOD_SHIFT)
                elif event.key == pygame.K_LEFT:
                    player.go_left(shift=event.mod & pygame.KMOD_SHIFT)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RSHIFT or event.key == pygame.K_LSHIFT:
                    if pygame.key.get_pressed()[pygame.K_RIGHT]:
                        player.go_right()
                    if pygame.key.get_pressed()[pygame.K_LEFT]:
                        player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.stop('right')
                if event.key == pygame.K_LEFT:
                    player.stop('left')
            if event.type == pygame.MOUSEBUTTONUP:
                a = event.pos[0] - player.weapon.rect.centerx
                b = event.pos[1] - player.weapon.rect.centery
                player.attack((a/hypot(a, b), b/hypot(a, b)))
        point = pygame.math.Vector2(player.weapon.rect.centerx, player.weapon.rect.centery)
        mouse_pos = pygame.math.Vector2(*pygame.mouse.get_pos())
        radius, angle = (mouse_pos - point).as_polar()
        if player.update() == 'death':
            soundtrack.fadeout(2500)
            return portal.xp, 'death'
        weapon_group.update(-angle)
        camera.update(player)
        projectile_group.update()
        rail_group.update()
        enemy_group.update()
        if not enemy_group.sprites() and portal.rect.collidepoint(player.rect.center):
            portal.activate()
        if portal.update() == 'teleport':
            player.stop('both')
            soundtrack.fadeout(2500)
            return portal.xp,  'next'
        for sprite in all_sprites:
            camera.apply(sprite)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    num = 0
    xp = 0
    res = run_level(name=choice(os.listdir('levels')))
    game_is_on = res[1]
    if game_is_on:
        xp += res[0]
    while game_is_on == 'next':
        num += 1
        boost = bridge(num)
        res = run_level(number=num, buff=boost, name=choice(os.listdir('levels')))
        game_is_on = res[1]
        xp += res[0]
    if game_is_on == 'death':
        death_screen(xp)
    dump_add_xp(xp)
