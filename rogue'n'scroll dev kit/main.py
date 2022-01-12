import os
import sys
import pygame
from random import choice
from math import hypot

FPS = 60
pygame.init()
clock = pygame.time.Clock()
FULL_SIZE = WIDTH, HEIGHT = 1920, 1080
pre_screen = pygame.display.set_mode(FULL_SIZE)
enemy_health = None
STATS = {'HP': 100, 'MP': 50, 'damage': 30}
ENEMY_STATS = {'HP': 100, 'damage': 30}
all_sprites = pygame.sprite.LayeredUpdates()
floor_group = pygame.sprite.Group()
# platform_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
weapon_group = pygame.sprite.Group()
rail_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()


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


def generate_level(level):
    x, y = None, None
    # player_xy = (15, 8)
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '1':
                Tile((x, y), build(level, x, y))
            elif level[y][x] == '2':
                Platform((x, y))
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '3':
                Rail((x, y))
            if level[y][x] == 'm':
                Mortar((x, y))
    # floor_group.update(level)
    # new_player = Player(*player_xy)
    return x, y


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
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_width = tile_height = 40


class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, im_build):
        super().__init__(floor_group, all_sprites)
        all_sprites.change_layer(self, 1)
        self.image = im_build
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * tile_width
        self.rect.y = pos[1] * tile_height

    # def update(self, level):
    #     x, y = self.rect.x // tile_width, self.rect.y // tile_height
    #     self.image = build(level, x, y)


class Platform(Tile):
    platform_image = load_image('platforms')

    def __init__(self, pos):
        super().__init__(pos, self.platform_image)
        self.rect.height = 7


class Rail(pygame.sprite.Sprite):
    rail_frames = cut_sheet(load_image('rail'), 8)

    def __init__(self, pos):
        super().__init__(all_sprites, rail_group)
        all_sprites.change_layer(self, 3)
        self.cur_frame = 0
        self.image = self.rail_frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] * tile_width
        self.rect.y = pos[1] * tile_height - 5

    def update(self):
        self.cur_frame = (self.cur_frame + 6 / FPS) % 7
        self.image = self.rail_frames[round(self.cur_frame)]


class StatBar(pygame.sprite.Sprite):
    bar_image = load_image('stat_bar')
    back_image = load_image('stat_bar_back')

    def __init__(self):
        super().__init__(all_sprites)
        all_sprites.change_layer(self, 6)
        self.image = self.back_image.copy()
        self.stats = STATS.copy()
        pygame.draw.rect(self.image, (155, 0, 15), (2, 3, 200, 28))
        pygame.draw.rect(self.image, (15, 0, 155), (2, 38, 160, 21))
        self.image.blit(self.bar_image, (0, 0))
        self.rect = self.image.get_rect()

    def update(self):
        self.image = self.back_image.copy()
        pygame.draw.rect(self.image, (155, 0, 15), (2, 3, self.stats['HP'] * 200 / STATS['HP'], 28))
        pygame.draw.rect(self.image, (15, 0, 155), (2, 38, self.stats['MP'] * 160 / STATS['MP'], 21))
        self.image.blit(self.bar_image, (0, 0))

    def change_health(self, value):
        self.stats['HP'] += value
        if self.stats['HP'] <= 0:
            death_screen()
        self.update()


class Player(pygame.sprite.Sprite):
    player_image = load_image('torso')

    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        all_sprites.change_layer(self, 4)
        self.image = self.player_image
        self.rect = self.image.get_rect().move(tile_width * pos_x - 24, tile_height * pos_y - 24)
        self.change_x = 0
        self.change_y = 0
        self.fall = 0
        self.float_x = self.rect.x
        self.float_y = self.rect.y
        self.speed = 120 / FPS
        self.stat_bar = StatBar()
        self.weapon = CosmoWeapon()

    def take_damage(self, damage):
        self.stat_bar.change_health(-damage)

    def update(self, *args, **kwargs):
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
            self.fall = FPS * 0.3

    def go_left(self):
        self.change_x = -self.speed

    def go_right(self):
        self.change_x = self.speed

    def stop(self):
        self.change_x = 0


class CosmoWeapon(pygame.sprite.Sprite):
    def __init__(self):
        # super().__init__(player_group, all_sprites)
        super().__init__(weapon_group, all_sprites)
        all_sprites.change_layer(self, 4)
        self.color = (215, 215, 185)
        self.image = pygame.surface.Surface((48, 48), pygame.SRCALPHA, 32)
        pygame.draw.circle(self.image, self.color, (24, 24), 10, 0)
        self.image.blit(load_image('cosmo_weapon'), (0, 0))
        self.orig_image = self.image.copy()
        self.rect = self.image.get_rect()
        self.cooldown = [0, 2 * FPS]
        self.angle = 0

    def update(self, angle=0, *args, **kwargs):
        rot_image = pygame.transform.rotate(self.orig_image, angle)
        rot_rect = self.rect.copy()
        rot_rect.center = rot_image.get_rect().center
        self.image = rot_image.subsurface(rot_rect).copy()
        self.angle = angle
        self.cooldown[0] -= 1 if self.cooldown[0] else 0

    def attack(self, vector):
        if not self.cooldown[0]:
            SunDrop(self.rect.center, ('straight', self.angle), vector, friendly=True)
            self.cooldown[0] = self.cooldown[1]


class Projectile(pygame.sprite.Sprite):
    def __init__(self, name, pos, trajectory, vector, friendly=False):
        super().__init__(projectile_group, all_sprites)
        all_sprites.change_layer(self, 2)
        self.trajectory = trajectory[0]
        self.friendly = friendly
        if friendly:
            self.dmg = STATS['damage']
        else:
            self.dmg = ENEMY_STATS['damage']
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

    def collisions(self, ratio):
        pl_collisions = pygame.sprite.spritecollideany(self, player_group,
                                                       collided=pygame.sprite.collide_circle_ratio(ratio))
        if pl_collisions and isinstance(pl_collisions, Player) and not self.friendly:
            pl_collisions.take_damage(self.dmg)
            self.detonate()
        en_collisions = pygame.sprite.spritecollideany(self, enemy_group,
                                                       collided=pygame.sprite.collide_circle_ratio(ratio))
        if en_collisions and isinstance(en_collisions, Enemy) and self.friendly:
            en_collisions.take_damage(self.dmg)
            self.detonate()

        collisions = pygame.sprite.spritecollideany(self,
                                                    floor_group, collided=pygame.sprite.collide_circle_ratio(ratio))
        if collisions and not isinstance(collisions, Platform):
            self.detonate()

    def detonate(self):
        self.kill()

# class Explosion(Projectile):
#     def __init__(self, pos):
#         super().__init__('explosion', pos, (0, 0), (0, 0))


class SunDrop(Projectile):
    def __init__(self, pos, angle, vector, friendly=True):
        super().__init__('drop', pos, ('straight', angle), vector, friendly)

    def update(self, *args, **kwargs):
        super().update()
        self.cur_frame = (self.cur_frame + 8 / FPS)
        self.image = self.frames[round(self.cur_frame) % len(self.frames)]
        self.collisions(.625)

    def detonate(self):
        self.kill()


class Plasma(Projectile):
    def __init__(self, pos, angle, vector, friendly=False):
        super().__init__('plasma', pos, ('straight', angle), vector, friendly)
        self.speed = 25 / FPS
        self.timer = 1.5

    def update(self, *args, **kwargs):
        super().update()
        self.cur_frame = (self.cur_frame + 8 / FPS)
        self.image = self.frames[round(self.cur_frame) % len(self.frames)]
        if self.timer == 1.5:
            collisions = pygame.sprite.spritecollideany(self, player_group,
                                                        collided=pygame.sprite.collide_circle_ratio(1.65))
            if collisions:
                self.timer -= 1 / FPS
        elif 0 < self.timer < 2.5:
            self.timer -= 1 / FPS
        else:
            self.detonate()
        self.collisions(.4375)

    def detonate(self):
        self.kill()


class EnemyHealthBar(pygame.sprite.Sprite):
    def __init__(self, cur_hp, max_hp):
        super().__init__(all_sprites)
        all_sprites.change_layer(self, 6)
        length = cur_hp * min(max_hp * 2, 800) / max_hp
        self.image = pygame.surface.Surface((min(max_hp * 2, 800), 15), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = FULL_SIZE[0] // 2 - self.rect.width // 2, 15
        pygame.draw.rect(self.image, (25, 25, 25), (0, 0, self.rect.width, 15))
        pygame.draw.rect(self.image, (155, 0, 15), (0, 0, length, 15))


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
        global enemy_health
        enemy_health = None
        self.kill()


class Mortar(Enemy):
    def __init__(self, pos, orientation='bottom'):
        super().__init__("mortar_" + orientation, 5, pos)
        Rail(pos)
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
        if isinstance(obj, StatBar) or isinstance(obj, EnemyHealthBar):
            return
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        if isinstance(obj, Player) or isinstance(obj, Projectile) or isinstance(obj, Enemy):
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


PLAYER = Player(15, 8)


def terminate():
    pygame.quit()
    sys.exit()


def death_screen():
    terminate()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    pre_screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        pre_screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def level():
    global PLAYER
    running = True
    levels = os.listdir('levels/')
    print(levels)
    cur_level = choice(levels)
    level_x, level_y = generate_level(load_level(cur_level))
    level_size = ((level_x + 1) * tile_width, (level_y + 1) * tile_height)
    view_size = (min((1920, level_size[0])), min((1080, level_size[1])))
    screen = pygame.display.set_mode(level_size)
    camera = Camera(level_size, view_size)
    # player = Player(FULL_SIZE[0] // 2, FULL_SIZE[1] // 2)
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_UP]:
                    PLAYER.jump()
                if pressed[pygame.K_DOWN]:
                    PLAYER.dismount()
                if pressed[pygame.K_RIGHT]:
                    PLAYER.go_right()
                if pressed[pygame.K_LEFT]:
                    PLAYER.go_left()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    PLAYER.stop()
                if event.key == pygame.K_LEFT:
                    PLAYER.stop()
            if event.type == pygame.MOUSEBUTTONUP:
                a = event.pos[0] - PLAYER.weapon.rect.centerx
                b = event.pos[1] - PLAYER.weapon.rect.centery
                PLAYER.weapon.attack((a / hypot(a, b), b / hypot(a, b)))
        point = pygame.math.Vector2(PLAYER.weapon.rect.centerx, PLAYER.weapon.rect.centery)
        mouse_pos = pygame.math.Vector2(*pygame.mouse.get_pos())
        radius, angle = (mouse_pos - point).as_polar()
        player_group.update()
        weapon_group.update(-angle)
        camera.update(PLAYER)
        projectile_group.update()
        rail_group.update()
        enemy_group.update()
        for sprite in all_sprites:
            camera.apply(sprite)
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


if __name__ == '__main__':
    # start_screen()
    level()
