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

explosion_sound = pygame.mixer.Sound('boom.wav')
pygame.display.set_caption('Asteroides')

clock = pygame.time.Clock()

config = {
    "explosion_played": False,
    "collided": False,
    "collision_animation_counter": 0
}

def create_asteroid():
    return {
        'surface': pygame.image.load('asteroid.png').convert_alpha(),
        'position': [randrange(892), -64],
        'speed': randrange(8, 35)
    }


def get_ticks_to_asteroid():
    return randrange(30, 90)

ticks_to_asteroid = get_ticks_to_asteroid()

asteroids = []


def move_asteroids():
    for asteroid in asteroids:
        asteroid['position'][1] += asteroid['speed']


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
    ship["speed"] = {
        'x': 0,
        'y': 0
    }
    exploded_ship["speed"] = {
        'x': 0,
        'y': 0
    },
    exploded_ship['rect'] = Rect(0, 0, 48, 48)
    config["explosion_played"] = False
    config["collided"] = False
    asteroids = []
    config["collision_animation_counter"] = 0


while True:

    if not ticks_to_asteroid:
        ticks_to_asteroid = get_ticks_to_asteroid()
        asteroids.append(create_asteroid())
    else:
        ticks_to_asteroid -= 1

    ship['speed'] = {
        'x': 0,
        'y': 0
    }

    for event in pygame.event.get():
        if event.type == QUIT:
            exit()

    pressed_keys = pygame.key.get_pressed()
    pressed_mods = pygame.key.get_mods()

    if pressed_keys[K_UP]:
        ship['speed']['y'] = -20
    elif pressed_keys[K_DOWN]:
        ship['speed']['y'] = 20

    if pressed_keys[K_LEFT]:
        ship['speed']['x'] = -20
    elif pressed_keys[K_RIGHT]:
        ship['speed']['x'] = 20

    screen.blit(background, (0, 0))

    move_asteroids()

    for asteroid in asteroids:
        screen.blit(asteroid['surface'], asteroid['position'])

    if not config["collided"]:
        config["collided"] = ship_collided()
        ship['position'][0] += ship['speed']['x']
        ship['position'][1] += ship['speed']['y']

        screen.blit(ship['surface'], ship['position'])
    else:
        if not config["explosion_played"]:
            config["explosion_played"] = True
            explosion_sound.play()
            ship['position'][0] += ship['speed']['x']
            ship['position'][1] += ship['speed']['y']

            screen.blit(ship['surface'], ship['position'])
        elif config["collision_animation_counter"] == 3:
            text = game_font.render('GAME OVER', 1, (255, 0, 0))
            screen.blit(text, (335, 250))
            if pressed_mods and KMOD_CTRL:
                if pressed_keys[K_r]:
                    new_game(config)
        else:
            exploded_ship['rect'].x = config["collision_animation_counter"] * 48
            exploded_ship['position'] = ship['position']
            screen.blit(exploded_ship['surface'], exploded_ship['position'],
                        exploded_ship['rect'])
            config["collision_animation_counter"] += 1

    pygame.display.update()
    time_passed = clock.tick(30)

    remove_used_asteroids()
