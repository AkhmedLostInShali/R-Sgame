from data_funcs import load_xp

xp = load_xp()
lvl = 0
grade = pre_value = value = 500
while xp // value:
    lvl += 1
    grade = pre_value * 1.5 ** lvl
    value = pre_value + grade
buff_texts = {'temp_HP_boost': ('+15% to max HP', ['Is it bird?', 'is it helicopter?',
                                                   'Nope, just regular health bonus']),
              'temp_MP_boost': ('+20% to max MP', ['Li-magic-ion battery.',
                                                   'STOP. someone said magic?']),
              'temp_DMG_boost': ('+20% to your DMG', ["You're gettin' warmer.",
                                                      'Ecology hates you']),
              'sigil_MP_boost': ('+66% mana regeneration, wasting mana gives strength',
                                 ['Foreign knowledge that came from people called thaumathurgs.',
                                  'They use goods for magic and magic for goods.',
                                  'People says, that their power was as limitless as their ambitions.'
                                  'But where are all of them now?']),
              'sigil_XP_boost': ('Extra HP turns into XP, 25% of max MP at every level too',
                                 ['Sign of ordo was impersonation of balance and harmony.',
                                  'Was created by pure majesty and served to maintain the peace all over the world.',
                                  'But rapacity of Homo Sapiens was capable of destroying even such powerful artefact.',
                                  'No one had known where it is...', '',
                                  'What if all of this true? Would you take second chance for humanity?'])}
FPS = 60
FULL_SIZE = WIDTH, HEIGHT = 1920, 1080
tile_width = tile_height = 40
STATS = {'HP': 100 * (1 + 0.1 * lvl), 'MP': 50 * (1 + 0.2 * lvl), 'damage': 30 * (1 + 0.15 * lvl)}
ENEMY_STATS = {'HP': 100, 'damage': 30}
