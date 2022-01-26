import pygame
from data_funcs import load_image
from settings_n_variables import STATS, FULL_SIZE


class StatBar(pygame.sprite.Sprite):
    bar_image = load_image('stat_bar')
    back_image = load_image('stat_bar_back')

    def __init__(self, *group):
        super().__init__(*group)
        self.static = True
        group[-1].change_layer(self, 6)
        self.image = self.back_image.copy()
        self.stats = STATS.copy()
        self.HP_buff, self.MP_buff = 1, 1
        self.rect = self.image.get_rect()
        self.update()

    def update(self):
        self.image = self.back_image.copy()
        pygame.draw.rect(self.image, (155, 0, 15), (2, 3, self.stats['HP'] * 200 / (STATS['HP'] * self.HP_buff), 28))
        pygame.draw.rect(self.image, (15, 0, 155), (2, 38, self.stats['MP'] * 160 / (STATS['MP'] * self.MP_buff), 21))
        self.image.blit(self.bar_image, (0, 0))
        font = pygame.font.Font(None, 38)
        health_text = font.render(f'{round(self.stats["HP"])}', True,
                                  pygame.Color((215, 230, 255)))
        self.image.blit(health_text, (4, 6))
        font = pygame.font.Font(None, 28)
        mana_text = font.render(f'{round(self.stats["MP"])}', True,
                                pygame.Color((255, 190, 215)))
        self.image.blit(mana_text, (4, 39))

    def get_value(self, key='MP', cur=False):
        if cur:
            return self.stats[key]
        else:
            return STATS[key] * (self.MP_buff if key == 'MP' else self.HP_buff)

    def change_health(self, value, xp_sigil=False):
        xp = 0
        if xp_sigil and self.stats['HP'] + value > STATS['HP'] * self.HP_buff:
            xp = self.stats['HP'] + value - STATS['HP'] * self.HP_buff
        self.stats['HP'] = min(self.stats['HP'] + value, STATS['HP'] * self.HP_buff)
        self.update()
        return xp

    def change_mana(self, value):
        if self.stats['MP'] + value <= 0:
            return False
        self.stats['MP'] = min(self.stats['MP'] + value, STATS['MP'] * self.MP_buff)
        self.update()
        return True
        
    def is_alive(self):
        return self.stats['HP'] > 0

    def increase_max(self, mana=0, health=0):
        self.MP_buff += mana
        self.HP_buff += health


class EnemyHealthBar(pygame.sprite.Sprite):
    def __init__(self, name, cur_hp, max_hp, *group):
        super().__init__(*group)
        self.static = True
        group[-1].change_layer(self, 6)
        length = cur_hp * 400 / max_hp
        self.image = pygame.surface.Surface((400, 15), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = FULL_SIZE[0] // 2 - self.rect.width // 2, 15
        pygame.draw.rect(self.image, (25, 25, 25), (0, 0, self.rect.width, 15))
        pygame.draw.rect(self.image, (155, 0, 15), (0, 0, length, 15))
        font = pygame.font.Font(None, 24)
        name_text = font.render(f'{name} {round(cur_hp)} / {round(max_hp)}', True,
                                pygame.Color((237, 178, 72)))
        self.image.blit(name_text, (self.rect.width // 2 - (name_text.get_width() // 2), 0))


class Button(pygame.sprite.Sprite):
    def __init__(self, pos, name, *group):
        super().__init__(*group)
        self.static = True
        self.name = name
        self.image = load_image('tips/' + name)
        self.rect = self.image.get_rect()
        self.rect.x = FULL_SIZE[0] // 2 - (0.8 + (pos - 1)) * self.rect.width
        self.rect.y = FULL_SIZE[1] // 2 - 0.5 * self.rect.width

    def __str__(self):
        return self.name

    def clicked(self, position):
        return self.rect.collidepoint(position)
