import pygame

pygame.init()
enemy_health = None
all_sprites = pygame.sprite.LayeredUpdates()
floor_group = pygame.sprite.Group()
portal_group = pygame.sprite.Group()
# platform_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
weapon_group = pygame.sprite.Group()
rail_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
projectile_group = pygame.sprite.Group()