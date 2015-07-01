#! /usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
from sys import exit
from random import randrange

pygame.init()
pygame.font.init()
pygame.mixer.pre_init(44100, 32, 2, 4096)

font_name = pygame.font.get_default_font()
game_font = pygame.font.SysFont(font_name, 72)

screen = pygame.display.set_mode((956, 560), 0, 32)

background_filename = 'bg_big.png'
background = pygame.image.load(background_filename).convert()


ship = {
    'surface': pygame.image.load('ship.png').convert_alpha(),
    'position': [478, 500],
    'speed': {
        'x': 0,
        'y': 0
    }
}

exploded_ship = {
    'surface': pygame.image.load('ship_exploded.png').convert_alpha(),
    'position': [],
    'speed': {
        'x': 0,
        'y': 0
    },
    'rect': Rect(0, 0, 48, 48)
}

explosion_sound = pygame.mixer.Sound('boom.ogg')
pygame.display.set_caption('Asteroides')

clock = pygame.time.Clock()


def get_ticks_to_asteroid():
    return randrange(30, 90)

config = {
    'explosion_played': False,
    'collided': False,
    'collision_animation_counter': 0,
    'laser_cooldown': 0,
    'ticks_to_asteroid': get_ticks_to_asteroid()
}


def create_asteroid():
    return {
        'surface': pygame.image.load('asteroid.png').convert_alpha(),
        'position': [randrange(892), -64],
        'speed': randrange(8, 35)
    }


def create_laser():
    return {
        'surface': pygame.image.load('laser.png').convert_alpha(),
        'position': [ship.get('position')[0]+24, ship.get('position')[1]],
        'speed': {
            'x': ship.get('speed').get('x'),
            'y': ship.get('speed').get('y')-32}
    }


asteroids = []

lasers = []


def move_asteroids():
    for asteroid in asteroids:
        asteroid['position'][1] += asteroid['speed']


def move_lasers():
    for laser in lasers:
        laser['position'][0] += laser['speed']['x']
        laser['position'][1] += laser['speed']['y']


def remove_used_asteroids():
    for asteroid in asteroids:
        if asteroid['position'][1] > 560:
            asteroids.remove(asteroid)


def get_rect(obj):
    return Rect(obj['position'][0],
                obj['position'][1],
                obj['surface'].get_width(),
                obj['surface'].get_height())


def ship_collided():
    ship_rect = get_rect(ship)
    for asteroid in asteroids:
        if ship_rect.colliderect(get_rect(asteroid)):
            return True
    return False


def new_game(config):
    global asteroids
    global lasers

    ship['speed'] = {
        'x': 0,
        'y': 0
    }
    exploded_ship['speed'] = {
        'x': 0,
        'y': 0
    },
    exploded_ship['rect'] = Rect(0, 0, 48, 48)
    ship['position'] = [478, 500]
    config['explosion_played'] = False
    config['collided'] = False
    config['laser_cooldown'] = 0
    asteroids = []
    lasers = []
    config['collision_animation_counter'] = 0


def update_laser_cooldown():
    if not config['laser_cooldown']:
        config['laser_cooldown'] = 4
    else:
        config['laser_cooldown'] -= 1


def update_asteroids():
    if not config['ticks_to_asteroid']:
        config['ticks_to_asteroid'] = get_ticks_to_asteroid()
        asteroids.append(create_asteroid())
    else:
        config['ticks_to_asteroid'] -= 1


def check_exit():
    for event in pygame.event.get():
        if event.type == QUIT:
            exit()


def check_directions(pressed_keys):
    if pressed_keys[K_UP]:
        ship['speed']['y'] = -20
    elif pressed_keys[K_DOWN]:
        ship['speed']['y'] = 20

    if pressed_keys[K_LEFT]:
        ship['speed']['x'] = -20
    elif pressed_keys[K_RIGHT]:
        ship['speed']['x'] = 20


def check_laser(pressed_keys):
    if pressed_keys[K_SPACE]:
        if not config['laser_cooldown']:
            lasers.append(create_laser())


def check_restart(pressed_keys, pressed_mods):
    if config['collided'] and pressed_mods and KMOD_CTRL:
        if pressed_keys[K_r]:
            new_game(config)


def check_keyboard():
    pressed_keys = pygame.key.get_pressed()
    pressed_mods = pygame.key.get_mods()

    check_directions(pressed_keys)

    check_laser(pressed_keys)

    check_restart(pressed_keys, pressed_mods)


def draw():

    screen.blit(background, (0, 0))

    for asteroid in asteroids:
        screen.blit(asteroid['surface'], asteroid['position'])

    if not config['collided']:
        screen.blit(ship['surface'], ship['position'])

        for laser in lasers:
            screen.blit(laser['surface'], laser['position'])
    else:
        if not config['explosion_played']:
            screen.blit(ship['surface'], ship['position'])
        elif config["collision_animation_counter"] == 3:
            text = game_font.render('GAME OVER', 1, (255, 0, 0))
            screen.blit(text, (335, 250))
            text = game_font.render('CTRL+R TO RESTART', 1, (255, 0, 0))
            screen.blit(text, (220, 300))
        else:
            exploded_ship['rect'].x = config['collision_animation_counter'] * 48
            exploded_ship['position'] = ship['position']
            screen.blit(exploded_ship['surface'], exploded_ship['position'],
                        exploded_ship['rect'])
            config['collision_animation_counter'] += 1

    pygame.display.update()


def control_ship():
    if not config['collided']:
        config['collided'] = ship_collided()
        ship['position'][0] += ship['speed']['x']
        ship['position'][1] += ship['speed']['y']
    else:
        if not config['explosion_played']:
            config['explosion_played'] = True
            explosion_sound.play()
            ship['position'][0] += ship['speed']['x']
            ship['position'][1] += ship['speed']['y']

        elif config['collision_animation_counter'] < 3:
            exploded_ship['position'] = ship['position']


while True:

    update_asteroids()

    ship['speed'] = {
        'x': 0,
        'y': 0
    }

    check_exit()

    check_keyboard()

    pressed_mods = pygame.key.get_mods()

    move_asteroids()
    move_lasers()

    control_ship()

    draw()
    time_passed = clock.tick(30)

    remove_used_asteroids()
    update_laser_cooldown()
