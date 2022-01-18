import pygame
from data_funcs import load_image
from settings_n_variables import STATS, FULL_SIZE


class StatBar(pygame.sprite.Sprite):
    bar_image = load_image('stat_bar')
    back_image = load_image('stat_bar_back')

    def __init__(self, *group):
        super().__init__(*group)
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
        self.stats['HP'] += value
        self.update()


class EnemyHealthBar(pygame.sprite.Sprite):
    def __init__(self, cur_hp, max_hp, *group):
        super().__init__(*group)
        group[-1].change_layer(self, 6)
        length = cur_hp * min(max_hp * 2, 800) / max_hp
        self.image = pygame.surface.Surface((min(max_hp * 2, 800), 15), pygame.SRCALPHA, 32)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = FULL_SIZE[0] // 2 - self.rect.width // 2, 15
        pygame.draw.rect(self.image, (25, 25, 25), (0, 0, self.rect.width, 15))
        pygame.draw.rect(self.image, (155, 0, 15), (0, 0, length, 15))