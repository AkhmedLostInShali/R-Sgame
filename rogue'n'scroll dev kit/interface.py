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
        self.stats['HP'] = min(self.stats['HP'] + value, STATS['HP'])
        self.update()

    def change_mana(self, value):
        self.stats['MP'] = min(self.stats['MP'] + value, STATS['MP'])
        self.update()
        
    def is_alive(self):
        return self.stats['HP'] > 0


class EnemyHealthBar(pygame.sprite.Sprite):
    def __init__(self, cur_hp, max_hp, *group):
        super().__init__(*group)
        self.static = True
        group[-1].change_layer(self, 6)
        length = cur_hp * min(max_hp * 2, 800) / max_hp
        self.image = pygame.surface.Surface((min(max_hp * 2, 800), 15), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = FULL_SIZE[0] // 2 - self.rect.width // 2, 15
        pygame.draw.rect(self.image, (25, 25, 25), (0, 0, self.rect.width, 15))
        pygame.draw.rect(self.image, (155, 0, 15), (0, 0, length, 15))


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